"""Evidence based explanation generation.

Explanations are written from the indicators that actually matched - never from
a generic template alone - and are available in English, Hindi and Hinglish.
"""

from __future__ import annotations

from app.services.detection.categories import category_label
from app.services.detection.rules import Indicator

LEVEL_TEXT = {
    "en": {
        "Low": "Low risk",
        "Medium": "Medium risk",
        "High": "High risk",
        "Critical": "Critical risk",
        "Uncertain": "Uncertain - not enough signal",
    },
    "hinglish": {
        "Low": "Kam risk",
        "Medium": "Medium risk",
        "High": "Zyada risk",
        "Critical": "Bahut zyada risk",
        "Uncertain": "Clear nahi hai - poori jaankari nahi mili",
    },
    "hi": {
        "Low": "कम जोखिम",
        "Medium": "मध्यम जोखिम",
        "High": "उच्च जोखिम",
        "Critical": "गंभीर जोखिम",
        "Uncertain": "स्पष्ट नहीं - पर्याप्त संकेत नहीं",
    },
}

LABELS = {
    "en": {},
    "hinglish": {
        "credential_request": "OTP, PIN ya password maanga ja raha hai",
        "account_data_request": "bank ya identity details maangi ja rahi hain",
        "kyc_update": "turant KYC update karne ko kaha ja raha hai",
        "threat_of_block": "account ya SIM block karne ki dhamki",
        "urgency_pressure": "jaldi karne ka dabav",
        "authority_impersonation": "bank ya sarkari vibhag ka naam use kiya gaya hai",
        "lottery_lure": "inaam ya lottery jeetne ka dava",
        "advance_fee": "pehle fees ya charge maanga ja raha hai",
        "job_lure": "ghar baithe zyada kamai ka lalach",
        "upi_collect_or_pin": "paisa lene ke liye UPI PIN ya QR",
        "refund_bait": "bina maange refund ya cashback ka lalach",
        "link_in_message": "message mein link diya gaya hai",
        "shortener_in_message": "link shortener se asli website chhupayi gayi hai",
        "generic_greeting": "'Dear Customer' jaisa general sambodhan",
        "channel_redirect": "WhatsApp ya Telegram par le jaane ki koshish",
        "investment_returns": "guaranteed ya asambhav munafa",
        "delivery_parcel": "parcel fail hone ka bahana",
        "fake_support": "customer care number diya gaya hai",
        "account_takeover_setup": "remote access app install karne ko kaha ja raha hai",
        "money_mule": "paise receive karke aage bhejne ko kaha ja raha hai",
        "secrecy_pressure": "baat kisi ko na batane ko kaha gaya hai",
        "digital_arrest": "digital arrest ya police case ki dhamki",
        "otp_delivery_claim": "OTP bhejne ka dava",
        "vague_threat_generic": "aspaṣht dhamki",
        "callback_request": "message mein diye number par call karne ko kaha gaya hai",
        "gift_card_crypto": "gift card ya crypto se payment",
        "loan_offer": "bina paperwork turant loan ka offer",
        "electricity_gas_threat": "bijli ya gas katne ki dhamki",
        "suspicious_attachment": "anjaan attachment ya file",
        "nlp_caps_flood": "poore capital letters",
        "nlp_punctuation_flood": "zyada ! aur ? ka istemal",
        "nlp_multiple_links": "ek se zyada link",
        "nlp_obfuscated_text": "chhupe ya milte-julte characters",
        "nlp_multiple_phone_numbers": "kai phone numbers",
    },
    "hi": {
        "credential_request": "ओटीपी, पिन या पासवर्ड मांगा जा रहा है",
        "account_data_request": "बैंक या पहचान की जानकारी मांगी जा रही है",
        "kyc_update": "तुरंत केवाईसी अपडेट करने का दबाव",
        "threat_of_block": "खाता या सिम बंद करने की धमकी",
        "urgency_pressure": "जल्दी करने का दबाव",
        "authority_impersonation": "बैंक या सरकारी विभाग का नाम इस्तेमाल",
        "lottery_lure": "इनाम या लॉटरी जीतने का दावा",
        "advance_fee": "पहले शुल्क या चार्ज मांगा जा रहा है",
        "job_lure": "घर बैठे अधिक कमाई का लालच",
        "upi_collect_or_pin": "पैसा लेने के लिए यूपीआई पिन या क्यूआर",
        "refund_bait": "बिना मांगे रिफंड या कैशबैक का लालच",
        "link_in_message": "संदेश में लिंक दिया गया है",
        "shortener_in_message": "लिंक शॉर्टनर से असली वेबसाइट छिपाई गई है",
        "generic_greeting": "'प्रिय ग्राहक' जैसा सामान्य संबोधन",
        "channel_redirect": "व्हाट्सएप या टेलीग्राम पर ले जाने की कोशिश",
        "investment_returns": "गारंटीड या असंभव मुनाफा",
        "delivery_parcel": "पार्सल विफल होने का बहाना",
        "fake_support": "कस्टमर केयर नंबर दिया गया है",
        "account_takeover_setup": "रिमोट एक्सेस ऐप इंस्टॉल करने को कहा जा रहा है",
        "money_mule": "पैसा लेकर आगे भेजने को कहा जा रहा है",
        "secrecy_pressure": "बात किसी को न बताने को कहा गया है",
        "digital_arrest": "डिजिटल अरेस्ट या पुलिस केस की धमकी",
        "otp_delivery_claim": "ओटीपी भेजने का दावा",
        "vague_threat_generic": "अस्पष्ट धमकी",
        "callback_request": "संदेश में दिए नंबर पर कॉल करने को कहा गया है",
        "gift_card_crypto": "गिफ्ट कार्ड या क्रिप्टो से भुगतान",
        "loan_offer": "बिना कागजी कार्रवाई तुरंत लोन का ऑफर",
        "electricity_gas_threat": "बिजली या गैस कटने की धमकी",
        "suspicious_attachment": "अनजान अटैचमेंट या फाइल",
        "nlp_caps_flood": "पूरे बड़े अक्षर",
        "nlp_punctuation_flood": "अधिक विस्मयादिबोधक चिह्न",
        "nlp_multiple_links": "एक से अधिक लिंक",
        "nlp_obfuscated_text": "छिपे या मिलते-जुलते अक्षर",
        "nlp_multiple_phone_numbers": "कई फोन नंबर",
    },
}

