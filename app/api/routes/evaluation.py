import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Request
from typing import Optional, List
import json

from app.services.heuristic_engine import HeuristicEvaluationEngine
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/evaluate")
async def evaluate_heuristics(
    request: Request,
    image: UploadFile = File(...),
    include_llm_analysis: bool = True
):
    try:
        detection_client = request.app.state.omniparser_client
        contents = await image.read()
        detection_result = await detection_client.detect_elements(contents)

        evaluation_engine = HeuristicEvaluationEngine()
        await evaluation_engine.initialize()

        evaluation_result = await evaluation_engine.evaluate_interface(detection_result)

        return {
            "success": True,
            "data": evaluation_result.to_dict(),
            "metadata": {
                "processing_time_ms": 0,
                "model_version": "1.0.0",
                "include_llm_analysis": include_llm_analysis
            }
        }

    except Exception as e:
        logger.error(f"Error evaluating heuristics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate-legacy/{heuristic_id}")
async def evaluate_legacy_format(
    heuristic_id: str,
    elements: List[dict] = Body(...)
):
    try:
        from app.core.constants import HeuristicId

        # Normalize heuristic_id to uppercase
        normalized_id = heuristic_id.upper()
        if normalized_id not in [h.value for h in HeuristicId]:
            raise HTTPException(status_code=400, detail=f"Invalid heuristic ID: {heuristic_id}")

        evaluation_engine = HeuristicEvaluationEngine()
        await evaluation_engine.initialize()

        from app.services.omniparser_client import UIElement
        ui_elements = [UIElement.from_dict(e) for e in elements]

        # Find the matching HeuristicId enum by value
        h_id = next(h for h in HeuristicId if h.value == normalized_id)
        score = await evaluation_engine.evaluate_heuristic(h_id, ui_elements, None)

        return {
            "success": True,
            "data": score.to_dict()
        }

    except Exception as e:
        logger.error(f"Error in legacy evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/heuristics")
async def get_heuristics():
    from app.core.constants import NIELSEN_HEURISTICS

    return {
        "success": True,
        "data": {
            heuristic_id.value: {
                "name": data["name"],
                "description": data["description"],
                "criteria_count": len(data["measurable_criteria"])
            }
            for heuristic_id, data in NIELSEN_HEURISTICS.items()
        }
    }

@router.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    try:
        from app.services.rag_knowledge_base import RAGKnowledgeBase

        kb = RAGKnowledgeBase()
        await kb.initialize()
        stats = await kb.get_stats()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
