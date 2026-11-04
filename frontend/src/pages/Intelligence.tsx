import { useState } from "react";
import { ChevronDown, Radar } from "lucide-react";

interface Threat {
  key: string;
  title: string;
  summary: string;
  lines: string[];
  playbook: string[];
}

const THREATS: Threat[] = [
  {
    key: "bank_kyc",
    title: "Bank / KYC fraud",
    summary:
      "A message claims your account or card will be blocked unless you re-do KYC, and pushes you to a link or an app.",
    lines: [
      "Dear Customer, your account will be blocked today. Complete KYC immediately.",
      "Your PAN is not linked. Update KYC within 24 hours or services will stop.",
    ],
    playbook: [
      "KYC is never completed through an SMS link.",
      "Open the bank's own app or visit a branch.",
      "Report the sender to your bank and on Chakshu (1909).",
    ],
  },
  {
    key: "upi_payment",
    title: "UPI / payment fraud",
    summary:
      "You are asked to approve a collect request, scan a QR or enter a PIN in order to *receive* money.",
    lines: [
      "You have a collect request of Rs 4,999. Approve and enter PIN to receive.",
      "Scan this QR to get your refund of Rs 1,200.",
    ],
    playbook: [
      "Receiving money never needs a PIN or a QR scan.",
      "Reject unknown collect requests inside the UPI app.",
      "Report unauthorised debits to your bank within 3 days.",
    ],
  },
  {
    key: "phishing",
    title: "Phishing links",
    summary:
      "A link opens a page that copies a bank, wallet or government portal and harvests your credentials.",
    lines: [
      "Verify your account at sbi-kyc-verify.top/update",
      "Your session expired. Login again here: bit.ly/xxxx",
    ],
    playbook: [
      "Read the domain from the end, right to left.",
      "Type the official address yourself; never click through.",
      "A padlock does not mean the site is genuine.",
    ],
  },
  {
    key: "fake_job",
    title: "Fake job offers",
    summary:
      "Easy work, high daily pay, and a small registration or training fee before you start.",
    lines: [
      "Work from home, earn Rs 5,000 daily. Pay Rs 499 registration fee.",
      "Part-time typing job. Pay refundable security deposit of Rs 1,000.",
    ],
    playbook: [
      "No genuine employer charges you to be hired.",
      "Verify the company's CIN/GST and official careers page.",
      "Never share Aadhaar or bank details before an offer letter.",
    ],
  },
  {
    key: "lottery_reward",
    title: "Lottery and reward scams",
    summary:
      "A prize you never entered for, released only after a processing fee, tax or courier charge.",
    lines: [
      "Congratulations! You won Rs 25,00,000 in the KBC lucky draw.",
      "Your number won a scratch card. Pay GST to release the amount.",
    ],
    playbook: [
      "You cannot win a draw you never entered.",
      "Prizes never require an advance payment.",
      "Never share bank details to 'receive' a prize.",
    ],
  },
  {
    key: "govt_impersonation",
    title: "Government impersonation",
    summary:
      "Messages in the name of a scheme, subsidy, electricity board or police, asking for a fee or documents.",
    lines: [
      "PM Kisan installment on hold. Update Aadhaar to release it.",
      "Your electricity connection will be disconnected tonight. Pay now.",
    ],
    playbook: [
      "Check the scheme only on the official .gov.in portal.",
      "Utility disconnection notices come on the bill, not by SMS link.",
      "Government offices never demand payment over WhatsApp.",
    ],
  },
  {
    key: "otp_account_takeover",
    title: "OTP and account takeover",
    summary:
      "Someone triggers an OTP on your number, then calls to 'help' you, or asks you to install a screen-sharing app.",
    lines: [
      "Share the OTP you just received to complete verification.",
      "Install AnyDesk and share the code so we can fix your account.",
    ],
    playbook: [
      "Never share an OTP with anyone, for any reason.",
      "An OTP you did not request means someone has your details.",
      "Never install remote access apps for a caller.",
    ],
  },
  {
    key: "investment",
    title: "Investment scams",
    summary:
      "Guaranteed daily returns, VIP trading groups and 'sure shot' signals that grow until withdrawal is blocked.",
    lines: [
      "Guaranteed 30% daily profit. Join our VIP trading group.",
      "Double your money in 15 days. Limited seats in the batch.",
    ],
    playbook: [
      "Guaranteed high returns do not exist.",
      "Check SEBI registration of any intermediary.",
      "Never pay a 'withdrawal tax' to release profits.",
    ],
  },
  {
    key: "delivery_parcel",
    title: "Delivery and parcel scams",
    summary:
      "A stuck parcel, a customs duty or a redelivery fee that leads to a card-harvesting page.",
    lines: [
      "Your parcel is held at customs. Pay Rs 199 clearance charge.",
      "Delivery failed. Update your address and pay the redelivery fee.",
    ],
    playbook: [
      "Track only on the courier's official site with your own order id.",
      "Couriers do not collect fees through random links.",
      "Never re-enter card details from an SMS link.",
    ],
  },
  {
    key: "fake_customer_support",
    title: "Fake customer support",
    summary:
      "A search result or social post lists a helpline that is actually a call centre running the fraud.",
    lines: [
      "For refund, call our customer care 9xxxx xxxxx.",
      "Contact our support on WhatsApp to unlock your account.",
    ],
    playbook: [
      "Get helpline numbers only from the official app or website.",
      "Never allow remote access to your phone.",
      "A real agent never asks for your PIN or OTP.",
    ],
  },
  {
    key: "malicious_url",
    title: "Malicious or suspicious links",
    summary:
      "Lookalike domains, throwaway TLDs, shortened links and IP addresses used to deliver phishing or malware.",
    lines: [
      "http://hdfcbank-kyc.com/verify",
      "https://sbi.co.in.secure-login.xyz/kyc",
    ],
    playbook: [
      "Check the registered domain, not the subdomain.",
      "Treat shorteners and raw IP links as hostile until proven otherwise.",
      "Do not open a link to 'see what it is'.",
    ],
  },
  {
    key: "unknown",
    title: "Unclassified and uncertain cases",
    summary:
      "Some messages carry no clear pattern. They are reported as unverified rather than safe, because absence of evidence is not proof.",
    lines: ["Hi, this is regarding your recent complaint. Please call back."],
    playbook: [
      "Verify the sender through a channel you already trust.",
      "Never act on money or credentials from an unverified sender.",
      "Run the scan again if more context arrives.",
    ],
  },
];

