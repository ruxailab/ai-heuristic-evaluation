import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
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
        recommendation: str,
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
            "recommendation": self.recommendation,
        }


class HeuristicScore:
    def __init__(
        self,
        heuristic_id: str,
        score: int,
        max_score: int = 100,
        violations: Optional[List[HeuristicViolation]] = None,
        explanation: Optional[str] = None,
        llm_explanation: Optional[str] = None,
    ):
        self.heuristic_id = heuristic_id
        self.score = score
        self.max_score = max_score
        self.violations = violations or []
        self.explanation = explanation
        self.llm_explanation = llm_explanation

    def to_dict(self):
        return {
            "heuristic_id": self.heuristic_id,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round((self.score / self.max_score) * 100, 2),
            "violations": [v.to_dict() for v in self.violations],
            "explanation": self.explanation,
            "llm_explanation": self.llm_explanation,
        }


class HeuristicEvaluationResult:
    def __init__(
        self,
        overall_score: float,
        heuristic_scores: List[HeuristicScore],
        total_violations: int,
        critical_issues: int,
        evaluation_metadata: Optional[Dict[str, Any]] = None,
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
            "timestamp": self.timestamp,
        }


class HeuristicEvaluationEngine:
    """LLM-powered heuristic evaluation engine (v2.0.0)."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_client: Optional[AsyncOpenAI] = None
        self.rag_kb: Optional[RAGKnowledgeBase] = None
        self.initialized = False

    async def initialize(self):
        self.logger.info("Initializing Heuristic Evaluation Engine...")
        self.llm_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.rag_kb = RAGKnowledgeBase()
        await self.rag_kb.initialize()
        self.initialized = True
        self.logger.info("Heuristic Evaluation Engine initialized")

    def _serialize_elements_for_llm(self, elements: List[UIElement]) -> str:
        serialized = []
        for e in elements:
            serialized.append(
                {
                    "type": e.element_type,
                    "bbox": list(e.bbox),
                    "interactivity": e.interactivity,
                    "content": e.text,
                }
            )
        return json.dumps(serialized, indent=2)

    async def _evaluate_with_llm(
        self,
        heuristic_id: HeuristicId,
        elements: List[UIElement],
        detection_result: UIElementDetectionResult,
    ) -> List[HeuristicViolation]:
        heuristic_def = NIELSEN_HEURISTICS.get(heuristic_id)
        if not heuristic_def:
            self.logger.error(f"No definition for {heuristic_id.value}")
            return []

        self.logger.info(
            f"LLM evaluation started for {heuristic_id.value} "
            f"with {len(elements)} UI elements"
        )

        elements_json = self._serialize_elements_for_llm(elements)

        rag_context = ""
        if self.rag_kb:
            try:
                examples = await self.rag_kb.retrieve_relevant_context(
                    query=f"{heuristic_def['name']} violations",
                    heuristic_id=heuristic_id.value,
                    top_k=3,
                )
                if examples:
                    rag_context = "\n\nRelevant examples:\n"
                    for ex in examples:
                        rag_context += f"- {ex['content']}\n"
            except Exception as exc:
                self.logger.warning(f"RAG lookup failed: {exc}")

        criteria_text = "\n".join(
            f"- {c['id']}: {c['description']}"
            for c in heuristic_def["measurable_criteria"]
        )

        prompt = f"""
You are a UX evaluation expert.

Heuristic: {heuristic_def['name']}
Description: {heuristic_def['description']}

Criteria:
{criteria_text}

UI Elements:
{elements_json}
{rag_context}

Return a JSON array of violations.
"""

        try:
            response = await self.llm_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            parsed = json.loads(response.choices[0].message.content)
            violations_data = parsed.get("violations", parsed)

            violations: List[HeuristicViolation] = []
            for v in violations_data if isinstance(violations_data, list) else []:
                severity = {
                    "critical": SeverityLevel.CRITICAL,
                    "major": SeverityLevel.MAJOR,
                    "minor": SeverityLevel.MINOR,
                    "cosmetic": SeverityLevel.COSMETIC,
                }.get(v.get("severity", "minor"), SeverityLevel.MINOR)

                violations.append(
                    HeuristicViolation(
                        heuristic_id=heuristic_id.value,
                        criterion_id=v.get("criterion_id", f"{heuristic_id.value}.0"),
                        severity=severity,
                        description=v.get("description", ""),
                        affected_elements=v.get("affected_elements", []),
                        recommendation=v.get("recommendation", ""),
                    )
                )

            self.logger.info(
                f"LLM evaluation completed for {heuristic_id.value}: "
                f"{len(violations)} violations"
            )

            return violations

        except Exception as exc:
            self.logger.error(f"LLM evaluation failed for {heuristic_id.value}: {exc}")
            return []

    def calculate_score(
        self, violations: List[HeuristicViolation], heuristic_id: str
    ) -> tuple[int, str]:
        heuristic_def = NIELSEN_HEURISTICS.get(HeuristicId(heuristic_id))
        if not heuristic_def:
            return 100, "No criteria defined"

        deduction = 0
        explanations = []

        for v in violations:
            criterion = next(
                (c for c in heuristic_def["measurable_criteria"] if c["id"] == v.criterion_id),
                None,
            )
            if criterion:
                deduction += criterion["severity_weights"].get(v.severity.value, 1)
                explanations.append(f"{v.severity.value}: {v.description}")

        score = max(0, 100 - deduction)
        return score, f"Score {score}/100 - {len(violations)} violations: " + "; ".join(explanations)

    async def evaluate_heuristic(
        self,
        heuristic_id: HeuristicId,
        elements: List[UIElement],
        detection_result: UIElementDetectionResult,
    ) -> HeuristicScore:
        violations = await self._evaluate_with_llm(heuristic_id, elements, detection_result)
        score, explanation = self.calculate_score(violations, heuristic_id.value)

        return HeuristicScore(
            heuristic_id=heuristic_id.value,
            score=score,
            violations=violations,
            explanation=explanation,
        )

    async def evaluate_interface(
        self, detection_result: UIElementDetectionResult
    ) -> HeuristicEvaluationResult:
        if not self.initialized:
            await self.initialize()

        heuristic_ids = [
            HeuristicId.H1_VISIBILITY_OF_SYSTEM_STATUS,
            HeuristicId.H2_MATCH_BETWEEN_SYSTEM_AND_REAL_WORLD,
            HeuristicId.H3_USER_CONTROL_AND_FREEDOM,
            HeuristicId.H4_CONSISTENCY_AND_STANDARDS,
        ]

        scores = []
        total_violations = 0
        critical = 0

        for hid in heuristic_ids:
            score = await self.evaluate_heuristic(hid, detection_result.elements, detection_result)
            scores.append(score)
            total_violations += len(score.violations)
            critical += sum(1 for v in score.violations if v.severity == SeverityLevel.CRITICAL)

        overall = sum(s.score for s in scores) / len(scores)

        return HeuristicEvaluationResult(
            overall_score=round(overall, 2),
            heuristic_scores=scores,
            total_violations=total_violations,
            critical_issues=critical,
            evaluation_metadata={
                "evaluation_version": "2.0.0-llm",
                "evaluation_method": "llm-based",
                "total_elements": len(detection_result.elements),
            },
        )
