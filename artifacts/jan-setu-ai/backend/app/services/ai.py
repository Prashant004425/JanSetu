import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import settings


CATEGORY_RULES = {
    "Roads & Transport": (
        "road",
        "traffic",
        "bus",
        "transport",
        "सड़क",
        "रास्ता",
        "बस",
        "রাস্তা", "ରାସ୍ତା", "రోడ్డు", "रस्ता", "சாலை", "ರಸ್ತೆ", "റോഡ്", "ਸੜਕ", "سڑک",
        "road condition",
    ),
    "Water & Sanitation": (
        "water",
        "drain",
        "toilet",
        "sewage",
        "पानी",
        "नाली",
        "शौचालय",
        "পানি", "জল", "ପାଣି", "ପିଇବା", "నీరు", "నీరిన", "पाणी", "தண்ணீர்", "ನೀರು", "ನೀರಿನ",
        "വെള്ളം", "പാനീയം", "ਪਾਣੀ", "پانی", "pani", "paani", "water problem",
    ),
    "Healthcare": (
        "health",
        "hospital",
        "clinic",
        "medicine",
        "स्वास्थ्य",
        "अस्पताल",
        "दवा",
        "hospital", "হাসপাতাল", "ఆసుపత్రి", "रुग्णालय", "மருத்துவமனை", "ಆಸ್ಪತ್ರೆ", "ആശുപത്രി", "ਹਸਪਤਾਲ", "ہسپتال",
        "চিকিৎসালয়",
    ),
    "Education": (
        "school",
        "teacher",
        "classroom",
        "education",
        "स्कूल",
        "शिक्षा",
        "বিদ্যালয়", "শিক্ষক", "పాఠశాల", "शाळा", "பள்ளி", "ಶಾಲೆ", "ਸਕੂਲ",
    ),
    "Electricity": (
        "electricity",
        "power",
        "streetlight",
        "street light",
        "बिजली",
        "रोशनी",
        "বিদ্যুৎ", "વીઝળી", "વીજળી", "విద్యుత్", "वीज", "மின்சாரம்", "ವಿದ್ಯುತ್", "ವಿದ್ಯುತ್", "ವಿದ್ಯುತ್", "വൈദ്യുതി", "ਬਿਜਲੀ", "بجلی",
    ),
    "Waste Management": (
        "sanitation",
        "waste",
        "garbage",
        "toilet",
        "स्वच्छता",
        "कचरा",
        "शौचालय",
    ),
    "Public Transport": (
        "public transport",
        "bus",
        "transit",
        "परिवहन",
        "बस सेवा",
    ),
}

SUBCATEGORY_RULES = {
    "Water & Sanitation": {
        "Drinking Water": ("drinking water", "no water", "water supply", "pani", "paani", "पानी", "পানীয়", "জল", "నీరు", "पाणी", "தண்ணீர்", "ಕುಡಿಯುವ ನೀರು", "ಕುಡಿಯುವ ನೀರಿನ", "ପିଇବା ପାଣି", "വെള്ളം", "ਪਾਣੀ", "پانی"),
        "Drainage": ("drain", "नाली", "নর্দমা", "కాలువ", "नाला", "வடிகால்", "ಚರಂಡಿ", "ഡ്രെയിൻ"),
        "Toilet / Sanitation": ("toilet", "sanitation", "शौचालय", "স্বাস্থ্যবিধি", "మరుగుదొడ్డి", "शौचालय", "கழிப்பறை"),
    },
    "Roads & Transport": {
        "Road Condition": ("road", "রাস্তা", "রাস্ত", "ରାସ୍ତା", "రోడ్డు", "रस्ता", "சாலை", "ರಸ್ತೆ", "റോഡ്", "ਸੜਕ", "سڑک", "सड़क"),
        "Public Transport": ("bus", "transport", "বাস", "ବସ", "బస్సు", "बस", "பேருந்து", "ಬಸ್", "ബസ്", "ਬੱਸ"),
    },
    "Healthcare": {
        "Healthcare Facility": ("hospital", "clinic", "अस्पताल", "হাসপাতাল", "চিকিৎসালয়", "ఆసుపత్రి", "रुग्णालय", "மருத்துவமனை", "ಆಸ್ಪತ್ರೆ", "ആശുപത്രി", "ਹਸਪਤਾਲ", "ہسپتال"),
        "Medicine Availability": ("medicine", "दवा", "ওষুধ", "మందు", "औषध", "மருந்து", "ಔಷಧ", "മരുന്ന്", "ਦਵਾਈ", "دوا"),
    },
    "Education": {
        "Teacher Availability": ("teacher", "teachers", "शिक्षक", "শিক্ষক", "ఉపాధ్యాయ", "शिक्षक", "ஆசிரியர்", "ಶಿಕ್ಷಕ", "അധ്യാപക", "ਅਧਿਆਪਕ", "استاد"),
        "School Infrastructure": ("school", "classroom", "स्कूल", "বিদ্যালয়", "పాఠశాల", "शाळा", "பள்ளி", "ಶಾಲೆ", "സ്കൂൾ", "ਸਕੂਲ", "اسکول"),
    },
    "Electricity": {
        "Power Supply": ("electricity", "power", "বিদ্যুৎ", "విద్యుత్", "वीज", "மின்சாரம்", "ವಿದ್ಯುತ್", "വൈദ്യുതി", "ਬਿਜਲੀ", "بجلی"),
        "Streetlight": ("streetlight", "street light", "रोशनी", "রাস্তার আলো", "వీధి దీపం", "रस्त्यावरील दिवे", "தெருவிளக்கு", "ಬೀದಿ ದೀಪ", "തെരുവ് വിളക്ക്", "ਗਲੀ ਦੀ ਬੱਤੀ", "سٹریٹ لائٹ"),
    },
}

