"""
Multilingual support — language detection, instruction mapping,
and translation helpers for 13 supported Indian languages.
"""

from __future__ import annotations

from typing import Dict, Optional

LANGUAGE_MAP: Dict[str, Dict[str, str]] = {
    "en": {
        "name": "English",
        "native": "English",
        "greeting": "Namaste! I am AyurVani, your Ayurvedic health assistant.",
        "disclaimer": (
            "This guidance is educational and based on traditional Ayurvedic principles. "
            "Please consult a qualified healthcare provider for medical concerns."
        ),
    },
    "hi": {
        "name": "Hindi",
        "native": "हिन्दी",
        "greeting": "नमस्ते! मैं आयुर्वाणी हूँ, आपकी आयुर्वेदिक स्वास्थ्य सहायक।",
        "disclaimer": (
            "यह मार्गदर्शन शैक्षिक है और पारंपरिक आयुर्वेदिक सिद्धांतों पर आधारित है। "
            "कृपया चिकित्सा संबंधी चिंताओं के लिए योग्य स्वास्थ्य सेवा प्रदाता से परामर्श करें।"
        ),
    },
    "ta": {
        "name": "Tamil",
        "native": "தமிழ்",
        "greeting": "வணக்கம்! நான் ஆயுர்வாணி, உங்கள் ஆயுர்வேத சுகாதார உதவியாளர்.",
        "disclaimer": (
            "இந்த வழிகாட்டுதல் கல்வி நோக்கமானது மற்றும் பாரம்பரிய ஆயுர்வேத கோட்பாடுகளை அடிப்படையாகக் கொண்டது."
        ),
    },
    "te": {
        "name": "Telugu",
        "native": "తెలుగు",
        "greeting": "నమస్కారం! నేను ఆయుర్వాణి, మీ ఆయుర్వేద ఆరోగ్య సహాయకురాలు.",
        "disclaimer": "ఈ మార్గదర్శకత్వం విద్యాపరమైనది మరియు సాంప్రదాయ ఆయుర్వేద సూత్రాలపై ఆధారపడి ఉంది.",
    },
    "kn": {
        "name": "Kannada",
        "native": "ಕನ್ನಡ",
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ಆಯುರ್ವಾಣಿ, ನಿಮ್ಮ ಆಯುರ್ವೇದ ಆರೋಗ್ಯ ಸಹಾಯಕ.",
        "disclaimer": "ಈ ಮಾರ್ಗದರ್ಶನವು ಶೈಕ್ಷಣಿಕವಾಗಿದೆ ಮತ್ತು ಸಾಂಪ್ರದಾಯಿಕ ಆಯುರ್ವೇದ ತತ್ವಗಳನ್ನು ಆಧರಿಸಿದೆ.",
    },
    "ml": {
        "name": "Malayalam",
        "native": "മലയാളം",
        "greeting": "നമസ്കാരം! ഞാൻ ആയുർവാണി, നിങ്ങളുടെ ആയുർവേദ ആരോഗ്യ സഹായി.",
        "disclaimer": "ഈ മാർഗ്ഗനിർദ്ദേശം വിദ്യാഭ്യാസപരമാണ്, പരമ്പരാഗത ആയുർവേദ തത്ത്വങ്ങളെ അടിസ്ഥാനമാക്കിയതാണ്.",
    },
    "bn": {
        "name": "Bengali",
        "native": "বাংলা",
        "greeting": "নমস্কার! আমি আয়ুর্বাণী, আপনার আয়ুর্বেদিক স্বাস্থ্য সহায়ক।",
        "disclaimer": "এই নির্দেশিকা শিক্ষামূলক এবং ঐতিহ্যবাহী আয়ুর্বেদিক নীতির উপর ভিত্তি করে।",
    },
    "mr": {
        "name": "Marathi",
        "native": "मराठी",
        "greeting": "नमस्कार! मी आयुर्वाणी, तुमची आयुर्वेदिक आरोग्य सहाय्यक.",
        "disclaimer": "हे मार्गदर्शन शैक्षणिक आहे आणि पारंपरिक आयुर्वेदिक तत्त्वांवर आधारित आहे.",
    },
    "gu": {
        "name": "Gujarati",
        "native": "ગુજરાતી",
        "greeting": "નમસ્તે! હું આયુર્વાણી છું, તમારી આયુર્વેદિક સ્વાસ્થ્ય સહાયક.",
        "disclaimer": "આ માર્ગદર્શન શૈક્ષણિક છે અને પરંપરાગત આયુર્વેદિક સિદ્ધાંતો પર આધારિત છે.",
    },
    "pa": {
        "name": "Punjabi",
        "native": "ਪੰਜਾਬੀ",
        "greeting": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਆਯੁਰਵਾਣੀ ਹਾਂ, ਤੁਹਾਡੀ ਆਯੁਰਵੈਦਿਕ ਸਿਹਤ ਸਹਾਇਕ।",
        "disclaimer": "ਇਹ ਮਾਰਗਦਰਸ਼ਨ ਵਿਦਿਅਕ ਹੈ ਅਤੇ ਰਵਾਇਤੀ ਆਯੁਰਵੈਦਿਕ ਸਿਧਾਂਤਾਂ 'ਤੇ ਅਧਾਰਤ ਹੈ।",
    },
    "or": {
        "name": "Odia",
        "native": "ଓଡ଼ିଆ",
        "greeting": "ନମସ୍କାର! ମୁଁ ଆୟୁର୍ବାଣୀ, ଆପଣଙ୍କ ଆୟୁର୍ବେଦିକ ସ୍ୱାସ୍ଥ୍ୟ ସହାୟକ।",
        "disclaimer": "ଏହି ମାର୍ଗଦର୍ଶନ ଶିକ୍ଷାମୂଳକ ଏବଂ ପାରମ୍ପରିକ ଆୟୁର୍ବେଦିକ ସିଦ୍ଧାନ୍ତ ଉପରେ ଆଧାରିତ।",
    },
    "ur": {
        "name": "Urdu",
        "native": "اردو",
        "greeting": "آداب! میں آیورْوانی ہوں، آپ کی آیورویدک صحت معاون۔",
        "disclaimer": "یہ رہنمائی تعلیمی ہے اور روایتی آیورویدک اصولوں پر مبنی ہے۔",
    },
    "sa": {
        "name": "Sanskrit",
        "native": "संस्कृतम्",
        "greeting": "नमस्ते! अहम् आयुर्वाणी, भवतः आयुर्वेदीय-स्वास्थ्य-सहायिका।",
        "disclaimer": "एतत् मार्गदर्शनं शैक्षिकम् अस्ति, पारम्परिक-आयुर्वेद-सिद्धान्तेषु आधारितम्।",
    },
}


