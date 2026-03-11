"""Integration tests for the AyurVani API."""

import pytest
import requests
import time

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module", autouse=True)
def wait_for_server():
    """Wait for the backend to be ready."""
    for _ in range(20):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=3)
            if r.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(2)
    pytest.fail("Backend did not start in time")


class TestHealthEndpoints:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_root(self):
        r = requests.get(f"{BASE_URL}/")
        data = r.json()
        assert data["name"] == "AyurVani"
        assert "nova_models" in data


class TestConsultation:
    def test_chat_endpoint(self):
        payload = {
            "user_id": "integration-test",
            "message": "What herbs help with stress?",
            "language": "en",
            "consultation_type": "initial",
        }
        r = requests.post(f"{BASE_URL}/api/consultation/chat", json=payload, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data
        assert "response" in data
        assert len(data["response"]) > 0

    def test_symptoms_endpoint(self):
        payload = {
            "user_id": "integration-test",
            "symptoms": ["headache", "fatigue", "poor sleep"],
            "duration": "1 week",
            "severity": 5,
            "language": "en",
        }
        r = requests.post(f"{BASE_URL}/api/consultation/symptoms", json=payload, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert "analysis" in data

    def test_dosha_assessment(self):
        payload = {
            "user_id": "integration-test",
            "responses": {
                "body_frame": "vata",
                "skin_type": "vata",
                "appetite": "pitta",
                "digestion": "vata",
                "sleep": "vata",
                "temperament": "vata",
                "stress": "vata",
            },
            "language": "en",
        }
        r = requests.post(f"{BASE_URL}/api/consultation/dosha-assessment", json=payload, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert "primary_dosha" in data

    def test_history_endpoint(self):
        r = requests.get(f"{BASE_URL}/api/consultation/history/integration-test")
        assert r.status_code == 200


class TestMultimodal:
    def test_search_endpoint(self):
        payload = {"query": "Ashwagandha benefits for stress", "top_k": 3}
        r = requests.post(f"{BASE_URL}/api/multimodal/search", json=payload, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "results" in data