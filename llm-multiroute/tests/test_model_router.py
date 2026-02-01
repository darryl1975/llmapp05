from unittest.mock import patch

# import pytest

from app.router.model_router import ModelRouter, TaskType


class TestModelRouter:
    def test_get_model_classify(self):
        router = ModelRouter()
        model = router.get_model(TaskType.CLASSIFY)
        assert model == "gemma3:4b"

    def test_get_model_sentiment(self):
        router = ModelRouter()
        model = router.get_model(TaskType.SENTIMENT)
        assert model == "ministral-3:3b"

    def test_get_model_summarize(self):
        router = ModelRouter()
        model = router.get_model(TaskType.SUMMARIZE)
        assert model == "ministral-3:8b"

    def test_get_model_intent(self):
        router = ModelRouter()
        model = router.get_model(TaskType.INTENT)
        assert model == "gemma3:12b"

    def test_get_routes_returns_all_tasks(self):
        router = ModelRouter()
        routes = router.get_routes()
        assert len(routes) == 4
        assert "classify" in routes
        assert "sentiment" in routes
        assert "summarize" in routes
        assert "intent" in routes

    def test_get_routes_returns_correct_models(self):
        router = ModelRouter()
        routes = router.get_routes()
        assert routes["classify"] == "gemma3:4b"
        assert routes["sentiment"] == "ministral-3:3b"
        assert routes["summarize"] == "ministral-3:8b"
        assert routes["intent"] == "gemma3:12b"

    def test_each_task_has_unique_model(self):
        router = ModelRouter()
        routes = router.get_routes()
        models = list(routes.values())
        assert len(models) == len(set(models)), "Each task should route to a different model"


class TestModelRouterCustomConfig:
    @patch("app.router.model_router.settings")
    def test_custom_model_assignments(self, mock_settings):
        mock_settings.OLLAMA_MODEL_CLASSIFY = "custom-classify"
        mock_settings.OLLAMA_MODEL_SENTIMENT = "custom-sentiment"
        mock_settings.OLLAMA_MODEL_SUMMARIZE = "custom-summarize"
        mock_settings.OLLAMA_MODEL_INTENT = "custom-intent"

        router = ModelRouter()

        assert router.get_model(TaskType.CLASSIFY) == "custom-classify"
        assert router.get_model(TaskType.SENTIMENT) == "custom-sentiment"
        assert router.get_model(TaskType.SUMMARIZE) == "custom-summarize"
        assert router.get_model(TaskType.INTENT) == "custom-intent"

    @patch("app.router.model_router.settings")
    def test_custom_routes_dict(self, mock_settings):
        mock_settings.OLLAMA_MODEL_CLASSIFY = "model-a"
        mock_settings.OLLAMA_MODEL_SENTIMENT = "model-b"
        mock_settings.OLLAMA_MODEL_SUMMARIZE = "model-c"
        mock_settings.OLLAMA_MODEL_INTENT = "model-d"

        router = ModelRouter()
        routes = router.get_routes()

        assert routes == {
            "classify": "model-a",
            "sentiment": "model-b",
            "summarize": "model-c",
            "intent": "model-d",
        }


class TestTaskType:
    def test_task_type_values(self):
        assert TaskType.CLASSIFY.value == "classify"
        assert TaskType.SENTIMENT.value == "sentiment"
        assert TaskType.SUMMARIZE.value == "summarize"
        assert TaskType.INTENT.value == "intent"

    def test_task_type_count(self):
        assert len(TaskType) == 4
