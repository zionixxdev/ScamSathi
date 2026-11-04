import { BookOpen, ExternalLink, PhoneCall, ShieldCheck } from "lucide-react";

const SECTIONS = [
  {
    id: "common-scams",
    title: "Common Indian online scams",
    body: "Most fraud in India arrives as a short message or a phone call that borrows the name of a bank, a scheme, a courier or a government office. The pattern is remarkably consistent: a trusted name, a reason to act today, a link or a number, and then a request for a payment or a secret. KYC expiry, electricity disconnection, parcel held at customs, PM Kisan instalment, fake job registration fees, fake customer care numbers and 'digital arrest' calls cover the majority of reported cases.",
    points: [
      "The name is always borrowed, never earned — verify through official channels only.",
      "A deadline in the message exists to stop you checking with anyone else.",
      "A small 'fee' is the hook; the real loss comes after you share credentials.",
    ],
  },
  {
    id: "phishing",
    title: "How phishing works",
    body: "A phishing page copies a login screen you already recognise. The domain is the tell: a real bank uses its own registered domain, while the fake uses a lookalike, a hyphenated keyword string, a throwaway TLD or a subdomain that merely contains the brand name. Modern kits also copy the HTTPS padlock, because certificates are free. Reading the domain from the right is the single most useful habit you can build.",
    points: [
      "sbi.co.in is the bank. sbi-kyc-verify.top and sbi.co.in.secure-login.xyz are not.",
      "Never enter credentials on a page you reached from an SMS or WhatsApp link.",
      "Bookmark your bank and use the bookmark, not a search result.",
    ],
  },
  {
    id: "upi",
    title: "UPI safety",
    body: "The core rule of UPI is directional: money leaves your account when you enter your PIN or approve a collect request. Money arrives without any action from you. Fraudsters exploit this by framing a debit as a credit — 'approve this request to receive your refund'. A QR code shown to you for 'receiving' a payment is always a payment request in disguise.",
    points: [
      "PIN, QR scan or approval is only ever needed to send money.",
      "Reject collect requests you did not initiate.",
      "Check the payee name in the app before confirming, every time.",
    ],
  },
  {
    id: "otp",
    title: "OTP protection",
    body: "An OTP is the last lock on your account, so it is the thing fraudsters want most. They will claim to be a bank executive, a delivery agent, a police officer or a 'digital arrest' officer. None of them need it. If an OTP arrives that you did not trigger, someone already has your number and is trying to log in — that is an emergency, not a coincidence.",
    points: [
      "No legitimate caller ever needs your OTP, PIN, CVV or password.",
      "Never install AnyDesk, TeamViewer or a screen-sharing app for a caller.",
      "If you shared an OTP, call your bank immediately and ask them to freeze the account.",
    ],
  },
  {
    id: "fake-jobs",
    title: "Fake job detection",
    body: "A real hiring process costs you time, not money. Fake offers invert this: a large daily income, no interview, and a registration, training or security deposit fee. Work-from-home 'task' jobs on Telegram that ask you to pay to unlock higher payouts are the same fraud in a newer wrapper. Verify the company's corporate identity number, GST details and official careers page before sharing any document.",
    points: [
      "Any employer asking for money before hiring is a scam.",
      "Verify the company on the MCA portal and its own website.",
      "Never share Aadhaar, PAN or bank details before a written offer.",
    ],
  },
  {
    id: "safe-browsing",
    title: "Safe browsing",
    body: "Most malicious links only work if you click and then act. Slowing down at that moment defeats a large share of attacks: read the domain, refuse to type credentials on a page reached from a message, and keep the browser and phone updated. On Android, never install an APK sent over WhatsApp — Play Protect cannot check what it has never seen.",
    points: [
      "Read the domain right to left; the part before the last dot matters most.",
      "Never install an APK file received in a chat.",
      "Keep your banking apps updated and enable transaction alerts.",
    ],
  },
  {
    id: "report",
    title: "How to report cybercrime in India",
    body: "Speed decides recovery. Report a financial fraud within the golden hour — the sooner a complaint is filed, the better the chance the transaction can be frozen. Use the National Cyber Crime Reporting Portal for all cyber fraud, dial 1930 for financial fraud, and use Chakshu (1909) to report a fraudulent call or message to the Department of Telecommunications. CERT-In handles incident reporting for organisations and technical vulnerabilities.",
    points: [
      "cybercrime.gov.in — file a complaint and track it.",
      "1930 — national cyber financial fraud helpline.",
      "1909 (Chakshu) — report suspected fraud calls and messages.",
    ],
  },
];

const RESOURCES = [
  {
    title: "National Cyber Crime Reporting Portal",
    href: "https://cybercrime.gov.in/",
    note: "Official Government of India portal for reporting cybercrime, including financial fraud.",
  },
  {
    title: "CERT-In",
    href: "https://www.cert-in.org.in/",
    note: "Indian Computer Emergency Response Team — advisories and incident reporting.",
  },
  {
    title: "Sanchar Saathi (Chakshu)",
    href: "https://sancharsaathi.gov.in/",
    note: "Department of Telecommunications portal to report fraud calls and messages, and to check connections in your name.",
  },
];

export default function Guide() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          <BookOpen size={22} className="text-accent-mint" aria-hidden="true" /> Safety guide
        </h1>
        <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
          Practical, India-specific guidance. Five minutes here is worth more than any detector, because
          you are the last line of defence.
        </p>
      </header>

      <nav className="glass flex flex-wrap gap-2 p-3" aria-label="Guide sections">
        {SECTIONS.map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className="chip transition hover:border-accent/40 hover:text-white"
          >
            {section.title}
          </a>
        ))}
      </nav>

      <div className="space-y-4">
        {SECTIONS.map((section) => (
          <section key={section.id} id={section.id} className="glass scroll-mt-24 p-5">
            <h2 className="text-base font-semibold text-white">{section.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">{section.body}</p>
            <ul className="mt-4 space-y-2">
              {section.points.map((point) => (
                <li key={point} className="flex gap-2 text-sm leading-relaxed text-slate-300">
                  <ShieldCheck size={15} className="mt-0.5 shrink-0 text-risk-low" aria-hidden="true" />
                  {point}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <section className="glass-strong p-5">
        <h2 className="flex items-center gap-2 text-base font-semibold text-white">
          <PhoneCall size={17} className="text-accent" aria-hidden="true" /> Official resources
        </h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {RESOURCES.map((resource) => (
            <a
              key={resource.href}
              href={resource.href}
              target="_blank"
              rel="noreferrer noopener"
              className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-accent/30 hover:bg-accent/5"
            >
              <p className="flex items-center gap-1.5 text-sm font-semibold text-white">
                {resource.title}
                <ExternalLink size={13} className="text-slate-500" aria-hidden="true" />
              </p>
              <p className="mt-1.5 text-xs leading-relaxed text-slate-400">{resource.note}</p>
            </a>
          ))}
        </div>
        <p className="mt-4 text-xs text-slate-500">
          Helpline 1930 for financial cyber fraud · 112 for immediate police assistance.
        </p>
      </section>
    </div>
  );
}