export default function Intelligence() {
  const [open, setOpen] = useState<string | null>(THREATS[0].key);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          <Radar size={22} className="text-accent" aria-hidden="true" /> Scam intelligence
        </h1>
        <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
          How each major Indian scam works, the lines they use, and the exact counter-move. This is
          pattern knowledge from public reporting and Indian cybercrime guidance — not live statistics.
        </p>
      </header>

      <div className="space-y-3">
        {THREATS.map((threat) => {
          const isOpen = open === threat.key;
          return (
            <article key={threat.key} className="glass overflow-hidden">
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : threat.key)}
                aria-expanded={isOpen}
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition hover:bg-white/[0.03]"
              >
                <span>
                  <span className="block text-sm font-semibold text-white">{threat.title}</span>
                  <span className="mt-1 block text-xs leading-relaxed text-slate-400">{threat.summary}</span>
                </span>
                <ChevronDown
                  size={18}
                  className={`shrink-0 text-slate-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
                  aria-hidden="true"
                />
              </button>
              {isOpen && (
                <div className="grid gap-4 border-t border-white/[0.06] px-5 py-4 sm:grid-cols-2">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                      Lines they use
                    </h3>
                    <ul className="mt-2 space-y-2">
                      {threat.lines.map((line) => (
                        <li
                          key={line}
                          className="rounded-lg border border-white/5 bg-ink-950/60 p-2.5 font-mono text-[11px] leading-relaxed text-slate-400"
                        >
                          {line}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                      Counter-move
                    </h3>
                    <ul className="mt-2 space-y-2 text-sm leading-relaxed text-slate-300">
                      {threat.playbook.map((item) => (
                        <li key={item} className="flex gap-2">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" aria-hidden="true" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
