"""Lexical URL analysis.

The submitted URL is **never fetched, resolved or rendered**.  Everything below
works on the string alone, which removes SSRF and drive-by risk entirely.  If a
reputation provider is configured, only the normalised URL with its query string
and fragment removed is sent to it.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from app.core.errors import AppError

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "cutt.ly",
    "rb.gy", "shorturl.at", "tiny.cc", "rebrand.ly", "bit.do", "shorte.st", "adf.ly",
    "clck.ru", "shrinkme.io", "t.ly", "shorturl.gg", "urlz.fr", "s.id", "tr.ee",
    "wa.me", "t.me", "chat.whatsapp.com", "linktr.ee", "tiny.one", "bl.ink",
}

SUSPICIOUS_TLDS = {
    "top", "xyz", "click", "zip", "mov", "tk", "ml", "ga", "cf", "gq", "work", "loan",
    "cam", "rest", "buzz", "monster", "sbs", "cyou", "icu", "best", "quest", "bar",
    "review", "country", "stream", "download", "kim", "party", "science", "gdn",
    "wang", "support", "live", "online", "site", "shop", "store", "info", "biz",
}

SECOND_LEVEL_SUFFIXES = {
    "co.in", "gov.in", "ac.in", "nic.in", "org.in", "net.in", "edu.in", "res.in",
    "firm.in", "gen.in", "ind.in", "co.uk", "com.au", "co.jp",
}

BRANDS: dict[str, tuple[str, ...]] = {
    "sbi": ("sbi.co.in", "onlinesbi.sbi", "sbiyono.sbi", "onlinesbi.com", "sbi.card"),
    "hdfc": ("hdfcbank.com", "hdfc.com", "hdfclife.com", "hdfcsec.com"),
    "icici": ("icicibank.com", "icicibank.co.in", "icicidirect.com"),
    "axis": ("axisbank.com", "axismf.com"),
    "kotak": ("kotak.com", "kotakbank.com", "kotaksecurities.com"),
    "pnb": ("pnbindia.in", "netpnb.com"),
    "rbi": ("rbi.org.in", "rbiretaildirect.org.in"),
    "uidai": ("uidai.gov.in", "myaadhaar.uidai.gov.in"),
    "incometax": ("incometax.gov.in", "incometaxindia.gov.in", "tin.nsdl.com"),
    "epfo": ("epfindia.gov.in", "unifiedportal-mem.epfindia.gov.in"),
    "irctc": ("irctc.co.in", "irctc.com"),
    "indiapost": ("indiapost.gov.in", "indiapost.co.in"),
    "paytm": ("paytm.com", "paytmbank.com", "paytmmall.com"),
    "phonepe": ("phonepe.com"),
    "amazon": ("amazon.in", "amazon.com", "amazonpay.in"),
    "flipkart": ("flipkart.com"),
    "netflix": ("netflix.com"),
    "google": ("google.com", "google.co.in", "gpay.app"),
    "cybercrime": ("cybercrime.gov.in"),
    "trai": ("trai.gov.in"),
    "nsdl": ("nsdl.co.in", "nsdl.com"),
    "lic": ("licindia.in", "licindia.com"),
    "bluedart": ("bluedart.com"),
    "delhivery": ("delhivery.com"),
    "swiggy": ("swiggy.com"),
    "zomato": ("zomato.com"),
}

BAIT_KEYWORDS = (
    "kyc", "verify", "verification", "secure", "security", "login", "signin", "update",
    "refund", "claim", "prize", "reward", "winner", "lottery", "otp", "unlock", "reactivate",
    "suspend", "blocked", "pan-card", "aadhaar", "netbanking", "wallet-recover",
)

_LEET = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "$": "s"})
_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


@dataclass(frozen=True)
class UrlFinding:
    id: str
    label: str
    weight: int
    evidence: str = ""
    explanation: str = ""

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "weight": self.weight,
            "evidence": self.evidence,
            "explanation": self.explanation,
        }


@dataclass
class UrlReport:
    submitted: str
    normalized: str
    host: str
    scheme: str
    https: bool
    is_ip_literal: bool
    is_shortener: bool
    is_punycode: bool
    lookalike_of: str | None
    risk_score: int
    risk_level: str
    findings: list[UrlFinding] = field(default_factory=list)
    mitigators: list[UrlFinding] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "submitted": self.submitted,
            "normalized": self.normalized,
            "host": self.host,
            "scheme": self.scheme,
            "https": self.https,
            "is_ip_literal": self.is_ip_literal,
            "is_shortener": self.is_shortener,
            "is_punycode": self.is_punycode,
            "lookalike_of": self.lookalike_of,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "findings": [f.as_dict() for f in self.findings],
        }


def _registrable(host: str) -> str:
    labels = host.split(".")
    if len(labels) <= 2:
        return host
    last_two = ".".join(labels[-2:])
    if last_two in SECOND_LEVEL_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return last_two


def _edit_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if abs(len(a) - len(b)) > 2:
        return 3
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb))
            )
        previous = current
    return previous[-1]


def _official_hosts() -> set[str]:
    hosts: set[str] = set()
    for domains in BRANDS.values():
        hosts.update(domains)
    return hosts


OFFICIAL_HOSTS = _official_hosts()


def _is_official(host: str) -> bool:
    for official in OFFICIAL_HOSTS:
        if host == official or host.endswith("." + official):
            return True
    return False


def _brand_match(host: str) -> str | None:
    """Return the brand token that this host imitates, if any."""
    registrable = _registrable(host)
    labels = registrable.split(".")
    stem = labels[0].translate(_LEET)
    stem_compact = stem.replace("-", "")

    for brand in BRANDS:
        if len(brand) < 3:
            continue
        if brand == stem_compact:
            return brand if not _is_official(host) else None
        if brand in stem_compact and brand != stem_compact:
            # e.g. 'sbi-kyc-verify', 'hdfcbanklogin'
            return brand if not _is_official(host) else None
        if _edit_distance(stem_compact, brand) == 1 and len(brand) >= 4:
            return brand if not _is_official(host) else None
    return None


def _brand_in_subdomain(host: str) -> str | None:
    registrable = _registrable(host)
    if _is_official(host):
        return None
    sub_labels = host[: -(len(registrable) + 1)].split(".") if host.endswith(registrable) and host != registrable else []
    for label in sub_labels:
        compact = label.translate(_LEET).replace("-", "")
        for brand in BRANDS:
            if len(brand) >= 3 and (compact == brand or compact.startswith(brand)):
                return brand
    return None


_SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.IGNORECASE)


def normalize_url(raw: str) -> tuple[str, str, str, bool, bool]:
    """Return (normalized_url, scheme, host, https, had_userinfo) or raise AppError."""
    candidate = raw.strip()
    if not candidate:
        raise AppError("The URL is empty.", code="invalid_url")
    if len(candidate) > 2048:
        raise AppError("The URL is too long to analyse.", code="invalid_url")
    if re.search(r"\s", candidate):
        raise AppError("The URL contains whitespace, which is not valid.", code="invalid_url")
    scheme_match = _SCHEME_RE.match(candidate)
    if scheme_match and not candidate.lower().startswith(("http://", "https://")):
        raise AppError(
            "Only http and https URLs can be analysed. Other schemes are blocked for safety.",
            code="invalid_scheme",
        )
    if "://" not in candidate:
        candidate = "http://" + candidate

    try:
        parts = urlsplit(candidate)
    except ValueError as exc:  # pragma: no cover - defensive
        raise AppError("The URL could not be parsed.", code="invalid_url") from exc

    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        raise AppError(
            "Only http and https URLs can be analysed. Other schemes are blocked for safety.",
            code="invalid_scheme",
        )
    host = (parts.hostname or "").lower().strip(".")
    if not host:
        raise AppError("The URL does not contain a host name.", code="invalid_url")
    if len(host) > 253:
        raise AppError("The URL host is too long to analyse.", code="invalid_url")

    try:
        host.encode("idna")
    except UnicodeError as exc:
        raise AppError("The URL host contains invalid characters.", code="invalid_url") from exc

    if "." not in host and not host.replace(".", "").isdigit():
        raise AppError("The URL host does not look like a valid domain.", code="invalid_url")

    if not host.startswith("xn--"):
        for label in host.split("."):
            if not _HOST_LABEL.match(label):
                raise AppError("The URL host contains invalid characters.", code="invalid_url")

    had_userinfo = bool(parts.username or parts.password)
    # Drop query and fragment: they often carry personal data and are not needed.
    normalized = urlunsplit((scheme, host, parts.path or "/", "", ""))
    return normalized, scheme, host, scheme == "https", had_userinfo


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _aggregate(findings: list[UrlFinding], mitigators: list[UrlFinding]) -> int:
    weights = sorted((f.weight for f in findings), reverse=True)
    decay = (1.0, 0.85, 0.72, 0.6, 0.5)
    total = 0.0
    for index, weight in enumerate(weights):
        total += weight * (decay[index] if index < len(decay) else 0.4)
    total -= sum(m.weight for m in mitigators)
    return int(round(max(0.0, min(100.0, total))))


def level_for(score: int) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def analyze_url(raw: str) -> UrlReport:
    """Analyse a URL string. Never performs network access to the target."""
    normalized, scheme, host, https, had_userinfo = normalize_url(raw)
    findings: list[UrlFinding] = []
    mitigators: list[UrlFinding] = []

    parts = urlsplit(normalized)
    path = parts.path or ""
    registrable = _registrable(host)

    if _is_official(host):
        mitigators.append(
            UrlFinding(
                id="known_official_domain",
                label="Host belongs to a known official domain",
                weight=18,
                evidence=host,
                explanation="This host is on the built-in list of official bank, government or service domains.",
            )
        )

    if not https:
        findings.append(
            UrlFinding(
                id="no_https",
                label="Link is not using HTTPS",
                weight=8,
                evidence=f"{scheme}://{host}",
                explanation="Traffic to this link is unencrypted. Note that HTTPS on its own does not make a site safe.",
            )
        )

    if _is_ip(host):
        findings.append(
            UrlFinding(
                id="ip_literal_host",
                label="Uses a raw IP address instead of a domain",
                weight=18,
                evidence=host,
                explanation="Legitimate banks and government portals publish a domain name, not a bare IP address.",
            )
        )

    if _is_ip(host):
        try:
            address = ipaddress.ip_address(host)
            if address.is_private or address.is_loopback or address.is_reserved or address.is_link_local:
                findings.append(
                    UrlFinding(
                        id="internal_address",
                        label="Points at a private or internal network address",
                        weight=20,
                        evidence=host,
                        explanation="Internal addresses are used to probe servers and devices. The scanner never connects to them.",
                    )
                )
        except ValueError:  # pragma: no cover
            pass

    if had_userinfo:
        findings.append(
            UrlFinding(
                id="userinfo_trick",
                label="Hides the real host behind an '@' character",
                weight=24,
                evidence=raw.strip()[:100],
                explanation="Everything before '@' is ignored by browsers, so the visible name is not the host you reach.",
            )
        )

    if host in SHORTENERS or registrable in SHORTENERS:
        findings.append(
            UrlFinding(
                id="shortener",
                label="Shortened link hides the destination",
                weight=26,
                evidence=host,
                explanation="The real destination is only revealed after the redirect. Do not open it to find out.",
            )
        )

    if host.startswith("xn--") or ".xn--" in host:
        findings.append(
            UrlFinding(
                id="punycode_host",
                label="Uses encoded international characters (punycode)",
                weight=18,
                evidence=host,
                explanation="Punycode is used to display lookalike characters that appear identical to a trusted name.",
            )
        )

    tld = host.rsplit(".", 1)[-1]
    if tld in SUSPICIOUS_TLDS:
        findings.append(
            UrlFinding(
                id="suspicious_tld",
                label=f"Uses a TLD commonly seen in abuse (.{tld})",
                weight=14,
                evidence=host,
                explanation="These cheap, lightly policed domains are over represented in phishing campaigns.",
            )
        )

    brand = _brand_match(host)
    if brand:
        findings.append(
            UrlFinding(
                id="lookalike_domain",
                label=f"Imitates the '{brand.upper()}' brand without owning its domain",
                weight=26,
                evidence=host,
                explanation="The name is engineered to look like a trusted brand while the registered domain belongs to someone else.",
            )
        )

    sub_brand = _brand_in_subdomain(host)
    if sub_brand and not brand:
        findings.append(
            UrlFinding(
                id="brand_in_subdomain",
                label=f"Puts the '{sub_brand.upper()}' name in a subdomain of an unrelated domain",
                weight=24,
                evidence=host,
                explanation="The trusted name appears only as a subdomain; the registered domain (the part that matters) is not the brand's.",
            )
        )

    hyphen_count = host.count("-")
    if hyphen_count >= 3:
        findings.append(
            UrlFinding(
                id="many_hyphens",
                label="Host name is padded with hyphens",
                weight=8,
                evidence=host,
                explanation="Chained keywords separated by hyphens are typical of throwaway phishing domains.",
            )
        )

    digit_count = sum(ch.isdigit() for ch in host)
    if digit_count >= 4:
        findings.append(
            UrlFinding(
                id="digits_in_host",
                label="Host contains an unusual number of digits",
                weight=6,
                evidence=host,
                explanation="Digit-heavy domains are cheap bulk registrations used for short lived campaigns.",
            )
        )

    if len(host) > 30:
        findings.append(
            UrlFinding(
                id="long_host",
                label="Host name is unusually long",
                weight=6,
                evidence=host,
                explanation="Long hosts are used to bury the real domain at the end of the visible text.",
            )
        )

    subdomain_count = len(host.split(".")) - len(registrable.split("."))
    if subdomain_count >= 3:
        findings.append(
            UrlFinding(
                id="many_subdomains",
                label="Uses many subdomain levels",
                weight=8,
                evidence=host,
                explanation="Deep subdomains push the registered domain out of sight on a small phone screen.",
            )
        )

    bait = [keyword for keyword in BAIT_KEYWORDS if keyword in host]
    if bait:
        findings.append(
            UrlFinding(
                id="bait_keywords",
                label="Host name contains bait words: " + ", ".join(bait[:4]),
                weight=12,
                evidence=host,
                explanation="Words like 'kyc', 'verify' or 'refund' are placed in the domain to look official.",
            )
        )

    path_bait = [keyword for keyword in BAIT_KEYWORDS if keyword in path.lower()]
    if path_bait:
        findings.append(
            UrlFinding(
                id="suspicious_path",
                label="Path targets a credential form: " + ", ".join(path_bait[:4]),
                weight=10,
                evidence=path[:100],
                explanation="Paths such as /kyc-update or /login lead to fake forms that harvest your details.",
            )
        )

    if "%" in path or "%" in host:
        findings.append(
            UrlFinding(
                id="encoded_characters",
                label="Contains percent-encoded characters",
                weight=10,
                evidence=(host + path)[:100],
                explanation="Encoding is used to hide characters from filters and from your eyes.",
            )
        )

    if parts.port and parts.port not in (80, 443):
        findings.append(
            UrlFinding(
                id="nonstandard_port",
                label=f"Uses a non-standard port ({parts.port})",
                weight=8,
                evidence=parts.netloc[:80],
                explanation="Public banking and government services do not run on unusual ports.",
            )
        )

    if re.search(r"\.(?:php|asp|aspx|html?)$", path, re.IGNORECASE) and "?" in normalized:  # pragma: no cover
        findings.append(
            UrlFinding(
                id="script_path",
                label="Links to a script page",
                weight=4,
                evidence=path[:100],
                explanation="Script endpoints are often used by phishing kits.",
            )
        )

    score = _aggregate(findings, mitigators)
    return UrlReport(
        submitted=raw.strip(),
        normalized=normalized,
        host=host,
        scheme=scheme,
        https=https,
        is_ip_literal=_is_ip(host),
        is_shortener=host in SHORTENERS or registrable in SHORTENERS,
        is_punycode=host.startswith("xn--") or ".xn--" in host,
        lookalike_of=brand or sub_brand,
        risk_score=score,
        risk_level=level_for(score),
        findings=findings,
        mitigators=mitigators,
    )
