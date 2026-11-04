# Privacy policy

**Summary: ScamSathi has no accounts, no trackers and no analytics. It stores a redacted preview of the
scans you choose to keep, tied to a random id in your browser, and you can delete any record at any time.**

## 1. What we do not collect

- No name, email address, phone number or password. There is no sign-up.
- No cookies, no third-party analytics, no advertising SDKs, no fingerprinting.
- No raw message content, OTPs, PINs, card numbers, account numbers, Aadhaar or PAN numbers.
- No browsing history, no location, no device identifiers beyond what your HTTP request carries.

## 2. What is processed

| Data | Purpose | Retention |
| --- | --- | --- |
| Message text or URL you submit | Analyse it and produce a result | In memory for the duration of the request only |
| Redacted excerpt (≤280 chars) | Show a preview in history | Until you delete it |
| SHA-256 hash of the content | Deduplication / integrity | Until you delete it |
| Risk score, level, category, confidence, indicators, explanation | Reopen a past result | Until you delete it |
| Anonymous client id | Link scans to your browser profile | In your browser's `localStorage` |
| Request metadata (route, status, duration, request id) | Operate and debug the service | Server log retention of the host |

Redaction masks: card-like digit runs, OTP values, Aadhaar numbers, PAN numbers, email addresses, Indian
phone numbers, IFSC/account patterns and any remaining digit run of six or more characters.

## 3. How history works

1. The app generates a random id (`web` + 32 hex characters) and stores it in `localStorage`.
2. Every request sends it as `X-Client-Id`.
3. The server stores scans under that id and returns only scans matching it — enforced in the SQL
   `WHERE` clause, not in application code.
4. Clearing site data, using the "Forget my local id" button, or unchecking "save to history" breaks the
   link immediately.

If you send no client id, **nothing is stored at all** — that is the privacy mode.

## 4. URLs

Submitted links are parsed as text. They are never opened, resolved, screenshotted or followed. The query
string and fragment are stripped before storage, because those often carry tokens or personal data.

## 5. Third parties

By default, **none**. Two integrations exist and are off unless the operator configures keys:

- **AI provider (optional).** Receives redacted message text, the deterministic score and category, to
  return a bounded score adjustment and one rationale sentence.
- **Google Safe Browsing (optional).** Receives the normalised URL without query string or fragment.

Neither receives your client id, IP address, or any data from a scan you did not submit. If no key is
configured, the API reports the provider as `none` and the result states that no external check was made.

## 6. Your controls

| Control | Effect |
| --- | --- |
| Uncheck "save to history" | The scan is analysed and returned but not stored |
| Delete a record | Removes it from the database permanently |
| "Forget my local id" | New id, no access to previous history, cached results cleared |
| Clear site data in the browser | Same as above |

## 7. Children

The tool is intended for general audiences and is not directed at children under 13. It collects no
personal data that would identify a child.

## 8. Changes

Material changes to this policy will be recorded in the repository history, which is public.

## 9. Contact

Open an issue on the repository. For fraud you have experienced, report to
[cybercrime.gov.in](https://cybercrime.gov.in/) or call **1930** — ScamSathi cannot investigate cases.
