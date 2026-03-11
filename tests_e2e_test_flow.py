"""End-to-end test — full consultation flow."""

import pytest
import requests

BASE_URL = "http://localhost:8000"


class TestFullConsultationFlow:
    """Simulate a complete user journey."""

    def test_full_flow(self):
        user_id = "e2e-test-user"

        # 1. Dosha assessment
        dosha_resp = requests.post(
            f"{BASE_URL}/api/consultation/dosha-assessment",
            json={
                "user_id": user_id,
                "responses": {
                    "body_frame": "pitta",
                    "skin_type": "pitta",
                    "appetite": "pitta",
                    "digestion": "pitta",
                    "sleep": "pitta",
                    "temperament": "pitta",
                    "stress": "pitta",
                },
                "language": "en",
            },
            timeout=60,
        )
        assert dosha_resp.status_code == 200
        dosha_data = dosha_resp.json()
        assert "primary_dosha" in dosha_data
        primary = dosha_data["primary_dosha"]

        # 2. Consultation mentioning the dosha
        chat_resp = requests.post(
            f"{BASE_URL}/api/consultation/chat",
            json={
                "user_id": user_id,
                "message": f"I have a {primary} constitution. I've been experiencing acid reflux and skin rashes. What Ayurvedic approach would you recommend?",
                "language": "en",
                "consultation_type": "initial",
            },
            timeout=60,
        )
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()
        session_id = chat_data["session_id"]
        assert len(chat_data["response"]) > 50

        # 3. Follow-up in the same session
        followup_resp = requests.post(
            f"{BASE_URL}/api/consultation/chat",
            json={
                "user_id": user_id,
                "session_id": session_id,
                "message": "Can you suggest specific herbs and a daily routine?",
                "language": "en",
                "consultation_type": "follow_up",
            },
            timeout=60,
        )
        assert followup_resp.status_code == 200
        assert len(followup_resp.json()["response"]) > 50

        # 4. Search knowledge base
        search_resp = requests.post(
            f"{BASE_URL}/api/multimodal/search",
            json={"query": f"herbs for {primary} imbalance", "top_k": 3},
            timeout=30,
        )
        assert search_resp.status_code == 200
        assert search_resp.json()["total_results"] > 0