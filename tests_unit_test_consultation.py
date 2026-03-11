"""Unit tests for the consultation router and agent."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from api.models.schemas import Language, ConsultationType


@pytest.fixture
def mock_nova():
    with patch("services.nova_service.NovaLiteService") as mock:
        instance = mock.return_value
        instance.generate = AsyncMock(return_value='{"response": "Namaste! Based on your symptoms, this appears to be a Vata imbalance.", "recommendations": ["Drink warm water"], "follow_up_questions": ["How long have you had this?"], "dosha_indication": "vata", "confidence": 0.87}')
        instance.assess_dosha = AsyncMock(return_value={
            "primary_dosha": "vata",
            "secondary_dosha": "pitta",
            "prakriti_description": "You have a Vata-Pitta constitution.",
            "characteristics": ["Creative", "Sharp intellect"],
            "dietary_guidelines": ["Warm foods", "Regular meals"],
            "lifestyle_recommendations": ["Routine schedule"],
        })
        yield instance


@pytest.fixture
def mock_knowledge_base():
    with patch("services.knowledge_base.KnowledgeBaseService") as mock:
        instance = mock.return_value
        instance.search = AsyncMock(return_value=[
            {"content": "Ashwagandha reduces Vata.", "source": "Charaka Samhita", "score": 0.92, "metadata": {}},
        ])
        instance.initialize = AsyncMock()
        yield instance


class TestAyurvedaAgent:
    @pytest.mark.asyncio
    async def test_consult_returns_response(self, mock_nova, mock_knowledge_base):
        from agents.ayurveda_agent import AyurvedaAgent

        agent = AyurvedaAgent()
        agent.nova = mock_nova

        result = await agent.consult(
            message="I have headaches and insomnia",
            session_id="test-session",
            user_id="test-user",
            language="en",
            knowledge_base=mock_knowledge_base,
        )

        assert "response" in result
        assert isinstance(result["response"], str)
        mock_nova.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_symptoms_returns_structure(self, mock_nova, mock_knowledge_base):
        from agents.ayurveda_agent import AyurvedaAgent

        mock_nova.generate = AsyncMock(return_value='{"analysis": "Vata imbalance", "possible_imbalances": ["Vata"], "recommended_herbs": [], "dietary_suggestions": ["Warm soups"], "yoga_recommendations": ["Shavasana"], "severity_assessment": "mild", "disclaimer": "Consult a doctor."}')

        agent = AyurvedaAgent()
        agent.nova = mock_nova

        result = await agent.analyze_symptoms(
            symptoms=["headache", "insomnia"],
            duration="2 weeks",
            severity=6,
            medical_history=None,
            language="en",
            knowledge_base=mock_knowledge_base,
        )

        assert "analysis" in result
        assert "possible_imbalances" in result


class TestMultilingualHelper:
    def test_get_language_name(self):
        from utils.multilingual import MultilingualHelper

        helper = MultilingualHelper()
        assert helper.get_language_name("hi") == "Hindi"
        assert helper.get_language_name("ta") == "Tamil"
        assert helper.get_language_name("xx") == "English"  # fallback

    def test_get_greeting(self):
        from utils.multilingual import MultilingualHelper

        helper = MultilingualHelper()
        greeting = helper.get_greeting("hi")
        assert "आयुर्वाणी" in greeting

    def test_detect_language_hint(self):
        from utils.multilingual import MultilingualHelper

        helper = MultilingualHelper()
        assert helper.detect_language_hint("नमस्ते") == "hi"
        assert helper.detect_language_hint("Hello world") == "en"


class TestAyurvedaKnowledge:
    def test_get_herb(self):
        from utils.ayurveda_knowledge import AyurvedaKnowledge

        kb = AyurvedaKnowledge()
        herb = kb.get_herb("ashwagandha")
        assert herb is not None
        assert herb.name == "Ashwagandha"

    def test_get_herbs_for_dosha(self):
        from utils.ayurveda_knowledge import AyurvedaKnowledge

        kb = AyurvedaKnowledge()
        herbs = kb.get_herbs_for_dosha("vata")
        assert len(herbs) > 0

    def test_get_foods_for_dosha(self):
        from utils.ayurveda_knowledge import AyurvedaKnowledge

        kb = AyurvedaKnowledge()
        foods = kb.get_foods_for_dosha("pitta")
        assert "favor" in foods
        assert "avoid" in foods
        assert len(foods["favor"]) > 0

    def test_prakriti_questions_loaded(self):
        from utils.ayurveda_knowledge import AyurvedaKnowledge

        kb = AyurvedaKnowledge()
        assert len(kb.prakriti_questions) >= 7