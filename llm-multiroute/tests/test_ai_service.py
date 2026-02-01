from unittest.mock import MagicMock

import pytest

from app.router.model_router import ModelRouter, TaskType
from app.service.ai_service import AIService


@pytest.fixture
def mock_http_client():
    return MagicMock()


@pytest.fixture
def mock_router():
    router = MagicMock(spec=ModelRouter)
    router.get_model.side_effect = lambda t: {
        TaskType.CLASSIFY: "gemma3:4b",
        TaskType.SENTIMENT: "ministral-3:3b",
        TaskType.SUMMARIZE: "ministral-3:8b",
        TaskType.INTENT: "gemma3:12b",
    }[t]
    return router


@pytest.fixture
def ai_service(mock_http_client, mock_router):
    return AIService(http_client=mock_http_client, router=mock_router)


def _setup_chat_response(mock_http_client, response_text: str):
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": {"content": response_text}}
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post.return_value = mock_response


class TestClassifyText:
    def test_valid_json_response(self, ai_service, mock_http_client):
        json_response = '{"labels": ["technology", "AI"], "primaryCategory": "technology", "confidence": 0.95}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.classify_text("AI is transforming healthcare")

        assert result is not None
        assert result.labels == ["technology", "AI"]
        assert result.primaryCategory == "technology"
        assert result.confidence == 0.95

    def test_uses_classify_model(self, ai_service, mock_http_client):
        json_response = '{"labels": ["test"], "primaryCategory": "test", "confidence": 0.9}'
        _setup_chat_response(mock_http_client, json_response)

        ai_service.classify_text("test text")

        call_args = mock_http_client.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert body["model"] == "gemma3:4b"

    def test_markdown_json_code_block(self, ai_service, mock_http_client):
        json_response = '```json\n{"labels": ["news"], "primaryCategory": "news", "confidence": 0.8}\n```'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.classify_text("Breaking news article")

        assert result is not None
        assert result.labels == ["news"]
        assert result.primaryCategory == "news"

    def test_plain_code_block(self, ai_service, mock_http_client):
        json_response = '```\n{"labels": ["sports"], "primaryCategory": "sports", "confidence": 0.9}\n```'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.classify_text("Football game results")

        assert result is not None
        assert result.primaryCategory == "sports"

    def test_invalid_json_raises_exception(self, ai_service, mock_http_client):
        _setup_chat_response(mock_http_client, "This is not valid JSON")

        with pytest.raises(RuntimeError, match="Failed to parse AI response as JSON"):
            ai_service.classify_text("some text")

    def test_empty_labels(self, ai_service, mock_http_client):
        json_response = '{"labels": [], "primaryCategory": "unknown", "confidence": 0.5}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.classify_text("ambiguous text")

        assert result.labels == []


class TestAnalyzeSentiment:
    def test_positive_sentiment(self, ai_service, mock_http_client):
        json_response = '{"overallSentiment": "positive", "sentimentScore": 0.85, "emotions": ["joy", "excitement"], "confidence": 0.92}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.analyze_sentiment("I love this!")

        assert result is not None
        assert result.overallSentiment == "positive"
        assert result.sentimentScore == 0.85
        assert result.emotions == ["joy", "excitement"]
        assert result.confidence == 0.92

    def test_uses_sentiment_model(self, ai_service, mock_http_client):
        json_response = '{"overallSentiment": "neutral", "sentimentScore": 0.0, "emotions": [], "confidence": 0.5}'
        _setup_chat_response(mock_http_client, json_response)

        ai_service.analyze_sentiment("test text")

        call_args = mock_http_client.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert body["model"] == "ministral-3:3b"

    def test_negative_sentiment(self, ai_service, mock_http_client):
        json_response = '{"overallSentiment": "negative", "sentimentScore": -0.75, "emotions": ["anger", "disappointment"], "confidence": 0.88}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.analyze_sentiment("This is terrible!")

        assert result.overallSentiment == "negative"
        assert result.sentimentScore == -0.75
        assert "anger" in result.emotions

    def test_neutral_sentiment_empty_emotions(self, ai_service, mock_http_client):
        json_response = '{"overallSentiment": "neutral", "sentimentScore": 0.0, "emotions": [], "confidence": 0.95}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.analyze_sentiment("The meeting is at 3 PM.")

        assert result.overallSentiment == "neutral"
        assert result.sentimentScore == 0.0
        assert result.emotions == []

    def test_markdown_wrapped_response(self, ai_service, mock_http_client):
        json_response = '```json\n{"overallSentiment": "positive", "sentimentScore": 0.9, "emotions": ["happiness"], "confidence": 0.95}\n```'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.analyze_sentiment("Great news!")

        assert result.overallSentiment == "positive"


