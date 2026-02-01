from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.dto.classification_response import ClassificationResponse
from app.dto.intent_response import IntentResponse
from app.dto.sentiment_response import SentimentResponse
from app.dto.summary_response import SummaryResponse
from app.main import app


@pytest.fixture
def mock_ai_service():
    with patch("app.controller.ai_controller.ai_service") as mock_service:
        yield mock_service


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestClassifyEndpoint:
    def test_valid_text_returns_classification(self, client, mock_ai_service):
        mock_ai_service.classify_text.return_value = ClassificationResponse(
            labels=["technology", "healthcare", "AI"],
            primaryCategory="technology",
            confidence=0.95,
        )

        response = client.post("/api/ai/classify", json={"text": "Artificial intelligence is transforming healthcare."})

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["technology", "healthcare", "AI"]
        assert data["primaryCategory"] == "technology"
        assert data["confidence"] == 0.95
        mock_ai_service.classify_text.assert_called_once_with("Artificial intelligence is transforming healthcare.")

    def test_empty_labels(self, client, mock_ai_service):
        mock_ai_service.classify_text.return_value = ClassificationResponse(
            labels=[],
            primaryCategory="unknown",
            confidence=0.5,
        )

        response = client.post("/api/ai/classify", json={"text": "Some ambiguous text"})

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == []
        assert data["primaryCategory"] == "unknown"
        assert data["confidence"] == 0.5

    def test_service_exception_returns_500(self, client, mock_ai_service):
        mock_ai_service.classify_text.side_effect = RuntimeError("AI service unavailable")

        response = client.post("/api/ai/classify", json={"text": "Test text"})

        assert response.status_code == 500


class TestSentimentEndpoint:
    def test_positive_sentiment(self, client, mock_ai_service):
        mock_ai_service.analyze_sentiment.return_value = SentimentResponse(
            overallSentiment="positive",
            sentimentScore=0.85,
            emotions=["joy", "excitement"],
            confidence=0.92,
        )

        response = client.post("/api/ai/sentiment", json={"text": "I love this product! It's amazing!"})

        assert response.status_code == 200
        data = response.json()
        assert data["overallSentiment"] == "positive"
        assert data["sentimentScore"] == 0.85
        assert data["emotions"] == ["joy", "excitement"]
        assert data["confidence"] == 0.92
        mock_ai_service.analyze_sentiment.assert_called_once_with("I love this product! It's amazing!")

    def test_negative_sentiment(self, client, mock_ai_service):
        mock_ai_service.analyze_sentiment.return_value = SentimentResponse(
            overallSentiment="negative",
            sentimentScore=-0.75,
            emotions=["disappointment", "frustration"],
            confidence=0.88,
        )

        response = client.post("/api/ai/sentiment", json={"text": "This is terrible. I'm very disappointed."})

        assert response.status_code == 200
        data = response.json()
        assert data["overallSentiment"] == "negative"
        assert data["sentimentScore"] == -0.75
        assert data["emotions"][0] == "disappointment"

    def test_neutral_sentiment(self, client, mock_ai_service):
        mock_ai_service.analyze_sentiment.return_value = SentimentResponse(
            overallSentiment="neutral",
            sentimentScore=0.0,
            emotions=[],
            confidence=0.95,
        )

        response = client.post("/api/ai/sentiment", json={"text": "The meeting is scheduled for 3 PM."})

        assert response.status_code == 200
        data = response.json()
        assert data["overallSentiment"] == "neutral"
        assert data["sentimentScore"] == 0.0
        assert data["emotions"] == []

    def test_service_exception_returns_500(self, client, mock_ai_service):
        mock_ai_service.analyze_sentiment.side_effect = RuntimeError("Failed to parse AI response")

        response = client.post("/api/ai/sentiment", json={"text": "Test text"})

        assert response.status_code == 500


class TestSummarizeEndpoint:
    def test_valid_text_returns_summary(self, client, mock_ai_service):
        input_text = (
            "Artificial intelligence (AI) is intelligence demonstrated by machines. "
            "AI research has been defined as the field of study of intelligent agents. "
            "Machine learning is a subset of AI that enables systems to learn from data."
        )
        mock_ai_service.summarize_text.return_value = SummaryResponse(
            summary="AI is machine intelligence, with machine learning being a key subset that enables data-driven learning.",
            keyPoints=[
                "AI is intelligence demonstrated by machines",
                "AI research studies intelligent agents",
                "Machine learning enables learning from data",
            ],
            wordCount=15,
        )

        response = client.post("/api/ai/summarize", json={"text": input_text})

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] != ""
        assert len(data["keyPoints"]) == 3
        assert data["wordCount"] == 15
        mock_ai_service.summarize_text.assert_called_once_with(input_text)

    def test_short_text_minimal_summary(self, client, mock_ai_service):
        mock_ai_service.summarize_text.return_value = SummaryResponse(
            summary="A simple greeting.",
            keyPoints=["Greeting message"],
            wordCount=3,
        )

        response = client.post("/api/ai/summarize", json={"text": "Hello world."})

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "A simple greeting."
        assert len(data["keyPoints"]) == 1
        assert data["wordCount"] == 3

    def test_service_exception_returns_500(self, client, mock_ai_service):
        mock_ai_service.summarize_text.side_effect = RuntimeError("AI service timeout")

        response = client.post("/api/ai/summarize", json={"text": "Test text"})

        assert response.status_code == 500


