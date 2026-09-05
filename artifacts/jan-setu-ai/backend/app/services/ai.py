import re


CATEGORY_RULES = {
    "Roads & mobility": (
        "road",
        "street",
        "traffic",
        "bus",
        "transport",
        "सड़क",
        "रास्ता",
        "बस",
    ),
    "Water & sanitation": (
        "water",
        "drain",
        "toilet",
        "sewage",
        "पानी",
        "नाली",
        "शौचालय",
    ),
    "Healthcare": (
        "health",
        "hospital",
        "clinic",
        "medicine",
        "स्वास्थ्य",
        "अस्पताल",
        "दवा",
    ),
    "Education": (
        "school",
        "teacher",
        "classroom",
        "education",
        "स्कूल",
        "शिक्षा",
    ),
    "Electricity": (
        "electricity",
        "power",
        "streetlight",
        "बिजली",
        "रोशनी",
    ),
}

LOCATION_HINTS = (
    "village",
    "ward",
    "district",
    "block",
    "market",
    "school",
    "गांव",
    "वार्ड",
    "जिला",
    "बाजार",
)


def detect_language(text: str) -> str:
    if re.search(r"[\u0900-\u097f]", text):
        return "hi"
    return "en"


def detect_category(text: str) -> str:
    normalized = text.casefold()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword.casefold() in normalized for keyword in keywords):
            return category
    return "Other civic services"


def extract_location(text: str, provided_location: str | None) -> str:
    if provided_location:
        return provided_location.strip()

    words = text.strip().split()
    for index, word in enumerate(words[:-1]):
        if word.casefold().strip(",.") in LOCATION_HINTS:
            return f"{word.strip(',.' )} {words[index + 1].strip(',.')}"
    return "Location to be verified"


def build_issue(text: str, category: str) -> str:
    clean_text = " ".join(text.split())
    if len(clean_text) <= 92:
        return clean_text
    return f"{category} request: {clean_text[:89].rstrip()}..."


def score_request(text: str, category: str) -> int:
    score = 52
    if category in {"Healthcare", "Water & sanitation"}:
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


def analyze_request(text: str, location: str | None = None) -> dict[str, str | float | int]:
    language = detect_language(text)
    category = detect_category(text)
    resolved_location = extract_location(text, location)
    priority_score = score_request(text, category)
    return {
        "language": language,
        "category": category,
        "location": resolved_location,
        "issue": build_issue(text, category),
        "confidence": 0.86 if category != "Other civic services" else 0.61,
        "priority_score": priority_score,
        "priority_label": label_for_score(priority_score),
    }