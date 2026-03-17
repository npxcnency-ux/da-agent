"""
Tests for ComplexityScorer - LLM-driven complexity scoring with rule-based fallback
"""
import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from lib.complexity_scorer import ComplexityResult, ComplexityScorer


class TestComplexityResult:
    """Test ComplexityResult dataclass"""

    def test_complexity_result_creation(self):
        """Test creating ComplexityResult with all fields"""
        result = ComplexityResult(
            score=5,
            reasoning="Medium complexity task",
            mode="collab"
        )
        assert result.score == 5
        assert result.reasoning == "Medium complexity task"
        assert result.mode == "collab"


class TestRuleBasedScoring:
    """Test rule-based complexity scoring"""

    def test_rule_based_simple_task(self):
        """Test simple task scores <= 3 and mode = 'auto'"""
        scorer = ComplexityScorer()

        # Simple aggregation on single file
        structured_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "aggregation",
            "metrics": ["SUM(revenue)"],
            "business_rules": []
        }

        result = scorer.score_with_rules(structured_req)

        assert isinstance(result, ComplexityResult)
        assert result.score <= 3
        assert result.mode == "auto"
        assert "simple" in result.reasoning.lower() or "low" in result.reasoning.lower()

    def test_rule_based_medium_task(self):
        """Test medium complexity task scores 3-7 and mode = 'collab'"""
        scorer = ComplexityScorer()

        # Multi-file JOIN with statistical analysis
        structured_req = {
            "data_sources": ["sales.csv", "customers.csv"],
            "analysis_type": "statistical",
            "metrics": ["AVG(revenue)", "STDDEV(revenue)"],
            "joins": [{"left": "sales", "right": "customers", "on": "customer_id"}],
            "business_rules": ["revenue > 1000"]
        }

        result = scorer.score_with_rules(structured_req)

        assert isinstance(result, ComplexityResult)
        assert 3 <= result.score <= 7
        assert result.mode == "collab"
        assert "medium" in result.reasoning.lower() or "moderate" in result.reasoning.lower()

    def test_rule_based_complex_task(self):
        """Test complex task scores > 7 and mode = 'assist'"""
        scorer = ComplexityScorer()

        # Complex transformation with modeling and cross-department logic
        structured_req = {
            "data_sources": ["sales.csv", "customers.csv", "products.csv", "regions.csv"],
            "analysis_type": "modeling",
            "metrics": ["predicted_revenue", "customer_lifetime_value"],
            "joins": [
                {"left": "sales", "right": "customers", "on": "customer_id"},
                {"left": "sales", "right": "products", "on": "product_id"},
                {"left": "customers", "right": "regions", "on": "region_id"}
            ],
            "transformations": ["pivot", "normalize", "feature_engineering"],
            "business_rules": [
                "revenue_adjusted_for_returns",
                "cross_department_allocation",
                "multi_touch_attribution"
            ]
        }

        result = scorer.score_with_rules(structured_req)

        assert isinstance(result, ComplexityResult)
        assert result.score > 7
        assert result.mode == "assist"
        assert "complex" in result.reasoning.lower() or "high" in result.reasoning.lower()

    def test_rule_based_data_complexity_scoring(self):
        """Test data complexity component scoring"""
        scorer = ComplexityScorer()

        # Single file = 1 point
        simple_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}
        simple_result = scorer.score_with_rules(simple_req)

        # Multiple files with JOIN = 2 points
        join_req = {
            "data_sources": ["sales.csv", "customers.csv"],
            "joins": [{"left": "sales", "right": "customers"}],
            "analysis_type": "aggregation"
        }
        join_result = scorer.score_with_rules(join_req)

        # Complex transformations = 3 points
        transform_req = {
            "data_sources": ["sales.csv", "customers.csv", "products.csv"],
            "transformations": ["pivot", "window_functions"],
            "analysis_type": "aggregation"
        }
        transform_result = scorer.score_with_rules(transform_req)

        # Verify increasing complexity
        assert simple_result.score < join_result.score < transform_result.score

    def test_rule_based_analytical_method_scoring(self):
        """Test analytical method complexity component"""
        scorer = ComplexityScorer()

        # Aggregation = 1 point
        agg_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}
        agg_result = scorer.score_with_rules(agg_req)

        # Statistical = 3 points
        stat_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "statistical",
            "metrics": ["STDDEV", "CORRELATION"]
        }
        stat_result = scorer.score_with_rules(stat_req)

        # Modeling = 4 points
        model_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "modeling",
            "metrics": ["predicted_value"]
        }
        model_result = scorer.score_with_rules(model_req)

        # Verify increasing complexity
        assert agg_result.score < stat_result.score < model_result.score

    def test_rule_based_business_logic_scoring(self):
        """Test business logic complexity component"""
        scorer = ComplexityScorer()

        # No business rules = 1 point
        simple_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "aggregation",
            "business_rules": []
        }
        simple_result = scorer.score_with_rules(simple_req)

        # Single business rule = 2 points
        rule_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "aggregation",
            "business_rules": ["revenue > 1000"]
        }
        rule_result = scorer.score_with_rules(rule_req)

        # Multiple complex rules = 3 points
        complex_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "aggregation",
            "business_rules": [
                "cross_department_allocation",
                "multi_touch_attribution",
                "revenue_adjusted_for_returns"
            ]
        }
        complex_result = scorer.score_with_rules(complex_req)

        # Verify increasing complexity
        assert simple_result.score <= rule_result.score <= complex_result.score