class TestSummarizeText:
    def test_valid_summary(self, ai_service, mock_http_client):
        json_response = '{"summary": "AI transforms healthcare through improved diagnostics.", "keyPoints": ["AI improves diagnosis", "Reduces costs", "Enhances care"], "wordCount": 6}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.summarize_text("Long article about AI in healthcare...")

        assert result is not None
        assert result.summary == "AI transforms healthcare through improved diagnostics."
        assert len(result.keyPoints) == 3
        assert result.wordCount == 6

    def test_uses_summarize_model(self, ai_service, mock_http_client):
        json_response = '{"summary": "Test.", "keyPoints": ["point"], "wordCount": 1}'
        _setup_chat_response(mock_http_client, json_response)

        ai_service.summarize_text("test text")

        call_args = mock_http_client.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert body["model"] == "ministral-3:8b"

    def test_single_key_point(self, ai_service, mock_http_client):
        json_response = '{"summary": "Brief summary.", "keyPoints": ["Main point"], "wordCount": 2}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.summarize_text("Short text")

        assert len(result.keyPoints) == 1
        assert result.keyPoints[0] == "Main point"

    def test_empty_key_points(self, ai_service, mock_http_client):
        json_response = '{"summary": "Too short to summarize.", "keyPoints": [], "wordCount": 4}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.summarize_text("Hi")

        assert result.keyPoints == []

    def test_malformed_json_raises_exception(self, ai_service, mock_http_client):
        _setup_chat_response(mock_http_client, "{summary: missing quotes}")

        with pytest.raises(RuntimeError, match="Failed to parse AI response as JSON"):
            ai_service.summarize_text("some text")


class TestDetectIntent:
    def test_question_intent(self, ai_service, mock_http_client):
        json_response = '{"primaryIntent": "find_restaurant", "secondaryIntents": ["location_search", "recommendation"], "intentCategory": "question", "confidence": 0.88}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.detect_intent("Where is the nearest restaurant?")

        assert result is not None
        assert result.primaryIntent == "find_restaurant"
        assert result.secondaryIntents == ["location_search", "recommendation"]
        assert result.intentCategory == "question"
        assert result.confidence == 0.88

    def test_uses_intent_model(self, ai_service, mock_http_client):
        json_response = '{"primaryIntent": "test", "secondaryIntents": [], "intentCategory": "statement", "confidence": 0.5}'
        _setup_chat_response(mock_http_client, json_response)

        ai_service.detect_intent("test text")

        call_args = mock_http_client.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert body["model"] == "gemma3:12b"

    def test_command_intent(self, ai_service, mock_http_client):
        json_response = '{"primaryIntent": "turn_off_lights", "secondaryIntents": ["smart_home"], "intentCategory": "command", "confidence": 0.95}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.detect_intent("Turn off the lights")

        assert result.primaryIntent == "turn_off_lights"
        assert result.intentCategory == "command"

    def test_request_intent(self, ai_service, mock_http_client):
        json_response = '{"primaryIntent": "send_document", "secondaryIntents": [], "intentCategory": "request", "confidence": 0.90}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.detect_intent("Please send me the report")

        assert result.intentCategory == "request"
        assert result.secondaryIntents == []

    def test_statement_intent(self, ai_service, mock_http_client):
        json_response = '{"primaryIntent": "share_observation", "secondaryIntents": ["weather"], "intentCategory": "statement", "confidence": 0.85}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.detect_intent("The weather is nice today")

        assert result.intentCategory == "statement"

    def test_markdown_code_block(self, ai_service, mock_http_client):
        json_response = '```json\n{"primaryIntent": "greeting", "secondaryIntents": [], "intentCategory": "statement", "confidence": 0.99}\n```'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.detect_intent("Hello!")

        assert result.primaryIntent == "greeting"
        assert result.confidence == 0.99


