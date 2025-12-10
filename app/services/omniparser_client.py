import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import io
import json
from ultralytics import YOLO
import torch
from transformers import AutoProcessor, AutoModelForCausalLM



TYPE_MAPPING = {
    "clickable_button": "button",
    "icon_button": "button",
    "submit_button": "button",
    "button": "button",
    "text_input": "input",
    "input": "input",
    "search_bar": "input",
    "heading": "heading",
    "header": "heading",
    "title": "heading",
    "h1": "heading",
    "h2": "heading",
    "h3": "heading"
}

logger = logging.getLogger(__name__)

class UIElement:
    """UI Element matching real Omniparser output format.
    
    Fields align with Omniparser:
    - type: element type (button, text, input, etc.)
    - bbox: [x1, y1, x2, y2] bounding box coordinates
    - interactivity: boolean indicating if element is interactive
    - content: text content of the element
    """
    
    def __init__(
        self,
        element_type: str,
        bbox: List[float],
        content: str = "",
        interactivity: bool = False
    ):
        """Initialize UIElement with Omniparser-compatible format.
        
        Args:
            element_type: Type of UI element (button, text, input, etc.)
            bbox: Bounding box as [x1, y1, x2, y2]
            content: Text content of the element
            interactivity: Whether the element is interactive
        """
        self.element_type = element_type
        self.bbox = bbox
        self.content = content
        self.interactivity = interactivity
        
        # Computed properties for convenience
        self._width = bbox[2] - bbox[0] if len(bbox) == 4 else 0
        self._height = bbox[3] - bbox[1] if len(bbox) == 4 else 0
    
    @property
    def text(self) -> str:
        """Alias for content to maintain backward compatibility."""
        return self.content
    
    @property
    def width(self) -> float:
        """Computed width from bbox."""
        return self._width
    
    @property
    def height(self) -> float:
        """Computed height from bbox."""
        return self._height
    
    @property
    def bounds(self) -> Dict[str, float]:
        """Legacy bounds format for backward compatibility."""
        return {
            "x": self.bbox[0],
            "y": self.bbox[1],
            "width": self.width,
            "height": self.height
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.element_type,
            "bbox": self.bbox,
            "content": self.content,
            "interactivity": self.interactivity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIElement':
        """Create UIElement from Omniparser output dict."""
        return cls(
            element_type=data.get("type", data.get("element_type", "unknown")),
            bbox=data.get("bbox", [0, 0, 0, 0]),
            content=data.get("content", data.get("text", "")),
            interactivity=data.get("interactivity", data.get("interactive", False))
        )


def infer_heading_level(element: UIElement, all_text_elements: List[UIElement]) -> Optional[int]:
    """Infer heading level (1-6) based on bounding box height.
    
    Larger height indicates higher-level heading (h1 > h2 > h3, etc.).
    Uses normalization across all text elements to ensure consistency.
    
    Args:
        element: The element to classify
        all_text_elements: All text elements for normalization
    
    Returns:
        Heading level 1-6, or None if not a heading
    """
    if element.element_type not in ["text", "heading"]:
        return None
    
    # Get heights of all text elements
    heights = [e.height for e in all_text_elements if e.height > 0]
    if not heights or element.height <= 0:
        return None
    
    # Calculate percentile thresholds
    sorted_heights = sorted(heights, reverse=True)
    max_height = sorted_heights[0]
    min_height = sorted_heights[-1]
    
    # If height is below median, it's likely body text, not a heading
    median_height = sorted_heights[len(sorted_heights) // 2]
    if element.height < median_height:
        return None
    
    # Map height to heading levels using percentiles
    # Top 5% = h1, next 10% = h2, next 15% = h3, etc.
    percentile_rank = sorted_heights.index(element.height) / len(sorted_heights) if element.height in sorted_heights else 1.0
    
    if percentile_rank <= 0.05:  # Top 5%
        return 1
    elif percentile_rank <= 0.15:  # Top 15%
        return 2
    elif percentile_rank <= 0.30:  # Top 30%
        return 3
    elif percentile_rank <= 0.50:  # Top 50%
        return 4
    else:
        return None  # Body text


def calculate_height_variance(elements: List[UIElement]) -> float:
    """Calculate variance in element heights.
    
    Useful for detecting inconsistent sizing.
    
    Args:
        elements: List of UI elements
        
    Returns:
        Coefficient of variation (std dev / mean) as percentage
    """
    if len(elements) < 2:
        return 0.0
    
    heights = [e.height for e in elements if e.height > 0]
    if not heights:
        return 0.0
    
    mean_height = sum(heights) / len(heights)
    variance = sum((h - mean_height) ** 2 for h in heights) / len(heights)
    std_dev = variance ** 0.5
    
    # Return coefficient of variation as percentage
    return (std_dev / mean_height * 100) if mean_height > 0 else 0.0

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
        # Loading YOLO 
        self.yolo_model = YOLO("weights/icon_detect/best.pt")
        
        # Loading Florence-2 
        self.caption_model = AutoModelForCausalLM.from_pretrained(
            "weights/icon_caption_florence", 
            trust_remote_code=True
        )
        self.processor = AutoProcessor.from_pretrained(
            "weights/icon_caption_florence", 
            trust_remote_code=True
        )
        self.model_loaded = True
        self.logger.info("OmniParser client initialized successfully")

    def _map_element_type(self, raw_type: str) -> str:
        return TYPE_MAPPING.get(raw_type.lower(), "unknown")

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

            results = self.yolo_model(image)
            elements = []
            for result in results:
                for box in result.boxes:
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # Get type 
                    cls_id = int(box.cls[0])
                    raw_type = self.yolo_model.names[cls_id]
                    mapped_type = self._map_element_type(raw_type)

                    # Create Element matching new Omniparser format
                    elements.append(UIElement(
                        element_type=mapped_type,
                        bbox=[x1, y1, x2, y2],
                        content="",  # Placeholder for now
                        interactivity=False # Default to False as we don't infer it yet
                    ))

            layout_hierarchy = {}
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