GENERIC_ACTIONS = {
    "en": [
        "Do not reply, call back or click any link in the message.",
        "Verify independently through the organisation's official app or the number printed on your card.",
        "If you already shared an OTP, PIN or password, call your bank's official helpline and ask them to freeze the account.",
        "Report the message on https://cybercrime.gov.in and forward it to 1909 (Chakshu) for telecom fraud.",
    ],
    "hinglish": [
        "Message ka jawab na dein, na call karein, na kisi link par click karein.",
        "Bank ke official app ya card par likhe number se khud verify karein.",
        "Agar OTP, PIN ya password share kar diya hai to turant bank ki official helpline par call karke account freeze karwayein.",
        "https://cybercrime.gov.in par report karein aur telecom fraud ke liye 1909 (Chakshu) par forward karein.",
    ],
    "hi": [
        "संदेश का जवाब न दें, न कॉल करें, न किसी लिंक पर क्लिक करें।",
        "संस्था के आधिकारिक ऐप या कार्ड पर छपे नंबर से स्वयं पुष्टि करें।",
        "अगर ओटीपी, पिन या पासवर्ड साझा कर दिया है तो तुरंत बैंक की आधिकारिक हेल्पलाइन पर कॉल कर खाता फ्रीज कराएं।",
        "https://cybercrime.gov.in पर रिपोर्ट करें और टेलीकॉम धोखाधड़ी के लिए 1909 (चक्षु) पर भेजें।",
    ],
}

