"""Additional tests for AITutor edge cases and fallbacks."""

from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from opengov_earlymathematics.ai.tutor import AITutor, MathProblemGenerator


@patch("opengov_earlymathematics.ai.tutor.OpenAI")
def test_generate_problem_non_json_content(mock_openai):
    # OpenAI returns plain text, not JSON
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Solve 2+2"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    gen = MathProblemGenerator()
    res = gen.generate_problem("addition", 3, "easy")
    assert res["problem"]
    assert "solution" in res and "explanation" in res


def test_help_with_response_error_fallback():
    tutor = AITutor("student_fallback")
    with patch.object(tutor.client.chat.completions, "create", side_effect=Exception("api")):
        reply = tutor.help_with("How do I add numbers?")
        assert "Let me think about that" in reply
        # Conversation history should include the user question and assistant fallback
        assert any(msg["role"] == "user" for msg in tutor.conversation_history)
        assert any(msg["role"] == "assistant" for msg in tutor.conversation_history)


def test_help_with_success_path():
    tutor = AITutor("student_success")
    with patch.object(tutor.client.chat.completions, "create") as mock_create:
        mock_resp = Mock()
        mock_resp.choices = [Mock()]
        mock_resp.choices[0].message.content = "Here's how to add numbers..."
        mock_create.return_value = mock_resp
        reply = tutor.help_with("What's 2+2?")
        assert "Here's how" in reply
        assert any(m["role"] == "assistant" for m in tutor.conversation_history)


@patch("opengov_earlymathematics.ai.tutor.OpenAI")
def test_start_session_greeting_fallback(mock_openai):
    # Force greeting generation to raise
    mock_openai.return_value.chat.completions.create.side_effect = Exception("api")
    tutor = AITutor("student_greet")
    out = tutor.start_session("algebra")
    assert "session_id" in out and out["topic"] == "algebra"
    assert "learn about algebra" in out["greeting"]


def test_hint_fallback_path():
    tutor = AITutor("student_hint")
    # Request out-of-range hint level to hit fallback return
    hint = tutor.provide_hint("prob1", hint_level=99)
    assert "work through this together" in hint


def test_explain_concept_fallback():
    tutor = AITutor("student_explain")
    with patch.object(tutor.client.chat.completions, "create", side_effect=Exception("api")):
        text = tutor.explain_concept("fractions", 5)
        assert "Let me explain fractions" in text
