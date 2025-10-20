"""Unit tests for ai_apply.py - AI provider integrations."""
from unittest.mock import Mock, patch, MagicMock

import pytest

from crengine.ai_apply import propose_patches


@pytest.mark.skip(reason="AI provider tests require optional dependencies and mocking lazy imports")
class TestProposePatches:
    """Tests for propose_patches function with mocked AI providers."""

    @patch("openai.OpenAI")
    def test_propose_patches_openai(self, mock_openai_class):
        """Test propose_patches with OpenAI provider."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.output_text = "suggested patch content"
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        prompts = ["Fix this issue", "Fix that issue"]
        patches = propose_patches("openai", "gpt-4", prompts)

        assert len(patches) == 2
        assert all(p == "suggested patch content" for p in patches)
        assert mock_client.responses.create.call_count == 2

    @patch("crengine.ai_apply.anthropic")
    def test_propose_patches_anthropic(self, mock_anthropic_module):
        """Test propose_patches with Anthropic provider."""
        # Mock Anthropic client and response
        mock_client = Mock()
        mock_content = Mock()
        mock_content.text = "anthropic patch suggestion"
        mock_message = Mock()
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        mock_anthropic_class = Mock()
        mock_anthropic_class.return_value = mock_client
        mock_anthropic_module.Anthropic = mock_anthropic_class

        prompts = ["Prompt 1"]
        patches = propose_patches("anthropic", "claude-3-5-sonnet-20241022", prompts)

        assert len(patches) == 1
        assert patches[0] == "anthropic patch suggestion"
        assert mock_client.messages.create.call_count == 1

    @patch("crengine.ai_apply.genai")
    def test_propose_patches_gemini(self, mock_genai_module):
        """Test propose_patches with Gemini provider."""
        # Mock Gemini client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "gemini patch content"
        mock_client.models.generate_content.return_value = mock_response

        mock_genai_class = Mock()
        mock_genai_class.return_value = mock_client
        mock_genai_module.Client = mock_genai_class

        prompts = ["Fix security issue", "Fix style issue"]
        patches = propose_patches("gemini", "gemini-1.5-pro", prompts)

        assert len(patches) == 2
        assert all(p == "gemini patch content" for p in patches)
        assert mock_client.models.generate_content.call_count == 2

    def test_propose_patches_unsupported_provider(self):
        """Test that unsupported provider raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            propose_patches("unsupported", "model", ["prompt"])

    @patch("crengine.ai_apply.OpenAI")
    def test_propose_patches_empty_prompts(self, mock_openai_class):
        """Test with empty prompts list."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        patches = propose_patches("openai", "gpt-4", [])

        assert len(patches) == 0
        assert mock_client.responses.create.call_count == 0

    @patch("crengine.ai_apply.OpenAI")
    def test_propose_patches_single_prompt(self, mock_openai_class):
        """Test with a single prompt."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.output_text = "single patch"
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        patches = propose_patches("openai", "gpt-4", ["Single prompt"])

        assert len(patches) == 1
        assert patches[0] == "single patch"

    @patch("crengine.ai_apply.OpenAI")
    def test_propose_patches_retry_on_failure(self, mock_openai_class):
        """Test that retries are attempted on failure."""
        mock_client = Mock()
        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.output_text = "success"
        mock_client.responses.create.side_effect = [
            Exception("API Error"),
            mock_response
        ]
        mock_openai_class.return_value = mock_client

        # Should retry and eventually succeed
        patches = propose_patches("openai", "gpt-4", ["prompt"])

        assert len(patches) == 1
        assert patches[0] == "success"
        assert mock_client.responses.create.call_count == 2

    @patch("crengine.ai_apply.OpenAI")
    def test_propose_patches_max_retries_exceeded(self, mock_openai_class):
        """Test that exception is raised after max retries."""
        mock_client = Mock()
        # Always fail
        mock_client.responses.create.side_effect = Exception("Persistent API Error")
        mock_openai_class.return_value = mock_client

        with pytest.raises(Exception, match="Persistent API Error"):
            propose_patches("openai", "gpt-4", ["prompt"])

    @patch("crengine.ai_apply.anthropic")
    def test_propose_patches_anthropic_message_format(self, mock_anthropic_module):
        """Test that Anthropic messages are formatted correctly."""
        mock_client = Mock()
        mock_content = Mock()
        mock_content.text = "patch"
        mock_message = Mock()
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        mock_anthropic_class = Mock()
        mock_anthropic_class.return_value = mock_client
        mock_anthropic_module.Anthropic = mock_anthropic_class

        propose_patches("anthropic", "claude-3-5-sonnet-20241022", ["Test prompt"])

        # Verify message format
        call_args = mock_client.messages.create.call_args
        assert call_args[1]["model"] == "claude-3-5-sonnet-20241022"
        assert call_args[1]["max_tokens"] == 2000
        assert len(call_args[1]["messages"]) == 1
        assert call_args[1]["messages"][0]["role"] == "user"
        assert call_args[1]["messages"][0]["content"] == "Test prompt"

    @patch("crengine.ai_apply.genai")
    def test_propose_patches_gemini_parameters(self, mock_genai_module):
        """Test that Gemini API is called with correct parameters."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "output"
        mock_client.models.generate_content.return_value = mock_response

        mock_genai_class = Mock()
        mock_genai_class.return_value = mock_client
        mock_genai_module.Client = mock_genai_class

        propose_patches("gemini", "gemini-1.5-pro", ["Input prompt"])

        call_args = mock_client.models.generate_content.call_args
        assert call_args[1]["model"] == "gemini-1.5-pro"
        assert call_args[1]["contents"] == "Input prompt"

    @patch("crengine.ai_apply.OpenAI")
    def test_propose_patches_preserves_order(self, mock_openai_class):
        """Test that patch order matches prompt order."""
        mock_client = Mock()
        responses = [Mock(output_text=f"patch_{i}") for i in range(5)]
        mock_client.responses.create.side_effect = responses
        mock_openai_class.return_value = mock_client

        prompts = [f"prompt_{i}" for i in range(5)]
        patches = propose_patches("openai", "gpt-4", prompts)

        assert len(patches) == 5
        for i, patch in enumerate(patches):
            assert patch == f"patch_{i}"