CATEGORY_ACTIONS = {
    "bank_kyc": {
        "en": ["Never complete KYC through a link in an SMS or WhatsApp message.", "Check your account only inside the bank's own app."],
        "hinglish": ["SMS ya WhatsApp link se KYC kabhi na karein.", "Account sirf bank ke apne app mein check karein."],
        "hi": ["एसएमएस या व्हाट्सएप लिंक से केवाईसी कभी न करें।", "खाता केवल बैंक के अपने ऐप में जांचें।"],
    },
    "upi_payment": {
        "en": ["Receiving money never needs a PIN, QR scan or approval.", "Reject unexpected collect requests in your UPI app."],
        "hinglish": ["Paisa lene ke liye PIN ya QR ki zaroorat kabhi nahi hoti.", "UPI app mein anjaan collect request reject karein."],
        "hi": ["पैसा प्राप्त करने के लिए पिन या क्यूआर की आवश्यकता कभी नहीं होती।", "यूपीआई ऐप में अनजान कलेक्ट रिक्वेस्ट अस्वीकार करें।"],
    },
    "phishing": {
        "en": ["Type the official website address yourself instead of clicking the link.", "Check the domain carefully - a real bank never uses a hyphenated lookalike domain."],
        "hinglish": ["Link par click na karein, official website ka address khud type karein.", "Domain dhyan se dekhein - asli bank aise milte-julte domain use nahi karta."],
        "hi": ["लिंक पर क्लिक न करें, आधिकारिक वेबसाइट का पता स्वयं टाइप करें।", "डोमेन ध्यान से देखें - असली बैंक ऐसा मिलता-जुलता डोमेन नहीं उपयोग करता।"],
    },
    "fake_job": {
        "en": ["A genuine employer never charges a registration or joining fee.", "Check the company's official careers page and its GST/CIN details before paying anything."],
        "hinglish": ["Asli employer kabhi registration ya joining fee nahi leta.", "Koi paisa dene se pehle company ka official careers page aur GST/CIN check karein."],
        "hi": ["असली नियोक्ता कभी पंजीकरण या जॉइनिंग शुल्क नहीं लेता।", "कोई भुगतान करने से पहले कंपनी का आधिकारिक करियर पेज और जीएसटी/सीआईएन जांचें।"],
    },
    "lottery_reward": {
        "en": ["You cannot win a lottery you never entered.", "No prize ever requires an advance tax, processing fee or courier charge."],
        "hinglish": ["Jis lottery mein aapne hissa nahi liya, wo jeet nahi sakte.", "Kisi inaam ke liye pehle tax ya processing fee nahi deni hoti."],
        "hi": ["जिस लॉटरी में आपने भाग नहीं लिया, उसे जीत नहीं सकते।", "किसी इनाम के लिए पहले कर या प्रोसेसिंग शुल्क नहीं देना होता।"],
    },
    "govt_impersonation": {
        "en": ["Government offices never demand payment or documents over WhatsApp.", "There is no 'digital arrest' in Indian law - police never interrogate you on a video call."],
        "hinglish": ["Sarkari daftar WhatsApp par paisa ya documents nahi maangta.", "Bharatiya kanoon mein 'digital arrest' jaisi koi cheez nahi hai."],
        "hi": ["सरकारी दफ्तर व्हाट्सएप पर पैसा या दस्तावेज नहीं मांगते।", "भारतीय कानून में 'डिजिटल अरेस्ट' जैसी कोई व्यवस्था नहीं है।"],
    },
    "otp_account_takeover": {
        "en": ["Share an OTP with nobody - not with a bank, police, delivery agent or family member.", "If an OTP arrived that you did not request, treat your account as under attack."],
        "hinglish": ["OTP kisi ko na batayein - bank, police, delivery agent ya parivar mein bhi nahi.", "Bina maange OTP aaya hai to samajhiye account par hamla ho raha hai."],
        "hi": ["ओटीपी किसी को न बताएं - बैंक, पुलिस, डिलीवरी एजेंट या परिवार को भी नहीं।", "बिना मांगे ओटीपी आया है तो मानें कि खाते पर हमला हो रहा है।"],
    },
    "investment": {
        "en": ["Guaranteed high returns are always a fraud, however professional the group looks.", "Only invest through SEBI registered intermediaries."],
        "hinglish": ["Guaranteed zyada munafa hamesha dhokha hai, group kitna bhi professional lage.", "Sirf SEBI registered intermediary se invest karein."],
        "hi": ["गारंटीड अधिक मुनाफा हमेशा धोखा है, समूह कितना भी पेशेवर लगे।", "केवल सेबी पंजीकृत मध्यस्थ से निवेश करें।"],
    },
    "delivery_parcel": {
        "en": ["Track the parcel only on the courier's official website using your own order number.", "A redelivery fee is almost always a card-harvesting page."],
        "hinglish": ["Parcel sirf courier ki official website par apne order number se track karein.", "Redelivery fee ka link aksar card details churane ke liye hota hai."],
        "hi": ["पार्सल केवल कूरियर की आधिकारिक वेबसाइट पर अपने ऑर्डर नंबर से ट्रैक करें।", "रीडिलीवरी शुल्क का लिंक अक्सर कार्ड विवरण चुराने के लिए होता है।"],
    },
    "fake_customer_support": {
        "en": ["Find the helpline only on the official app or website, never from a search ad or forwarded message.", "Never install a screen sharing app at a caller's request."],
        "hinglish": ["Helpline sirf official app ya website se lein, search ad ya forwarded message se nahi.", "Kisi caller ke kehne par screen sharing app install na karein."],
        "hi": ["हेल्पलाइन केवल आधिकारिक ऐप या वेबसाइट से लें, सर्च विज्ञापन या फॉरवर्ड संदेश से नहीं।", "किसी कॉलर के कहने पर स्क्रीन शेयरिंग ऐप इंस्टॉल न करें।"],
    },
    "malicious_url": {
        "en": ["Do not open the link on any device.", "If you already opened it, do not enter any details and clear your browser data."],
        "hinglish": ["Link ko kisi bhi device par na kholein.", "Agar khol liya hai to koi detail na daalein aur browser data clear karein."],
        "hi": ["लिंक को किसी भी डिवाइस पर न खोलें।", "अगर खोल लिया है तो कोई विवरण न भरें और ब्राउज़र डेटा साफ करें।"],
    },
    "unknown": {
        "en": ["No specific scam pattern matched. Treat it as unverified rather than safe.", "Verify the sender through a channel you already trust before acting."],
        "hinglish": ["Koi khaas scam pattern nahi mila. Ise 'safe' nahi, 'unverified' maanein.", "Kuch karne se pehle sender ko apne bharose ke channel se verify karein."],
        "hi": ["कोई विशिष्ट धोखाधड़ी पैटर्न नहीं मिला। इसे 'सुरक्षित' नहीं, 'असत्यापित' मानें।", "कुछ करने से पहले प्रेषक को अपने विश्वसनीय माध्यम से सत्यापित करें।"],
    },
}


