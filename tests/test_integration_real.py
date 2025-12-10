import pytest
import json
import os
from app.services.omniparser_client import OmniParserClient

@pytest.mark.asyncio
async def test_real_omniparser_integration():
    client = OmniParserClient()
    if not os.path.exists("weights/icon_detect/best.pt"):
        pytest.skip("Skipping integration test: Weights not found")
    
    await client.initialize()

    with open("tests/ground_truth.json") as f:
        truth = json.load(f)

    # Ensure this image exists in your tests folder or root
    image_path = truth["image_filename"] 
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()

    result = await client.detect_elements(image_data)


    assert len(result.elements) > 0, "Should detect at least one element"
    
    # Check if we found the expected button
    found_button = any(e.element_type == "button" for e in result.elements)
    assert found_button, "Failed to detect the expected button"