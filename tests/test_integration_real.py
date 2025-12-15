import pytest
import json
import os
from app.services.omniparser_client import OmniParserClient
from app.services.heuristic_engine import HeuristicEvaluationEngine

@pytest.mark.asyncio
async def test_real_omniparser_integration():
    client = OmniParserClient()
    if not os.path.exists("weights/icon_detect/best.pt"):
        pytest.skip("Skipping integration test: Weights not found")
    
    await client.initialize()

    with open("tests/ground_truth.json") as f:
        truth = json.load(f)

    image_path = truth["image_filename"] 
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()

    detection_result = await client.detect_elements(image_data)

    assert len(detection_result.elements) > 0, "Should detect at least one element"
    found_button = any(e.element_type == "button" for e in detection_result.elements)
    assert found_button, "Failed to detect the expected button"

    # Heuristic Engine Test
    engine = HeuristicEvaluationEngine()
    
    if not os.environ.get("OPENAI_API_KEY"):
         print("\nWarning: OPENAI_API_KEY not found. Skipping Engine portion.")
         return 

    await engine.initialize()
    report = await engine.evaluate_interface(detection_result)
    
    assert len(report.heuristic_scores) == 10, f"Expected 10 heuristic scores, got {len(report.heuristic_scores)}"