class TestLLMScoring:
    """Test LLM-based complexity scoring"""

    @patch('lib.complexity_scorer.Anthropic')
    def test_llm_scoring_success(self, mock_anthropic_class):
        """Test successful LLM scoring"""
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock the message response
        mock_response = Mock()
        mock_response.content = [
            Mock(text='{"score": 6, "reasoning": "Multi-file analysis with statistical methods", "suggested_mode": "collab"}')
        ]
        mock_client.messages.create.return_value = mock_response

        scorer = ComplexityScorer(api_key="test-api-key")

        structured_req = {
            "data_sources": ["sales.csv", "customers.csv"],
            "analysis_type": "statistical",
            "metrics": ["AVG(revenue)", "CORRELATION"]
        }

        result = scorer.score_with_llm(structured_req)

        assert isinstance(result, ComplexityResult)
        assert result.score == 6
        assert result.mode == "collab"
        assert "Multi-file" in result.reasoning

        # Verify API was called correctly
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-6"
        assert call_kwargs["max_tokens"] == 1024

    @patch('lib.complexity_scorer.Anthropic')
    def test_llm_scoring_with_system_prompt(self, mock_anthropic_class):
        """Test LLM scoring includes proper system prompt"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [
            Mock(text='{"score": 5, "reasoning": "Test", "suggested_mode": "collab"}')
        ]
        mock_client.messages.create.return_value = mock_response

        scorer = ComplexityScorer(api_key="test-api-key")
        structured_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}

        scorer.score_with_llm(structured_req)

        # Verify system prompt includes scoring rubric
        call_kwargs = mock_client.messages.create.call_args[1]
        messages = call_kwargs["messages"]

        # Check that the user message contains the structured request
        assert any("data_sources" in str(msg) for msg in messages)

    @patch('lib.complexity_scorer.Anthropic')
    def test_llm_scoring_invalid_json(self, mock_anthropic_class):
        """Test LLM scoring handles invalid JSON response"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.content = [Mock(text='This is not valid JSON')]
        mock_client.messages.create.return_value = mock_response

        scorer = ComplexityScorer(api_key="test-api-key")
        structured_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}

        # Should raise an exception or return None
        with pytest.raises(json.JSONDecodeError):
            scorer.score_with_llm(structured_req)

    @patch('lib.complexity_scorer.Anthropic')
    def test_llm_scoring_api_error(self, mock_anthropic_class):
        """Test LLM scoring handles API errors"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock API error
        mock_client.messages.create.side_effect = Exception("API connection failed")

        scorer = ComplexityScorer(api_key="test-api-key")
        structured_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}

        # Should raise exception
        with pytest.raises(Exception):
            scorer.score_with_llm(structured_req)

    def test_llm_scoring_without_api_key(self):
        """Test LLM scoring fails gracefully without API key"""
        scorer = ComplexityScorer()  # No API key
        structured_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}

        # Should raise ValueError or similar
        with pytest.raises((ValueError, AttributeError)):
            scorer.score_with_llm(structured_req)


class TestMainScoringMethod:
    """Test main score() method with fallback logic"""

    @patch('lib.complexity_scorer.Anthropic')
    def test_score_uses_llm_when_available(self, mock_anthropic_class):
        """Test score() uses LLM when available"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [
            Mock(text='{"score": 7, "reasoning": "LLM scoring result", "suggested_mode": "collab"}')
        ]
        mock_client.messages.create.return_value = mock_response

        scorer = ComplexityScorer(api_key="test-api-key")
        structured_req = {"data_sources": ["sales.csv"], "analysis_type": "aggregation"}

        result = scorer.score(structured_req)

        assert result.score == 7
        assert "LLM scoring result" in result.reasoning
        assert mock_client.messages.create.called

    @patch('lib.complexity_scorer.Anthropic')
    def test_fallback_to_rules_on_llm_error(self, mock_anthropic_class):
        """Test fallback to rule-based scoring when LLM fails"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock LLM failure
        mock_client.messages.create.side_effect = Exception("API error")

        scorer = ComplexityScorer(api_key="test-api-key")

        # Simple task
        structured_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "aggregation",
            "metrics": ["SUM(revenue)"],
            "business_rules": []
        }

        result = scorer.score(structured_req)

        # Should get rule-based result
        assert isinstance(result, ComplexityResult)
        assert result.score <= 3
        assert result.mode == "auto"
        assert "rule-based" in result.reasoning.lower() or "fallback" in result.reasoning.lower()

    def test_score_uses_rules_without_api_key(self):
        """Test score() uses rules when no API key provided"""
        scorer = ComplexityScorer()  # No API key

        structured_req = {
            "data_sources": ["sales.csv"],
            "analysis_type": "aggregation",
            "metrics": ["SUM(revenue)"],
            "business_rules": []
        }

        result = scorer.score(structured_req)

        # Should get rule-based result
        assert isinstance(result, ComplexityResult)
        assert result.score <= 3
        assert result.mode == "auto"


class TestModeSelection:
    """Test score-to-mode mapping"""

    def test_mode_selection_logic(self):
        """Test _get_mode_for_score maps scores correctly"""
        scorer = ComplexityScorer()

        # Auto mode: score < 3
        assert scorer._get_mode_for_score(1) == "auto"
        assert scorer._get_mode_for_score(2) == "auto"

        # Collab mode: 3 <= score <= 7
        assert scorer._get_mode_for_score(3) == "collab"
        assert scorer._get_mode_for_score(5) == "collab"
        assert scorer._get_mode_for_score(7) == "collab"

        # Assist mode: score > 7
        assert scorer._get_mode_for_score(8) == "assist"
        assert scorer._get_mode_for_score(9) == "assist"
        assert scorer._get_mode_for_score(10) == "assist"

    def test_mode_selection_boundary_cases(self):
        """Test mode selection at exact boundaries"""
        scorer = ComplexityScorer()

        # Test boundary between auto and collab
        assert scorer._get_mode_for_score(2) == "auto"
        assert scorer._get_mode_for_score(3) == "collab"

        # Test boundary between collab and assist
        assert scorer._get_mode_for_score(7) == "collab"
        assert scorer._get_mode_for_score(8) == "assist"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_structured_request(self):
        """Test handling of empty structured request"""
        scorer = ComplexityScorer()

        result = scorer.score_with_rules({})

        # Should still return a valid result with minimum score
        assert isinstance(result, ComplexityResult)
        assert result.score >= 1
        assert result.mode in ["auto", "collab", "assist"]

    def test_missing_optional_fields(self):
        """Test handling of structured request with missing optional fields"""
        scorer = ComplexityScorer()

        # Minimal structured request
        structured_req = {
            "data_sources": ["sales.csv"]
        }

        result = scorer.score_with_rules(structured_req)

        assert isinstance(result, ComplexityResult)
        assert 1 <= result.score <= 10
        assert result.mode in ["auto", "collab", "assist"]

    def test_score_bounds(self):
        """Test that scores are always within 1-10 range"""
        scorer = ComplexityScorer()

        # Test various structured requests
        test_cases = [
            {"data_sources": ["sales.csv"]},
            {"data_sources": ["a.csv", "b.csv", "c.csv", "d.csv", "e.csv"]},
            {"data_sources": ["sales.csv"], "analysis_type": "modeling"},
        ]

        for req in test_cases:
            result = scorer.score_with_rules(req)
            assert 1 <= result.score <= 10, f"Score {result.score} out of bounds for {req}"