class TestAuthorizationHeader:
    def test_api_key_sends_bearer_header(self, mock_http_client):
        json_response = '{"labels": ["test"], "primaryCategory": "test", "confidence": 0.9}'
        _setup_chat_response(mock_http_client, json_response)

        service = AIService(http_client=mock_http_client)
        service.api_key = "test-api-key"
        service.classify_text("test text")

        call_args = mock_http_client.post.call_args
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        assert headers["Authorization"] == "Bearer test-api-key"

    def test_no_api_key_sends_no_auth_header(self, mock_http_client):
        json_response = '{"labels": ["test"], "primaryCategory": "test", "confidence": 0.9}'
        _setup_chat_response(mock_http_client, json_response)

        service = AIService(http_client=mock_http_client)
        service.api_key = ""
        service.classify_text("test text")

        call_args = mock_http_client.post.call_args
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        assert "Authorization" not in headers


class TestModelRoutingIntegration:
    def test_each_task_uses_different_model(self, mock_http_client, mock_router):
        service = AIService(http_client=mock_http_client, router=mock_router)

        tasks_and_models = [
            (lambda: service.classify_text("text"), "gemma3:4b"),
            (lambda: service.analyze_sentiment("text"), "ministral-3:3b"),
            (lambda: service.summarize_text("text"), "ministral-3:8b"),
            (lambda: service.detect_intent("text"), "gemma3:12b"),
        ]

        responses = [
            '{"labels": ["t"], "primaryCategory": "t", "confidence": 0.9}',
            '{"overallSentiment": "neutral", "sentimentScore": 0.0, "emotions": [], "confidence": 0.5}',
            '{"summary": "s", "keyPoints": ["p"], "wordCount": 1}',
            '{"primaryIntent": "i", "secondaryIntents": [], "intentCategory": "statement", "confidence": 0.5}',
        ]

        for (task_fn, expected_model), response_text in zip(tasks_and_models, responses):
            _setup_chat_response(mock_http_client, response_text)
            task_fn()

            call_args = mock_http_client.post.call_args
            body = call_args.kwargs.get("json") or call_args[1].get("json")
            assert body["model"] == expected_model, f"Expected model {expected_model}, got {body['model']}"


class TestJsonParsingEdgeCases:
    def test_extra_whitespace(self, ai_service, mock_http_client):
        json_response = '  \n\n  {"labels": ["test"], "primaryCategory": "test", "confidence": 0.9}  \n\n  '
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.classify_text("test")

        assert result.primaryCategory == "test"

    def test_extra_fields_ignored(self, ai_service, mock_http_client):
        json_response = '{"labels": ["test"], "primaryCategory": "test", "confidence": 0.9, "extraField": "ignored"}'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.classify_text("test")

        assert result.primaryCategory == "test"

    def test_only_closing_code_block(self, ai_service, mock_http_client):
        json_response = '{"overallSentiment": "neutral", "sentimentScore": 0.0, "emotions": [], "confidence": 0.5}```'
        _setup_chat_response(mock_http_client, json_response)

        result = ai_service.analyze_sentiment("test")

        assert result.overallSentiment == "neutral"

    def test_prompt_contains_expected_elements(self, ai_service, mock_http_client):
        json_response = '{"labels": ["test"], "primaryCategory": "test", "confidence": 0.9}'
        _setup_chat_response(mock_http_client, json_response)

        ai_service.classify_text("Test input text")

        call_args = mock_http_client.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        prompt = body["messages"][0]["content"]
        assert "Test input text" in prompt
        assert "Respond with ONLY valid JSON" in prompt
        assert "labels" in prompt
        assert "primaryCategory" in prompt
        assert "confidence" in prompt
