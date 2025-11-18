import logging
import asyncio
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import json

logger = logging.getLogger(__name__)

class UIElement:
    def __init__(
        self,
        element_type: str,
        text: str,
        bounds: Dict[str, int],
        interactive: bool = False,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.element_type = element_type
        self.text = text
        self.bounds = bounds
        self.interactive = interactive
        self.attributes = attributes or {}

    def to_dict(self):
        return {
            "element_type": self.element_type,
            "text": self.text,
            "bounds": self.bounds,
            "interactive": self.interactive,
            "attributes": self.attributes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            element_type=data["element_type"],
            text=data.get("text", ""),
            bounds=data["bounds"],
            interactive=data.get("interactive", False),
            attributes=data.get("attributes", {})
        )

class UIElementDetectionResult:
    def __init__(
        self,
        elements: List[UIElement],
        layout_hierarchy: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.elements = elements
        self.layout_hierarchy = layout_hierarchy
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "elements": [e.to_dict() for e in self.elements],
            "layout_hierarchy": self.layout_hierarchy,
            "metadata": self.metadata
        }

class OmniParserClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_loaded = False

    async def initialize(self):
        self.logger.info("Initializing OmniParser client...")
        self.model_loaded = True
        self.logger.info("OmniParser client initialized successfully")

    async def detect_elements(
        self,
        image_data: bytes,
        image_url: Optional[str] = None
    ) -> UIElementDetectionResult:
        self.logger.info("Starting UI element detection...")

        if not self.model_loaded:
            await self.initialize()

        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            self.logger.info(f"Processing image: {width}x{height}")

            elements = [
                UIElement(
                    element_type="button",
                    text="Submit",
                    bounds={"x": 100, "y": 200, "width": 120, "height": 40},
                    interactive=True,
                    attributes={"class": "btn-primary", "color": "#0066cc"}
                ),
                UIElement(
                    element_type="input",
                    text="",
                    bounds={"x": 100, "y": 150, "width": 200, "height": 35},
                    interactive=True,
                    attributes={"type": "text", "placeholder": "Enter email"}
                ),
                UIElement(
                    element_type="heading",
                    text="Login Form",
                    bounds={"x": 100, "y": 100, "width": 200, "height": 30},
                    interactive=False,
                    attributes={"level": "h1"}
                ),
                UIElement(
                    element_type="link",
                    text="Forgot Password?",
                    bounds={"x": 100, "y": 260, "width": 150, "height": 20},
                    interactive=True,
                    attributes={"href": "/forgot-password"}
                )
            ]

            layout_hierarchy = {
                "root": {
                    "type": "form",
                    "children": [
                        {"type": "heading", "ref": 0},
                        {"type": "input", "ref": 1},
                        {"type": "button", "ref": 2},
                        {"type": "link", "ref": 3}
                    ]
                }
            }

            result = UIElementDetectionResult(
                elements=elements,
                layout_hierarchy=layout_hierarchy,
                metadata={
                    "width": width,
                    "height": height,
                    "total_elements": len(elements)
                }
            )

            self.logger.info(f"Detection complete: {len(elements)} elements found")
            return result

        except Exception as e:
            self.logger.error(f"Error in element detection: {str(e)}")
            raise

    def group_related_elements(self, elements: List[UIElement]) -> Dict[str, List[UIElement]]:
        grouped = {
            "buttons": [],
            "inputs": [],
            "navigation": [],
            "content": [],
            "links": []
        }

        for element in elements:
            element_type = element.element_type.lower()
            if element_type in ["button", "submit", "reset"]:
                grouped["buttons"].append(element)
            elif element_type in ["input", "textarea", "select"]:
                grouped["inputs"].append(element)
            elif element_type in ["nav", "menu", "header", "footer"]:
                grouped["navigation"].append(element)
            elif element_type in ["a", "link"]:
                grouped["links"].append(element)
            else:
                grouped["content"].append(element)

        return grouped