def _labels(language: str) -> dict[str, str]:
    return LABELS.get(language, {})


def label_for(indicator: Indicator, language: str) -> str:
    return _labels(language).get(indicator.id, indicator.label)


def _join(items: list[str], language: str) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if language == "en":
        return ", ".join(items[:-1]) + " and " + items[-1]
    return ", ".join(items[:-1]) + " aur " + items[-1] if language == "hinglish" else ", ".join(items[:-1]) + " और " + items[-1]


def build_explanation(
    *,
    language: str,
    category_key: str,
    score: int,
    level: str,
    indicators: list[Indicator],
    mitigators: list[Indicator],
    is_url: bool = False,
    url_host: str | None = None,
    url_findings: list[str] | None = None,
) -> tuple[str, list[str]]:
    """Return (plain language explanation, recommended actions)."""
    language = language if language in ("en", "hi", "hinglish") else "en"
    level_text = LEVEL_TEXT[language][level]
    category = category_label(category_key)
    top = sorted(indicators, key=lambda ind: ind.weight, reverse=True)[:3]
    top_labels = [label_for(ind, language) for ind in top]

    if language == "en":
        if is_url:
            findings_text = _join(url_findings or [], "en")
            summary = (
                f"This link scored {score}/100 ({level_text})."
                + (f" Host: {url_host}." if url_host else "")
                + (f" What the analysis found: {findings_text}." if findings_text else " No structural red flags were found in the link itself.")
                + " A clean structural analysis is not a guarantee that a site is safe."
            )
        elif not indicators:
            summary = (
                f"No known scam pattern matched this message, so the risk score is {score}/100 ({level_text}). "
                "That means the engine found no warning signs - not that the message is proven genuine. "
                "If it involves money, credentials or urgency, verify the sender independently."
            )
        else:
            summary = (
                f"This message scored {score}/100 ({level_text}) and looks like {category.lower()}. "
                f"The strongest signals are: {_join(top_labels, 'en')}. "
                f"{len(indicators)} warning sign{'s' if len(indicators) != 1 else ''} matched in total."
            )
            if mitigators:
                summary += (
                    " It also contains signals typical of genuine alerts ("
                    + _join([m.label.lower() for m in mitigators], "en")
                    + "), which reduced the score."
                )
        actions = list(GENERIC_ACTIONS["en"]) + list(CATEGORY_ACTIONS.get(category_key, CATEGORY_ACTIONS["unknown"])["en"])
        return summary, actions

    if language == "hinglish":
        if is_url:
            summary = (
                f"Is link ka score {score}/100 ({level_text}) hai."
                + (f" Host: {url_host}." if url_host else "")
                + " Link ko kholein nahi. Domain ki spelling aur HTTPS dono dhyan se dekhein - HTTPS hone ka matlab safe hona nahi hota."
            )
        elif not indicators:
            summary = (
                f"Is message mein koi jaana-pehchaana scam pattern nahi mila, isliye score {score}/100 ({level_text}) hai. "
                "Iska matlab sirf ye hai ki koi warning sign nahi mila - message asli hai ye saabit nahi hota. "
                "Agar paisa, OTP ya jaldi karne ki baat ho to sender ko khud verify karein."
            )
        else:
            summary = (
                f"Is message ka score {score}/100 ({level_text}) hai aur ye {category} jaisa lagta hai. "
                f"Sabse strong sanket: {_join(top_labels, 'hinglish')}. "
                f"Kul {len(indicators)} warning sign mile."
            )
            if mitigators:
                summary += " Isme asli alerts jaise kuch sanket bhi hain, isliye score kam kiya gaya."
        actions = list(GENERIC_ACTIONS["hinglish"]) + list(CATEGORY_ACTIONS.get(category_key, CATEGORY_ACTIONS["unknown"])["hinglish"])
        return summary, actions

    # Hindi
    if is_url:
        summary = (
            f"इस लिंक का स्कोर {score}/100 ({level_text}) है।"
            + (f" होस्ट: {url_host}।" if url_host else "")
            + " लिंक को न खोलें। डोमेन की स्पेलिंग ध्यान से देखें - केवल HTTPS होना सुरक्षा का प्रमाण नहीं है।"
        )
    elif not indicators:
        summary = (
            f"इस संदेश में कोई ज्ञात धोखाधड़ी पैटर्न नहीं मिला, इसलिए स्कोर {score}/100 ({level_text}) है। "
            "इसका अर्थ केवल यह है कि कोई चेतावनी संकेत नहीं मिला - संदेश असली है यह सिद्ध नहीं होता। "
            "अगर पैसा, ओटीपी या जल्दबाजी की बात हो तो प्रेषक से स्वयं पुष्टि करें।"
        )
    else:
        summary = (
            f"इस संदेश का स्कोर {score}/100 ({level_text}) है और यह {category} जैसा दिखता है। "
            f"सबसे मजबूत संकेत: {_join(top_labels, 'hi')}। "
            f"कुल {len(indicators)} चेतावनी संकेत मिले।"
        )
        if mitigators:
            summary += " इसमें असली अलर्ट जैसे संकेत भी हैं, इसलिए स्कोर घटाया गया है।"
    actions = list(GENERIC_ACTIONS["hi"]) + list(CATEGORY_ACTIONS.get(category_key, CATEGORY_ACTIONS["unknown"])["hi"])
    return summary, actions
