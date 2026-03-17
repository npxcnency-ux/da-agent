"""
ComplexityScorer - LLM-driven complexity scoring with rule-based fallback

Evaluates analysis tasks and assigns complexity scores (1-10) to determine
execution mode (auto/collab/assist).
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class ComplexityResult:
    """Result of complexity scoring"""
    score: int  # 1-10
    reasoning: str  # Explanation of the score
    mode: str  # "auto", "collab", or "assist"


class ComplexityScorer:
    """
    Complexity scorer with LLM-based scoring and rule-based fallback

    Scoring Rubric (Rule-based):
    - Data complexity (0-3 pts): Single file (0), Multi-file (1), Multi-file JOIN (2), Complex transformation (3)
    - Analytical method (1-4 pts): Aggregation (1), Multi-dimensional (2), Statistical (3), Modeling (4)
    - Business logic (0-3 pts): Standard metrics (0), Business rules (1), Cross-department (3)

    Mode Mapping:
    - score < 3: "auto" (fully automated)
    - 3 <= score <= 7: "collab" (collaborative)
    - score > 7: "assist" (assistant mode)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ComplexityScorer

        Args:
            api_key: Optional Anthropic API key for LLM-based scoring
        """
        self.api_key = api_key
        self.client = None

        if api_key and ANTHROPIC_AVAILABLE:
            self.client = Anthropic(api_key=api_key)

    def score(self, structured_req: Dict[str, Any]) -> ComplexityResult:
        """
        Score complexity using LLM if available, fall back to rules

        Args:
            structured_req: Structured request dictionary

        Returns:
            ComplexityResult with score, reasoning, and mode
        """
        # Try LLM scoring first if available
        if self.client:
            try:
                return self.score_with_llm(structured_req)
            except Exception:
                # Fall back to rule-based scoring on any error
                result = self.score_with_rules(structured_req)
                # Add note about fallback
                result.reasoning = f"Rule-based fallback: {result.reasoning}"
                return result

        # Use rule-based scoring if no LLM available
        return self.score_with_rules(structured_req)

    def score_with_llm(self, structured_req: Dict[str, Any]) -> ComplexityResult:
        """
        Score complexity using Claude API

        Args:
            structured_req: Structured request dictionary

        Returns:
            ComplexityResult from LLM

        Raises:
            ValueError: If no API key is set
            Exception: If API call fails
        """
        if not self.client:
            raise ValueError("No Anthropic API key provided")

        # System prompt with scoring rubric
        system_prompt = """You are a data analysis complexity evaluator. Score tasks on a scale of 1-10.

Scoring Rubric:
- Data complexity (1-3 pts): Single file (1), Multi-file JOIN (2), Complex transformation (3)
- Analytical method (1-4 pts): Aggregation (1), Multi-dimensional (2), Statistical (3), Modeling (4)
- Business logic (1-3 pts): Standard metrics (1), Business rules (2), Cross-department (3)

Mode Mapping:
- score < 3: "auto" (fully automated)
- 3 <= score <= 7: "collab" (collaborative)
- score > 7: "assist" (assistant mode)

Return JSON only with fields: score (int 1-10), reasoning (str), suggested_mode (str)."""

        # Create user message with structured request
        user_message = f"""Evaluate this analysis task:

{json.dumps(structured_req, indent=2)}

Provide complexity score (1-10), reasoning, and suggested execution mode."""

        # Call Claude API
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": user_message}
            ],
            system=system_prompt
        )

        # Parse response
        response_text = response.content[0].text

        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result_data = json.loads(response_text)

        # Extract fields
        score = int(result_data["score"])
        reasoning = result_data["reasoning"]
        suggested_mode = result_data.get("suggested_mode")

        # Ensure score is in valid range
        score = max(1, min(10, score))

        # Use suggested mode or calculate from score
        if suggested_mode and suggested_mode in ["auto", "collab", "assist"]:
            mode = suggested_mode
        else:
            mode = self._get_mode_for_score(score)

        return ComplexityResult(
            score=score,
            reasoning=reasoning,
            mode=mode
        )

    def score_with_rules(self, structured_req: Dict[str, Any]) -> ComplexityResult:
        """
        Score complexity using rule-based heuristics

        Args:
            structured_req: Structured request dictionary

        Returns:
            ComplexityResult from rules
        """
        score = 0
        reasons = []

        # Data complexity (0-3 pts)
        data_sources = structured_req.get("data_sources", [])
        joins = structured_req.get("joins", [])
        transformations = structured_req.get("transformations", [])

        if not data_sources:
            data_pts = 0
            reasons.append("minimal data sources")
        elif len(data_sources) == 1 and not joins and not transformations:
            data_pts = 0
            reasons.append("single file, no joins")
        elif len(data_sources) > 1 and joins:
            data_pts = 2
            reasons.append("multi-file with joins")
        elif transformations and len(transformations) > 1:
            data_pts = 3
            reasons.append("complex transformations")
        elif len(data_sources) > 2 or joins:
            data_pts = 1
            reasons.append("multiple data sources")
        else:
            data_pts = 0
            reasons.append("simple data structure")

        score += data_pts

        # Analytical method (1-4 pts)
        analysis_type = structured_req.get("analysis_type", "aggregation")
        metrics = structured_req.get("metrics", [])

        if analysis_type == "modeling" or "predicted" in str(metrics).lower():
            analytical_pts = 4
            reasons.append("modeling/prediction required")
        elif analysis_type == "statistical" or any(
            stat in str(metrics).lower() for stat in ["stddev", "correlation", "variance"]
        ):
            analytical_pts = 3
            reasons.append("statistical analysis")
        elif "multi-dimensional" in str(analysis_type).lower() or len(metrics) > 3:
            analytical_pts = 2
            reasons.append("multi-dimensional analysis")
        else:
            analytical_pts = 1
            reasons.append("basic aggregation")

        score += analytical_pts

        # Business logic (0-3 pts)
        business_rules = structured_req.get("business_rules", [])

        if not business_rules:
            business_pts = 0
            reasons.append("standard metrics")
        elif len(business_rules) > 2 or any(
            keyword in str(business_rules).lower()
            for keyword in ["cross", "department", "allocation", "attribution", "adjusted"]
        ):
            business_pts = 3
            reasons.append("complex cross-department logic")
        else:
            business_pts = 1
            reasons.append("custom business rules")

        score += business_pts

        # Ensure score is in valid range (1-10)
        score = max(1, min(10, score))

        # Determine mode
        mode = self._get_mode_for_score(score)

        # Build reasoning
        complexity_level = "Low" if score < 3 else "Medium" if score <= 7 else "High"
        reasoning = f"{complexity_level} complexity: {', '.join(reasons)} (score: {score})"

        return ComplexityResult(
            score=score,
            reasoning=reasoning,
            mode=mode
        )

    def _get_mode_for_score(self, score: int) -> str:
        """
        Map complexity score to execution mode

        Args:
            score: Complexity score (1-10)

        Returns:
            Execution mode: "auto", "collab", or "assist"
        """
        if score < 3:
            return "auto"
        elif score <= 7:
            return "collab"
        else:
            return "assist"
