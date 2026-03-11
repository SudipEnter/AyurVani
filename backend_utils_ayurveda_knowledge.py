"""
Static Ayurveda knowledge base — herbs, doshas, therapies, yoga.
Used for quick look-ups without hitting the vector store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Herb:
    name: str
    sanskrit_name: str
    rasa: str
    guna: str
    virya: str
    vipaka: str
    dosha_effect: str
    benefits: List[str]
    dosage: str
    contraindications: List[str] = field(default_factory=list)


@dataclass
class YogaPractice:
    name: str
    sanskrit_name: str
    category: str
    dosha_effect: str
    benefits: List[str]
    contraindications: List[str] = field(default_factory=list)
    instructions: str = ""


class AyurvedaKnowledge:
    """In-memory Ayurveda reference data."""

    def __init__(self):
        self.herbs = self._load_herbs()
        self.yoga_practices = self._load_yoga()
        self.dosha_foods = self._load_dosha_foods()
        self.prakriti_questions = self._load_prakriti_questions()

    def get_herb(self, name: str) -> Optional[Herb]:
        name_lower = name.lower()
        for herb in self.herbs:
            if name_lower in herb.name.lower() or name_lower in herb.sanskrit_name.lower():
                return herb
        return None

    def get_herbs_for_dosha(self, dosha: str) -> List[Herb]:
        return [h for h in self.herbs if dosha.lower() in h.dosha_effect.lower()]

    def get_yoga_for_dosha(self, dosha: str) -> List[YogaPractice]:
        return [y for y in self.yoga_practices if dosha.lower() in y.dosha_effect.lower()]

    def get_foods_for_dosha(self, dosha: str) -> Dict[str, List[str]]:
        return self.dosha_foods.get(dosha.lower(), {"favor": [], "avoid": []})

    def _load_herbs(self) -> List[Herb]:
        return [
            Herb(
                name="Ashwagandha",
                sanskrit_name="Ashwagandha (Withania somnifera)",
                rasa="Tikta, Kashaya",
                guna="Laghu, Snigdha",
                virya="Ushna",
                vipaka="Madhura",
                dosha_effect="Reduces Vata and Kapha",
                benefits=[
                    "Adaptogenic — reduces stress and cortisol",
                    "Enhances strength and stamina",
                    "Supports immune function",
                    "Promotes restful sleep",
                    "Improves cognitive function",
                ],
                dosage="3-6g powder with warm milk, or 300-600mg extract twice daily",
                contraindications=["Pregnancy", "Hyperthyroidism", "High Ama"],
            ),
            Herb(
                name="Turmeric",
                sanskrit_name="Haridra (Curcuma longa)",
                rasa="Tikta, Katu",
                guna="Ruksha, Laghu",
                virya="Ushna",
                vipaka="Katu",
                dosha_effect="Balances all three doshas, especially Kapha",
                benefits=[
                    "Powerful anti-inflammatory",
                    "Antioxidant",
                    "Supports liver detoxification",
                    "Promotes healthy skin",
                    "Enhances digestion",
                ],
                dosage="1-3g powder with warm water or milk, add black pepper",
                contraindications=["Gallstones", "Blood-thinning medication"],
            ),
            Herb(
                name="Tulsi",
                sanskrit_name="Tulasi (Ocimum sanctum)",
                rasa="Tikta, Katu",
                guna="Laghu, Ruksha",
                virya="Ushna",
                vipaka="Katu",
                dosha_effect="Reduces Kapha and Vata",
                benefits=[
                    "Respiratory support",
                    "Immune modulator",
                    "Adaptogenic",
                    "Antimicrobial",
                ],
                dosage="3-5g powder or 10-20ml juice daily",
                contraindications=["Blood-thinning medication"],
            ),
            Herb(
                name="Brahmi",
                sanskrit_name="Brahmi (Bacopa monnieri)",
                rasa="Tikta, Kashaya, Madhura",
                guna="Laghu, Sara",
                virya="Sheeta",
                vipaka="Madhura",
                dosha_effect="Balances Pitta and Vata",
                benefits=[
                    "Enhances memory and concentration",
                    "Calms the nervous system",
                    "Supports healthy sleep",
                    "Neuroprotective",
                ],
                dosage="2-4g powder or 5-10ml juice daily",
                contraindications=["May increase Kapha in excess"],
            ),
            Herb(
                name="Triphala",
                sanskrit_name="Triphala",
                rasa="All five tastes except Lavana",
                guna="Laghu, Ruksha",
                virya="Anushna",
                vipaka="Madhura",
                dosha_effect="Tridoshic — balances all three doshas",
                benefits=[
                    "Gentle bowel regulation",
                    "Digestive support",
                    "Detoxification",
                    "Antioxidant",
                    "Eye health",
                ],
                dosage="3-6g powder with warm water before bed",
                contraindications=["Pregnancy", "Diarrhea"],
            ),
            Herb(
                name="Guduchi",
                sanskrit_name="Guduchi (Tinospora cordifolia)",
                rasa="Tikta, Kashaya",
                guna="Laghu, Snigdha",
                virya="Ushna",
                vipaka="Madhura",
                dosha_effect="Tridoshic",
                benefits=[
                    "Immunomodulator",
                    "Antipyretic",
                    "Liver protective",
                    "Anti-inflammatory",
                    "Blood purifier",
                ],
                dosage="3-6g powder or 20-30ml juice daily",
                contraindications=["Autoimmune conditions — consult practitioner"],
            ),
            Herb(
                name="Shatavari",
                sanskrit_name="Shatavari (Asparagus racemosus)",
                rasa="Madhura, Tikta",
                guna="Guru, Snigdha",
                virya="Sheeta",
                vipaka="Madhura",
                dosha_effect="Reduces Vata and Pitta",
                benefits=[
                    "Female reproductive tonic",
                    "Galactagogue",
                    "Digestive soother",
                    "Adaptogenic",
                    "Anti-aging Rasayana",
                ],
                dosage="3-6g powder with milk or ghee",
                contraindications=["Kidney disorders", "Excess Kapha conditions"],
            ),
            Herb(
                name="Neem",
                sanskrit_name="Nimba (Azadirachta indica)",
                rasa="Tikta, Kashaya",
                guna="Laghu, Ruksha",
                virya="Sheeta",
                vipaka="Katu",
                dosha_effect="Reduces Pitta and Kapha",
                benefits=[
                    "Blood purifier",
                    "Skin disorders",
                    "Antimicrobial",
                    "Antiparasitic",
                    "Supports dental health",
                ],
                dosage="1-3g powder or neem leaf tea",
                contraindications=["Pregnancy", "Infertility treatments", "Excess Vata"],
            ),
        ]

    def _load_yoga(self) -> List[YogaPractice]:
        return [
            YogaPractice(
                name="Surya Namaskar",
                sanskrit_name="Surya Namaskar",
                category="asana",
                dosha_effect="Balances all doshas; especially Kapha",
                benefits=["Full-body workout", "Improves circulation", "Stimulates Agni"],
                instructions="Perform 6-12 rounds at sunrise on empty stomach.",
            ),
            YogaPractice(
                name="Nadi Shodhana",
                sanskrit_name="Nadi Shodhana Pranayama",
                category="pranayama",
                dosha_effect="Balances Vata; calms Pitta",
                benefits=["Calms mind", "Reduces anxiety", "Improves focus"],
                instructions="Alternate nostrils using right thumb and ring finger. 5-10 min.",
            ),
            YogaPractice(
                name="Bhujangasana",
                sanskrit_name="Bhujangasana",
                category="asana",
                dosha_effect="Reduces Kapha; balances Vata",
                benefits=["Opens chest", "Strengthens spine", "Stimulates digestion"],
                contraindications=["Pregnancy", "Herniated disc"],
            ),
            YogaPractice(
                name="Shavasana",
                sanskrit_name="Shavasana",
                category="asana",
                dosha_effect="Reduces Vata and Pitta",
                benefits=["Deep relaxation", "Reduces blood pressure", "Relieves insomnia"],
                instructions="Lie flat, close eyes, relax each body part. 5-15 min.",
            ),
            YogaPractice(
                name="Kapalabhati",
                sanskrit_name="Kapalabhati",
                category="pranayama",
                dosha_effect="Reduces Kapha strongly",
                benefits=["Energizes", "Clears sinuses", "Stimulates Agni", "Detoxifies"],
                contraindications=["Pregnancy", "Hypertension", "Heart disease", "Epilepsy"],
            ),
            YogaPractice(
                name="Viparita Karani",
                sanskrit_name="Viparita Karani",
                category="asana",
                dosha_effect="Reduces Vata and Pitta",
                benefits=["Relieves tired legs", "Calms nervous system", "Improves sleep"],
                instructions="Legs up the wall, hips close to wall. Hold 5-15 min.",
                contraindications=["Glaucoma", "Serious neck injury"],
            ),
        ]

    def _load_dosha_foods(self) -> Dict[str, Dict[str, List[str]]]:
        return {
            "vata": {
                "favor": [
                    "Warm, cooked, moist foods",
                    "Sweet, sour, salty tastes",
                    "Ghee, sesame oil",
                    "Rice, wheat, oats",
                    "Cooked vegetables",
                    "Warm milk, soups, stews",
                    "Sweet fruits — bananas, grapes, mangoes",
                    "Nuts and seeds",
                ],
                "avoid": [
                    "Cold, raw, dry foods",
                    "Bitter, pungent, astringent tastes",
                    "Dried fruits in excess",
                    "Raw salads",
                    "Carbonated beverages",
                    "Excessive caffeine",
                ],
            },
            "pitta": {
                "favor": [
                    "Cool, refreshing foods",
                    "Sweet, bitter, astringent tastes",
                    "Coconut oil, ghee, olive oil",
                    "Basmati rice, wheat, barley, oats",
                    "Sweet fruits — melons, pears, grapes",
                    "Green leafy vegetables, cucumber",
                    "Dairy — milk, ghee, butter",
                    "Cooling herbs — coriander, fennel, mint",
                ],
                "avoid": [
                    "Spicy, sour, salty foods",
                    "Fermented foods, vinegar",
                    "Red meat, fried foods",
                    "Excessive alcohol, coffee",
                    "Tomatoes, citrus in excess",
                    "Hot peppers, garlic in excess",
                ],
            },
            "kapha": {
                "favor": [
                    "Light, warm, dry foods",
                    "Pungent, bitter, astringent tastes",
                    "Honey (uncooked) as sweetener",
                    "Barley, millet, corn, buckwheat",
                    "Light fruits — apples, pears, pomegranates",
                    "Spices — ginger, black pepper, turmeric",
                    "Legumes — mung beans, lentils",
                    "Steamed vegetables",
                ],
                "avoid": [
                    "Heavy, oily, cold foods",
                    "Sweet, sour, salty tastes in excess",
                    "Dairy — especially cold milk, ice cream",
                    "Fried foods, excessive nuts",
                    "Wheat, rice in excess",
                    "Sweet fruits — bananas, dates, figs",
                    "Excess sleep after meals",
                ],
            },
        }

    def _load_prakriti_questions(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "body_frame",
                "question": "What best describes your body frame?",
                "vata": "Thin, light, tall or short, difficulty gaining weight",
                "pitta": "Medium build, well-proportioned, moderate weight",
                "kapha": "Large frame, sturdy, gains weight easily",
            },
            {
                "id": "skin_type",
                "question": "How would you describe your skin?",
                "vata": "Dry, rough, thin, cool, darkish",
                "pitta": "Warm, oily, fair, prone to rashes or acne",
                "kapha": "Thick, oily, smooth, cool, pale",
            },
            {
                "id": "hair_type",
                "question": "What is your hair like?",
                "vata": "Dry, frizzy, thin, dark",
                "pitta": "Fine, soft, early graying or thinning, reddish",
                "kapha": "Thick, oily, wavy, lustrous, dark",
            },
            {
                "id": "appetite",
                "question": "How is your appetite?",
                "vata": "Irregular, sometimes strong, sometimes absent",
                "pitta": "Strong, irritable if meals are missed",
                "kapha": "Steady but slow, can skip meals easily",
            },
            {
                "id": "digestion",
                "question": "How is your digestion?",
                "vata": "Irregular, gas, bloating, constipation",
                "pitta": "Strong, acid reflux, loose stools possible",
                "kapha": "Slow, heavy feeling after meals",
            },
            {
                "id": "sleep_pattern",
                "question": "How do you sleep?",
                "vata": "Light, interrupted, difficulty falling asleep",
                "pitta": "Moderate, vivid dreams, wake feeling warm",
                "kapha": "Deep, heavy, hard to wake up, prolonged",
            },
            {
                "id": "temperament",
                "question": "What is your general mental temperament?",
                "vata": "Quick thinking, creative, anxious, restless",
                "pitta": "Sharp intellect, ambitious, irritable, focused",
                "kapha": "Calm, steady, loyal, slow to change, attached",
            },
            {
                "id": "stress_response",
                "question": "How do you respond to stress?",
                "vata": "Anxiety, worry, fear, insomnia",
                "pitta": "Anger, frustration, criticism, intensity",
                "kapha": "Withdrawal, comfort eating, lethargy, denial",
            },
            {
                "id": "climate_preference",
                "question": "What climate do you prefer?",
                "vata": "Warm, humid, dislike cold and wind",
                "pitta": "Cool, well-ventilated, dislike heat",
                "kapha": "Warm, dry, dislike cold and damp",
            },
            {
                "id": "energy_pattern",
                "question": "How is your energy throughout the day?",
                "vata": "Comes in bursts, tires quickly, variable",
                "pitta": "Moderate, sustained until overheated or frustrated",
                "kapha": "Slow to start, steady endurance once going",
            },
        ]