LOCATION_HINTS = (
    "village",
    "ward",
    "district",
    "block",
    "market",
    "गांव",
    "वार्ड",
    "जिला",
    "बाजार",
)


def detect_language(text: str) -> str:
    script_languages = (
        ("bn", r"[\u0980-\u09ff]"),
        ("pa", r"[\u0a00-\u0a7f]"),
        ("gu", r"[\u0a80-\u0aff]"),
        ("or", r"[\u0b00-\u0b7f]"),
        ("ta", r"[\u0b80-\u0bff]"),
        ("te", r"[\u0c00-\u0c7f]"),
        ("kn", r"[\u0c80-\u0cff]"),
        ("ml", r"[\u0d00-\u0d7f]"),
        ("ur", r"[\u0600-\u06ff]"),
        ("hi", r"[\u0900-\u097f]"),
    )
    for language, pattern in script_languages:
        if re.search(pattern, text):
            if language == "bn" and any(word in text for word in ("আমাৰ", "গাঁওত", "চিকিৎসালয়")):
                return "as"
            if language == "hi" and any(word in text for word in ("आमच्या", "गावातील", "रस्ता")):
                return "mr"
            return language
    if re.search(r"\b(hamare|mein|pani|paani|bahut|gaon|gaav|humare)\b", text.casefold()):
        return "hi-Latn"
    return "en" if re.search(r"[a-zA-Z]", text) else "unknown"


def detect_category(text: str) -> str:
    categories = detect_categories(text)
    return " + ".join(categories)


def detect_categories(text: str) -> list[str]:
    normalized = text.casefold()
    matches = [
        category
        for category, keywords in CATEGORY_RULES.items()
        if any(keyword.casefold() in normalized for keyword in keywords)
    ]
    return matches or ["Other civic services"]


def detect_subcategory(text: str, category: str) -> str:
    normalized = text.casefold()
    for subcategory, keywords in SUBCATEGORY_RULES.get(category, {}).items():
        if any(keyword.casefold() in normalized for keyword in keywords):
            return subcategory
    return "General civic need"


def extract_location(text: str, provided_location: str | None) -> str | None:
    if provided_location:
        return provided_location.strip()

    named_match = re.search(
        r"\b(?:from|in|at)\s+([A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?)",
        text,
    )
    if named_match:
        candidate = named_match.group(1).strip(" .,")
        if candidate.casefold() not in {"our village", "the village"}:
            return candidate

    words = text.strip().split()
    for index, word in enumerate(words[:-1]):
        if word.casefold().strip(",.") in LOCATION_HINTS:
            candidate = f"{word.strip(',.' )} {words[index + 1].strip(',.')}"
            if candidate.casefold() in {
                "village road", "our village", "village mein", "village for",
                "हमारे गांव", "गांव में", "गांव का", "गांव की"
            }:
                continue
            return candidate
    return None


def build_issue(text: str, category: str) -> str:
    clean_text = " ".join(text.split())
    if len(clean_text) <= 92:
        return clean_text
    return f"{category} request: {clean_text[:89].rstrip()}..."


def translate_to_common_language(
    text: str,
    categories: list[str],
    location: str | None,
) -> str:
    if detect_language(text) in {"en", "hi-Latn"}:
        return text

    exact_translations = {
        "हमारे गांव में पीने का पानी नहीं आता।": "There is no drinking water supply in our village.",
        "हमारे गांव में पीने का पानी नहीं आता": "There is no drinking water supply in our village.",
        "আমাদের গ্রামে পানীয় জলের সমস্যা হচ্ছে।": "There is a drinking water problem in our village.",
    }
    if text.strip() in exact_translations:
        return exact_translations[text.strip()]

    category_text = " and ".join(categories).lower()
    location_text = location or "an unspecified area"
    return (
        f"Resident reports a {category_text} need near {location_text}. "
        f"The original {detect_language(text)} request has been normalized into English for shared analysis."
    )


