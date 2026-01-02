import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Request
from typing import Optional, List
import json

from app.services.heuristic_engine import HeuristicEvaluationEngine
from app.core.config import settings, ALLOWED_IMAGE_TYPES
from app.services.exceptions import InvalidInputError

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/evaluate")
async def evaluate_heuristics(
    request: Request,
    image: UploadFile = File(...),
    include_llm_analysis: bool = True
):
    """Evaluate UI heuristics from an uploaded screenshot.
    
    Args:
        image: Uploaded image file (JPEG, PNG, or WebP)
        include_llm_analysis: Whether to include LLM-based analysis
        
    Returns:
        Evaluation results with scores and violations
        
    Raises:
        400: Invalid input (bad image type, corrupted file, etc.)
        422: OmniParser processing failed
        503: Model inference or RAG knowledge base unavailable
        500: Unexpected server error
    """
    try:
        # Validate file exists
        if not image:
            raise InvalidInputError(
                message="No image file provided",
                details={"field": "image"}
            )
        
        # Validate content type
        content_type = image.content_type or "application/octet-stream"
        if content_type not in ALLOWED_IMAGE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_IMAGE_TYPES))
            raise InvalidInputError(
                message=f"Unsupported image type: {content_type}. Allowed types: {allowed}",
                details={
                    "received": content_type,
                    "allowed_types": list(ALLOWED_IMAGE_TYPES)
                }
            )
        
        # Use singleton OmniParser client from app.state (avoids re-initializing model)
        detection_client = request.app.state.omniparser_client
        contents = await image.read()
        
        detection_result = await detection_client.detect_elements(contents)

        # Initialize evaluation engine and evaluate
        evaluation_engine = HeuristicEvaluationEngine()
        await evaluation_engine.initialize()

        evaluation_result = await evaluation_engine.evaluate_interface(detection_result)

        return {
            "success": True,
            "data": evaluation_result.to_dict(),
            "metadata": {
                "processing_time_ms": 0,
                "model_version": "2.0.0-llm",
                "include_llm_analysis": include_llm_analysis
            }
        }

    except Exception as e:
        logger.exception(f"Error evaluating heuristics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )

@router.post("/evaluate-legacy/{heuristic_id}")
async def evaluate_legacy_format(
    heuristic_id: str,
    elements: List[dict] = Body(...)
):
    """Evaluate a specific heuristic using legacy element format.
    
    Args:
        heuristic_id: Nielsen heuristic ID (H1-H5)
        elements: List of UI element dictionaries
        
    Returns:
        Heuristic score with violations
        
    Raises:
        400: Invalid heuristic ID or malformed elements
        503: Model inference unavailable
        500: Unexpected server error
    """
    try:
        from app.core.constants import HeuristicId

        # Normalize heuristic_id to uppercase
        normalized_id = heuristic_id.upper()
        if normalized_id not in [h.value for h in HeuristicId]:
            raise InvalidInputError(
                message=f"Invalid heuristic ID: {heuristic_id}",
                details={
                    "received": heuristic_id,
                    "valid_ids": [h.value for h in HeuristicId]
                }
            )

        evaluation_engine = HeuristicEvaluationEngine()
        await evaluation_engine.initialize()

        from app.services.omniparser_client import UIElement
        try:
            ui_elements = [UIElement.from_dict(e) for e in elements]
        except Exception as e:
            raise InvalidInputError(
                message="Invalid element format",
                details={"error": str(e)}
            )

        # Find the matching HeuristicId enum by value
        h_id = next(h for h in HeuristicId if h.value == normalized_id)
        score = await evaluation_engine.evaluate_heuristic(h_id, ui_elements, None)

        return {
            "success": True,
            "data": score.to_dict()
        }

    except InvalidInputError as e:
        logger.warning(f"Invalid input in legacy evaluation: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Input",
                "message": e.message,
                "details": e.details
            }
        )
    
    except ModelInferenceError as e:
        logger.error(f"Model inference error in legacy evaluation: {e.message}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service Unavailable",
                "message": e.message,
                "details": e.details
            }
        )

    except Exception as e:
        logger.exception(f"Unexpected error in legacy evaluation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your request"
            }
        )

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
    """Get statistics about the RAG knowledge base.
    
    Returns:
        Knowledge base statistics
        
    Raises:
        503: RAG knowledge base unavailable
        500: Unexpected server error
    """
    try:
        from app.services.rag_knowledge_base import RAGKnowledgeBase

        kb = RAGKnowledgeBase()
        await kb.initialize()
        stats = await kb.get_stats()

        return {
            "success": True,
            "data": stats
        }

    except RAGKnowledgeBaseError as e:
        logger.error(f"RAG knowledge base error: {e.message}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service Unavailable",
                "message": e.message,
                "details": e.details
            }
        )

    except Exception as e:
        logger.exception(f"Unexpected error getting knowledge base stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while retrieving knowledge base statistics"
            }
        )
