import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from openai import AsyncOpenAI

from app.core.constants import NIELSEN_HEURISTICS, HeuristicId, SeverityLevel
from app.core.config import settings
from app.services.omniparser_client import UIElementDetectionResult, UIElement
from app.services.rag_knowledge_base import RAGKnowledgeBase

logger = logging.getLogger(__name__)

class HeuristicViolation:
    def __init__(
        self,
        heuristic_id: str,
        criterion_id: str,
        severity: SeverityLevel,
        description: str,
        affected_elements: List[str],
        recommendation: str
    ):
        self.heuristic_id = heuristic_id
        self.criterion_id = criterion_id
        self.severity = severity
        self.description = description
        self.affected_elements = affected_elements
        self.recommendation = recommendation

    def to_dict(self):
        return {
            "heuristic_id": self.heuristic_id,
            "criterion_id": self.criterion_id,
            "severity": self.severity.value,
            "description": self.description,
            "affected_elements": self.affected_elements,
            "recommendation": self.recommendation
        }

class HeuristicScore:
    def __init__(
        self,
        heuristic_id: str,
        score: int,
        max_score: int = 100,
        violations: Optional[List[HeuristicViolation]] = None,
        explanation: Optional[str] = None
    ):
        self.heuristic_id = heuristic_id
        self.score = score
        self.max_score = max_score
        self.violations = violations or []
        self.explanation = explanation

    def to_dict(self):
        return {
            "heuristic_id": self.heuristic_id,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round((self.score / self.max_score) * 100, 2),
            "violations": [v.to_dict() for v in self.violations],
            "explanation": self.explanation
        }

class HeuristicEvaluationResult:
    def __init__(
        self,
        overall_score: float,
        heuristic_scores: List[HeuristicScore],
        total_violations: int,
        critical_issues: int,
        evaluation_metadata: Optional[Dict[str, Any]] = None
    ):
        self.overall_score = overall_score
        self.heuristic_scores = heuristic_scores
        self.total_violations = total_violations
        self.critical_issues = critical_issues
        self.evaluation_metadata = evaluation_metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "overall_score": self.overall_score,
            "heuristic_scores": [hs.to_dict() for hs in self.heuristic_scores],
            "total_violations": self.total_violations,
            "critical_issues": self.critical_issues,
            "evaluation_metadata": self.evaluation_metadata,
            "timestamp": self.timestamp
        }

class HeuristicEvaluationEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_client = None
        self.rag_kb = None
        self.initialized = False

    async def initialize(self):
        self.logger.info("Initializing Heuristic Evaluation Engine...")
        self.llm_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.rag_kb = RAGKnowledgeBase()
        await self.rag_kb.initialize()
        self.initialized = True
        self.logger.info("Heuristic Evaluation Engine initialized")

    def calculate_score(self, violations: List[HeuristicViolation], heuristic_id: str) -> tuple[int, str]:
        heuristic_def = NIELSEN_HEURISTICS.get(HeuristicId(heuristic_id))
        if not heuristic_def:
            return 100, "No criteria defined"

        total_deduction = 0
        explanation_parts = []

        for violation in violations:
            criterion = next(
                (c for c in heuristic_def["measurable_criteria"] if c["id"] == violation.criterion_id),
                None
            )
            if criterion:
                weights = criterion["severity_weights"]
                deduction = weights.get(violation.severity.value, 1)
                total_deduction += deduction
                explanation_parts.append(
                    f"{violation.severity.value}: {violation.description}"
                )

        score = max(0, 100 - total_deduction)
        explanation = f"Score {score}/100 - {len(violations)} violations: " + "; ".join(explanation_parts)

        return score, explanation

    async def evaluate_heuristic(
        self,
        heuristic_id: HeuristicId,
        elements: List[UIElement],
        detection_result: UIElementDetectionResult
    ) -> HeuristicScore:
        self.logger.info(f"Evaluating heuristic {heuristic_id.value}")

        violations = []

        if heuristic_id == HeuristicId.H1_VISIBILITY_OF_SYSTEM_STATUS:
            violations = await self._evaluate_h1_visibility(elements, detection_result)
        elif heuristic_id == HeuristicId.H2_MATCH_BETWEEN_SYSTEM_AND_REAL_WORLD:
            violations = await self._evaluate_h2_match_real_world(elements, detection_result)
        elif heuristic_id == HeuristicId.H3_USER_CONTROL_AND_FREEDOM:
            violations = await self._evaluate_h3_user_control(elements, detection_result)

        score, explanation = self.calculate_score(violations, heuristic_id.value)

        return HeuristicScore(
            heuristic_id=heuristic_id.value,
            score=score,
            violations=violations,
            explanation=explanation
        )

    async def _evaluate_h1_visibility(
        self,
        elements: List[UIElement],
        detection_result: UIElementDetectionResult
    ) -> List[HeuristicViolation]:
        violations = []

        buttons = [e for e in elements if e.element_type == "button"]
        inputs = [e for e in elements if e.element_type == "input"]

        for button in buttons:
            if not button.attributes.get("hover_state") and not button.attributes.get("active_state"):
                violations.append(HeuristicViolation(
                    heuristic_id="H1",
                    criterion_id="H1.2",
                    severity=SeverityLevel.MAJOR,
                    description=f"Button '{button.text}' lacks visible hover or active states",
                    affected_elements=[button.text],
                    recommendation="Add hover and active states to button for user feedback"
                ))

        for input_field in inputs:
            if not input_field.attributes.get("placeholder") and not input_field.text:
                violations.append(HeuristicViolation(
                    heuristic_id="H1",
                    criterion_id="H1.1",
                    severity=SeverityLevel.MINOR,
                    description=f"Input field lacks placeholder or label for guidance",
                    affected_elements=[input_field.text],
                    recommendation="Add placeholder text or label to help users understand input"
                ))

        if len(buttons) > 0 and not any(b.attributes.get("loading_state") for b in buttons):
            violations.append(HeuristicViolation(
                heuristic_id="H1",
                criterion_id="H1.2",
                severity=SeverityLevel.MAJOR,
                description="No loading states detected for action buttons",
                affected_elements=[b.text for b in buttons],
                recommendation="Add loading indicators to buttons during async operations"
            ))

        return violations

    async def _evaluate_h2_match_real_world(
        self,
        elements: List[UIElement],
        detection_result: UIElementDetectionResult
    ) -> List[HeuristicViolation]:
        violations = []

        for element in elements:
            if element.element_type == "button":
                text = element.text.lower()
                if any(term in text for term in ["submit", "execute", "process"]):
                    violations.append(HeuristicViolation(
                        heuristic_id="H2",
                        criterion_id="H2.2",
                        severity=SeverityLevel.MINOR,
                        description=f"Button uses technical term '{element.text}' instead of user-friendly language",
                        affected_elements=[element.text],
                        recommendation="Use action-oriented, user-friendly language (e.g., 'Send', 'Save', 'Continue')"
                    ))

            if element.element_type == "heading":
                text = element.text
                if any(jargon in text.lower() for jargon in ["api", "endpoint", "database"]):
                    violations.append(HeuristicViolation(
                        heuristic_id="H2",
                        criterion_id="H2.2",
                        severity=SeverityLevel.MAJOR,
                        description=f"Heading contains technical jargon: '{text}'",
                        affected_elements=[text],
                        recommendation="Replace technical jargon with user-friendly terminology"
                    ))

        return violations

    async def _evaluate_h3_user_control(
        self,
        elements: List[UIElement],
        detection_result: UIElementDetectionResult
    ) -> List[HeuristicViolation]:
        violations = []

        has_delete_button = any(
            "delete" in e.text.lower() or "remove" in e.text.lower()
            for e in elements if e.element_type == "button"
        )

        if has_delete_button:
            delete_buttons = [
                e for e in elements
                if e.element_type == "button" and
                ("delete" in e.text.lower() or "remove" in e.text.lower())
            ]

            for btn in delete_buttons:
                if not btn.attributes.get("confirmation"):
                    violations.append(HeuristicViolation(
                        heuristic_id="H3",
                        criterion_id="H3.3",
                        severity=SeverityLevel.CRITICAL,
                        description=f"Delete button '{btn.text}' lacks confirmation dialog",
                        affected_elements=[btn.text],
                        recommendation="Add confirmation dialog for destructive actions to prevent accidents"
                    ))

        form_elements = [e for e in elements if e.element_type in ["button", "input", "form"]]
        has_cancel = any(
            "cancel" in e.text.lower() or "back" in e.text.lower()
            for e in elements if e.element_type == "button"
        )

        if len(form_elements) > 2 and not has_cancel:
            violations.append(HeuristicViolation(
                heuristic_id="H3",
                criterion_id="H3.2",
                severity=SeverityLevel.MAJOR,
                description="Form lacks clear exit option (cancel/back button)",
                affected_elements=["form"],
                recommendation="Add cancel/back button to allow users to exit without completing form"
            ))

        return violations

    async def evaluate_interface(
        self,
        detection_result: UIElementDetectionResult
    ) -> HeuristicEvaluationResult:
        self.logger.info("Starting comprehensive heuristic evaluation...")

        if not self.initialized:
            await self.initialize()

        heuristic_ids = [
            HeuristicId.H1_VISIBILITY_OF_SYSTEM_STATUS,
            HeuristicId.H2_MATCH_BETWEEN_SYSTEM_AND_REAL_WORLD,
            HeuristicId.H3_USER_CONTROL_AND_FREEDOM
        ]

        heuristic_scores = []
        total_violations = 0
        critical_issues = 0

        for heuristic_id in heuristic_ids:
            score = await self.evaluate_heuristic(
                heuristic_id,
                detection_result.elements,
                detection_result
            )
            heuristic_scores.append(score)
            total_violations += len(score.violations)
            critical_issues += sum(1 for v in score.violations if v.severity == SeverityLevel.CRITICAL)

        overall_score = sum(hs.score for hs in heuristic_scores) / len(heuristic_scores)

        result = HeuristicEvaluationResult(
            overall_score=round(overall_score, 2),
            heuristic_scores=heuristic_scores,
            total_violations=total_violations,
            critical_issues=critical_issues,
            evaluation_metadata={
                "total_elements": len(detection_result.elements),
                "evaluation_version": "1.0.0"
            }
        )

        self.logger.info(
            f"Evaluation complete: Overall score {overall_score:.2f}, "
            f"{total_violations} violations, {critical_issues} critical"
        )

        return result