def classify_urgency(text: str, categories: list[str]) -> tuple[str, str]:
    normalized = text.casefold()
    urgent_signals = (
        "urgent",
        "unsafe",
        "emergency",
        "immediately",
        "danger",
        "तुरंत",
        "खतरा",
        "आपात",
    )
    severe_signals = (
        "broken",
        "outage",
        "dry",
        "no water",
        "medicine",
        "खराब",
        "सूखा",
        "पानी नहीं",
        "दवा",
    )
    if any(signal in normalized for signal in urgent_signals):
        return "HIGH", "HIGH"
    if any(signal in normalized for signal in severe_signals) or any(
        category in {"Healthcare", "Water & Sanitation"} for category in categories
    ):
        return "HIGH", "HIGH"
    if "Roads & Transport" in categories or "Electricity" in categories:
        return "MEDIUM", "MEDIUM"
    return "LOW", "LOW"


def normalize_urgency(value: object, fallback: str = "LOW") -> str:
    normalized = str(value).strip().upper()
    if normalized in {"HIGH", "MEDIUM", "LOW"}:
        return normalized
    if normalized in {"IMMEDIATE", "SOON"}:
        return "HIGH" if normalized == "IMMEDIATE" else "MEDIUM"
    if normalized in {"MONITOR", "LOW PRIORITY"}:
        return "LOW"
    return fallback


def score_request(text: str, category: str) -> int:
    score = 52
    if any(
        current_category in category
        for current_category in {"Healthcare", "Water & Sanitation"}
    ):
        score += 16
    if any(
        signal in text.casefold()
        for signal in ("urgent", "unsafe", "broken", "outage", "emergency", "तुरंत", "खराब")
    ):
        score += 12
    if len(text.split()) > 16:
        score += 5
    return min(score, 96)


def label_for_score(score: int) -> str:
    if score >= 75:
        return "High priority"
    if score >= 55:
        return "Needs review"
    return "Monitor"


def analyze_with_rules(
    text: str, location: str | None = None
) -> dict[str, str | float | int | None]:
    language = detect_language(text)
    categories = detect_categories(text)
    category = " + ".join(categories)
    subcategory = detect_subcategory(text, categories[0])
    resolved_location = extract_location(text, location)
    translated_text = translate_to_common_language(
        text,
        categories,
        resolved_location,
    )
    urgency, severity = classify_urgency(text, categories)
    priority_score = score_request(text, category)
    return {
        "language": language,
        "translated_text": translated_text,
        "understanding": (
            f"{category} concern reported in {resolved_location or 'an unspecified area'}. "
            f"Recommended response window: {urgency.lower()}."
        ),
        "categories": categories,
        "category": category,
        "subcategory": subcategory,
        "location": resolved_location,
        "issue": build_issue(text, category),
        "urgency": urgency,
        "severity": severity,
        "confidence": 0.86 if category != "Other civic services" else 0.61,
        "priority_score": priority_score,
        "priority_label": label_for_score(priority_score),
    }


LLM_FIELDS = (
    "language",
    "translated_text",
    "understanding",
    "categories",
    "category",
    "subcategory",
    "location",
    "issue",
    "urgency",
    "severity",
    "confidence",
    "priority_score",
    "priority_label",
)


def _llm_analysis(
    text: str, location: str | None
) -> dict[str, str | float | int] | None:
    prompt = {
        "role": "user",
        "content": (
            "Analyze this citizen development request. Return only valid JSON with "
            "these keys: language, translated_text, understanding, categories "
            "(array), category, subcategory, location, issue, urgency, severity, confidence "
            "(number 0 to 1), priority_score (integer 0 to 100), priority_label. "
            "Use concise English for normalized fields. Preserve the original meaning. "
            f"Provided location: {location or 'not provided'}\nRequest: {text}"
        ),
    }
    body = json.dumps(
        {
            "model": settings.llm_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "You are a civic-intelligence analyst for India.",
                },
                prompt,
            ],
        }
    ).encode("utf-8")
    request = Request(
        settings.llm_api_url,
        data=body,
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.llm_timeout_seconds) as response:
            payload = json.load(response)
        content = payload["choices"][0]["message"]["content"]
        result = json.loads(content)
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError):
        return None

    if not all(field in result for field in LLM_FIELDS):
        return None
    if (
        not isinstance(result["categories"], list)
        or not 0 <= float(result["confidence"]) <= 1
        or not 0 <= int(result["priority_score"]) <= 100
    ):
        return None
    result["urgency"] = normalize_urgency(result["urgency"])
    result["severity"] = normalize_urgency(result["severity"])
    return result


def analyze_request(
    text: str, location: str | None = None
) -> dict[str, str | float | int | None]:
    if settings.active_ai_provider == "llm":
        llm_result = _llm_analysis(text, location)
        if llm_result is not None:
            return llm_result
    return analyze_with_rules(text, location)