class TestIntentEndpoint:
    def test_question_intent(self, client, mock_ai_service):
        mock_ai_service.detect_intent.return_value = IntentResponse(
            primaryIntent="find_restaurant",
            secondaryIntents=["location_search", "recommendation_request"],
            intentCategory="question",
            confidence=0.88,
        )

        response = client.post("/api/ai/intent", json={"text": "Where is the nearest restaurant?"})

        assert response.status_code == 200
        data = response.json()
        assert data["primaryIntent"] == "find_restaurant"
        assert data["secondaryIntents"] == ["location_search", "recommendation_request"]
        assert data["intentCategory"] == "question"
        assert data["confidence"] == 0.88
        mock_ai_service.detect_intent.assert_called_once_with("Where is the nearest restaurant?")

    def test_command_intent(self, client, mock_ai_service):
        mock_ai_service.detect_intent.return_value = IntentResponse(
            primaryIntent="control_device",
            secondaryIntents=["smart_home", "lighting"],
            intentCategory="command",
            confidence=0.95,
        )

        response = client.post("/api/ai/intent", json={"text": "Turn off the lights"})

        assert response.status_code == 200
        data = response.json()
        assert data["primaryIntent"] == "control_device"
        assert data["intentCategory"] == "command"
        assert data["confidence"] == 0.95

    def test_request_intent(self, client, mock_ai_service):
        mock_ai_service.detect_intent.return_value = IntentResponse(
            primaryIntent="request_document",
            secondaryIntents=["email", "file_transfer"],
            intentCategory="request",
            confidence=0.90,
        )

        response = client.post("/api/ai/intent", json={"text": "Please send me the report"})

        assert response.status_code == 200
        data = response.json()
        assert data["primaryIntent"] == "request_document"
        assert data["intentCategory"] == "request"

    def test_statement_intent(self, client, mock_ai_service):
        mock_ai_service.detect_intent.return_value = IntentResponse(
            primaryIntent="share_information",
            secondaryIntents=["weather", "observation"],
            intentCategory="statement",
            confidence=0.85,
        )

        response = client.post("/api/ai/intent", json={"text": "The weather is nice today."})

        assert response.status_code == 200
        data = response.json()
        assert data["primaryIntent"] == "share_information"
        assert data["intentCategory"] == "statement"

    def test_service_exception_returns_500(self, client, mock_ai_service):
        mock_ai_service.detect_intent.side_effect = RuntimeError("Connection refused")

        response = client.post("/api/ai/intent", json={"text": "Test text"})

        assert response.status_code == 500


class TestRoutesEndpoint:
    def test_get_routes_returns_routing_table(self, client, mock_ai_service):
        response = client.get("/api/ai/routes")

        assert response.status_code == 200
        data = response.json()
        assert "classify" in data
        assert "sentiment" in data
        assert "summarize" in data
        assert "intent" in data

    def test_get_routes_returns_correct_models(self, client, mock_ai_service):
        response = client.get("/api/ai/routes")

        assert response.status_code == 200
        data = response.json()
        assert data["classify"] == "gemma3:4b"
        assert data["sentiment"] == "ministral-3:3b"
        assert data["summarize"] == "ministral-3:8b"
        assert data["intent"] == "gemma3:12b"


class TestRequestValidation:
    def test_empty_text(self, client, mock_ai_service):
        mock_ai_service.analyze_sentiment.return_value = SentimentResponse(
            overallSentiment="neutral",
            sentimentScore=0.0,
            emotions=[],
            confidence=0.0,
        )

        response = client.post("/api/ai/sentiment", json={"text": ""})

        assert response.status_code == 200
        assert response.json()["overallSentiment"] == "neutral"

    def test_long_text(self, client, mock_ai_service):
        long_text = "A" * 10000
        mock_ai_service.summarize_text.return_value = SummaryResponse(
            summary="A very long repetitive text.",
            keyPoints=["Contains repeated character A"],
            wordCount=5,
        )

        response = client.post("/api/ai/summarize", json={"text": long_text})

        assert response.status_code == 200
        assert "summary" in response.json()

    def test_special_characters(self, client, mock_ai_service):
        text = "Hello! @#$%^&*() Test 123"
        mock_ai_service.detect_intent.return_value = IntentResponse(
            primaryIntent="greeting",
            secondaryIntents=["test"],
            intentCategory="statement",
            confidence=0.7,
        )

        response = client.post("/api/ai/intent", json={"text": text})

        assert response.status_code == 200
        assert response.json()["primaryIntent"] == "greeting"

    def test_invalid_json_returns_422(self, client, mock_ai_service):
        response = client.post(
            "/api/ai/classify",
            content="{ invalid json }",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422
