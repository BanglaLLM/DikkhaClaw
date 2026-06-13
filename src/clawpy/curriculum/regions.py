"""Region-based education system configurations.

Each region defines tracks, subjects, exams, and universities.
Adding a new country = adding a new JSON-like config here.
AI translation can generate localized names from English keys.
"""

from __future__ import annotations

REGIONS: dict[str, dict] = {
    "bd": {
        "id": "bd",
        "name": "Bangladesh",
        "name_local": "বাংলাদেশ",
        "grade_level": "HSC (Grade 11-12)",
        "grade_level_local": "এইচএসসি (একাদশ-দ্বাদশ)",
        "language": "bn",
        "tracks": {
            "engineering": {
                "title": "Engineering",
                "title_local": "ইঞ্জিনিয়ারিং",
                "description": "BUET, KUET, RUET, CUET, IUT",
                "icon": "⚙️",
                "subjects": ["physics", "chemistry", "higher_math"],
                "weights": {"physics": 0.35, "higher_math": 0.35, "chemistry": 0.30},
                "exams": ["buet", "cuet", "kuet", "ruet", "iut", "sust"],
            },
            "medical": {
                "title": "Medical",
                "title_local": "মেডিকেল",
                "description": "MBBS admission",
                "icon": "🏥",
                "subjects": ["biology", "chemistry", "physics", "general_math"],
                "weights": {"biology": 0.40, "chemistry": 0.30, "physics": 0.20, "general_math": 0.10},
                "exams": ["medical"],
            },
            "university": {
                "title": "University Science",
                "title_local": "বিশ্ববিদ্যালয়",
                "description": "DU, RU, CU, JU, GST",
                "icon": "🏛️",
                "subjects": ["physics", "chemistry", "higher_math", "biology", "general_math"],
                "weights": {"physics": 0.20, "chemistry": 0.20, "higher_math": 0.20, "biology": 0.20, "general_math": 0.20},
                "exams": ["du", "ru", "cu", "ju", "gst"],
            },
        },
        "universities": {
            "buet": {"name": "BUET", "name_local": "বুয়েট", "track": "engineering", "city": "Dhaka"},
            "cuet": {"name": "CUET", "name_local": "চুয়েট", "track": "engineering", "city": "Chittagong"},
            "kuet": {"name": "KUET", "name_local": "কুয়েট", "track": "engineering", "city": "Khulna"},
            "ruet": {"name": "RUET", "name_local": "রুয়েট", "track": "engineering", "city": "Rajshahi"},
            "iut": {"name": "IUT", "name_local": "আইইউটি", "track": "engineering", "city": "Gazipur"},
            "sust": {"name": "SUST", "name_local": "শাবিপ্রবি", "track": "engineering", "city": "Sylhet"},
            "du": {"name": "Dhaka University", "name_local": "ঢাকা বিশ্ববিদ্যালয়", "track": "university", "city": "Dhaka"},
            "ru": {"name": "Rajshahi University", "name_local": "রাজশাহী বিশ্ববিদ্যালয়", "track": "university", "city": "Rajshahi"},
            "cu": {"name": "Chittagong University", "name_local": "চট্টগ্রাম বিশ্ববিদ্যালয়", "track": "university", "city": "Chittagong"},
            "ju": {"name": "Jahangirnagar University", "name_local": "জাহাঙ্গীরনগর বিশ্ববিদ্যালয়", "track": "university", "city": "Dhaka"},
            "gst": {"name": "GST Cluster (19 Universities)", "name_local": "জিএসটি ক্লাস্টার", "track": "university", "city": "Nationwide"},
            "medical": {"name": "Medical Colleges", "name_local": "মেডিকেল কলেজ", "track": "medical", "city": "Nationwide"},
        },
        "subjects": {
            "physics": {"title": "Physics", "title_local": "পদার্থবিজ্ঞান", "icon": "⚛️"},
            "chemistry": {"title": "Chemistry", "title_local": "রসায়ন", "icon": "⚗️"},
            "higher_math": {"title": "Higher Mathematics", "title_local": "উচ্চতর গণিত", "icon": "📐"},
            "general_math": {"title": "General Mathematics", "title_local": "সাধারণ গণিত", "icon": "➕"},
            "biology": {"title": "Biology", "title_local": "জীববিজ্ঞান", "icon": "🧬"},
        },
    },
    "in": {
        "id": "in",
        "name": "India",
        "name_local": "भारत",
        "grade_level": "Class 11-12 (CBSE/State Board)",
        "grade_level_local": "कक्षा 11-12",
        "language": "hi",
        "tracks": {
            "engineering": {
                "title": "Engineering",
                "title_local": "इंजीनियरिंग",
                "description": "JEE Main + Advanced, BITSAT",
                "icon": "⚙️",
                "subjects": ["physics", "chemistry", "mathematics"],
                "weights": {"physics": 0.33, "chemistry": 0.33, "mathematics": 0.34},
                "exams": ["jee_main", "jee_advanced", "bitsat"],
            },
            "medical": {
                "title": "Medical",
                "title_local": "मेडिकल",
                "description": "NEET UG",
                "icon": "🏥",
                "subjects": ["biology", "chemistry", "physics"],
                "weights": {"biology": 0.40, "chemistry": 0.30, "physics": 0.30},
                "exams": ["neet"],
            },
        },
        "universities": {
            "jee_main": {"name": "JEE Main (NITs/IIITs)", "name_local": "JEE Main", "track": "engineering", "city": "Nationwide"},
            "jee_advanced": {"name": "JEE Advanced (IITs)", "name_local": "JEE Advanced", "track": "engineering", "city": "Nationwide"},
            "bitsat": {"name": "BITS Pilani", "name_local": "BITS पिलानी", "track": "engineering", "city": "Pilani"},
            "neet": {"name": "NEET UG", "name_local": "NEET", "track": "medical", "city": "Nationwide"},
        },
        "subjects": {
            "physics": {"title": "Physics", "title_local": "भौतिक विज्ञान", "icon": "⚛️"},
            "chemistry": {"title": "Chemistry", "title_local": "रसायन विज्ञान", "icon": "⚗️"},
            "mathematics": {"title": "Mathematics", "title_local": "गणित", "icon": "📐"},
            "biology": {"title": "Biology", "title_local": "जीव विज्ञान", "icon": "🧬"},
        },
    },
}

DEFAULT_REGION = "bd"


def get_region(region_id: str | None = None) -> dict:
    return REGIONS.get(region_id or DEFAULT_REGION, REGIONS[DEFAULT_REGION])


def get_all_regions() -> dict[str, dict]:
    return {
        rid: {"id": r["id"], "name": r["name"], "name_local": r["name_local"], "language": r["language"]}
        for rid, r in REGIONS.items()
    }
