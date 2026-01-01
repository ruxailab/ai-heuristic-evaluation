import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from typing import Optional
from PIL import Image
import io

from app.services.omniparser_client import OmniParserClient, UIElementDetectionResult

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/detect-elements")
async def detect_ui_elements(
    request: Request,
    image: UploadFile = File(...),
    image_url: Optional[str] = Form(None)
):
    try:
        client = request.app.state.omniparser_client

        if image:
            contents = await image.read()
            result = await client.detect_elements(contents, image.filename)
        elif image_url:
            result = await client.detect_elements(image_url=image_url)
        else:
            raise HTTPException(status_code=400, detail="Either image or image_url must be provided")

        return {
            "success": True,
            "data": result.to_dict()
        }

    except Exception as e:
        logger.error(f"Error detecting UI elements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_interface(
    image: UploadFile = File(...)
):
    try:
        client = OmniParserClient()
        await client.initialize()

        contents = await image.read()
        result = await client.detect_elements(contents)

        grouped = client.group_related_elements(result.elements)

        return {
            "success": True,
            "data": {
                "detection": result.to_dict(),
                "grouped_elements": {
                    k: [e.to_dict() for e in v] for k, v in grouped.items()
                },
                "summary": {
                    "total_elements": len(result.elements),
                    "interactive_elements": sum(1 for e in result.elements if e.interactive),
                    "element_types": list(set(e.element_type for e in result.elements))
                }
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing interface: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