class MultilingualHelper:
    """Helpers for multilingual support across all agents."""

    def get_language_name(self, code: str) -> str:
        lang = LANGUAGE_MAP.get(code, LANGUAGE_MAP["en"])
        return lang["name"]

    def get_native_name(self, code: str) -> str:
        lang = LANGUAGE_MAP.get(code, LANGUAGE_MAP["en"])
        return lang["native"]

    def get_greeting(self, code: str) -> str:
        lang = LANGUAGE_MAP.get(code, LANGUAGE_MAP["en"])
        return lang["greeting"]

    def get_disclaimer(self, code: str) -> str:
        lang = LANGUAGE_MAP.get(code, LANGUAGE_MAP["en"])
        return lang["disclaimer"]

    def get_language_instruction(self, code: str) -> str:
        lang_name = self.get_language_name(code)
        if code == "en":
            return "Respond in English."
        return (
            f"Respond entirely in {lang_name} ({self.get_native_name(code)}). "
            f"Use {lang_name} script. Transliterate Sanskrit terms into {lang_name}."
        )

    def is_supported(self, code: str) -> bool:
        return code in LANGUAGE_MAP

    def get_supported_languages(self) -> Dict[str, str]:
        return {code: info["name"] for code, info in LANGUAGE_MAP.items()}

    def detect_language_hint(self, text: str) -> Optional[str]:
        """Basic script-based language hint (not full detection)."""
        if not text:
            return None

        # Unicode block ranges for Indic scripts
        SCRIPT_RANGES = {
            "hi": ("\u0900", "\u097F"),  # Devanagari
            "bn": ("\u0980", "\u09FF"),  # Bengali
            "pa": ("\u0A00", "\u0A7F"),  # Gurmukhi
            "gu": ("\u0A80", "\u0AFF"),  # Gujarati
            "or": ("\u0B00", "\u0B7F"),  # Oriya
            "ta": ("\u0B80", "\u0BFF"),  # Tamil
            "te": ("\u0C00", "\u0C7F"),  # Telugu
            "kn": ("\u0C80", "\u0CFF"),  # Kannada
            "ml": ("\u0D00", "\u0D7F"),  # Malayalam
            "ur": ("\u0600", "\u06FF"),  # Arabic (Urdu)
        }

        for char in text:
            for lang_code, (start, end) in SCRIPT_RANGES.items():
                if start <= char <= end:
                    return lang_code

        # Default: if mostly ASCII, assume English
        ascii_count = sum(1 for c in text if c.isascii() and c.isalpha())
        if ascii_count > len(text) * 0.5:
            return "en"

        return None