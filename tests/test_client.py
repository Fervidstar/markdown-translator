# tests/test_client.py
import pytest
from unittest.mock import Mock, patch
import requests
from api.client import APIClient, APIError
from config.models import APIConfig


class TestAPIError:
    def test_error_creation(self):
        error = APIError("Test error", status_code=500)
        assert str(error) == "API error (500): Test error"


class TestAPIClient:
    @pytest.fixture
    def sample_config(self):
        return APIConfig(
            base_url="https://test.api.com/v1",
            model="test-model",
            temperature=0.7,
            max_tokens=1024
        )

    @pytest.fixture
    def client(self, sample_config):
        return APIClient(config=sample_config, api_key="test-key")

    def test_client_initialization(self, sample_config):
        client = APIClient(config=sample_config, api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://test.api.com/v1"

    def test_client_missing_api_key(self, sample_config):
        with pytest.raises(ValueError, match="API key is required"):
            APIClient(config=sample_config, api_key=None)

    @patch("api.client.requests.post")
    def test_translate_success(self, mock_post, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Translated content here"}}
            ]
        }
        mock_post.return_value = mock_response

        result = client.translate("Hello, World!", "Prompt here")
        assert result == "Translated content here"
        mock_post.assert_called_once()

    @patch("api.client.requests.post")
    def test_translate_with_retry(self, mock_post, client):
        # First call fails with ConnectionError (RequestException), second succeeds
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Success after retry"}}
            ]
        }

        # Use ConnectionError which is a subclass of RequestException
        mock_post.side_effect = [
            requests.exceptions.ConnectionError("Network error"),
            mock_response
        ]

        result = client.translate("Test content", "Prompt", retry=True)
        assert result == "Success after retry"
        assert mock_post.call_count == 2

    @patch("api.client.requests.post")
    def test_translate_api_error(self, mock_post, client):
        # Create mock HTTPError response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.json.return_value = {
            "error": {"message": "Rate limit exceeded"}
        }
        # Make raise_for_status raise HTTPError with status 429
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            client.translate("Test content", "Prompt")
        assert exc_info.value.status_code == 429

    @patch("api.client.requests.post")
    def test_translate_invalid_response(self, mock_post, client):
        mock_response = Mock()
        # Make json() raise ValueError which gets wrapped as "Invalid response format"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            client.translate("Test content", "Prompt")
        assert "Invalid response format" in str(exc_info.value)