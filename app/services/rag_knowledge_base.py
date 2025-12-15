import logging
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class RAGKnowledgeBase:
    def __init__(self, index_path: Optional[str] = None, vector_store_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.index_path = index_path or "./data/knowledge_base.index"
        self.vector_store_path = vector_store_path or "./data/vector_store"
        self.index_initialized = False
        self.knowledge_entries = []

    async def initialize(self):
        self.logger.info("Initializing RAG Knowledge Base...")

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        await self._load_knowledge_base()

        self.index_initialized = True
        self.logger.info(f"RAG Knowledge Base initialized with {len(self.knowledge_entries)} entries")

    async def _load_knowledge_base(self):
        knowledge_data = [
            {
                "id": "kb_001",
                "category": "Button Feedback",
                "content": "Buttons should provide clear visual feedback on hover, active, and disabled states. This helps users understand interactability and system response.",
                "heuristic_id": "H1",
                "example": "A primary button changes to darker shade on hover and shows pressed state on click"
            },
            {
                "id": "kb_002",
                "category": "Error Prevention",
                "content": "Destructive actions like delete should always be preceded by confirmation dialogs to prevent accidental data loss.",
                "heuristic_id": "H3",
                "example": "Delete button triggers modal: 'Are you sure you want to delete this item? This action cannot be undone.'"
            },
            {
                "id": "kb_003",
                "category": "Form Labels",
                "content": "All input fields must have visible labels or placeholders. Placeholders should complement, not replace labels.",
                "heuristic_id": "H1",
                "example": "Email field has label 'Email Address' and placeholder 'you@example.com'"
            },
            {
                "id": "kb_004",
                "category": "User-Friendly Language",
                "content": "Use action-oriented, conversational language that matches user expectations. Avoid technical jargon in user-facing text.",
                "heuristic_id": "H2",
                "example": "Use 'Send Message' instead of 'Submit Payload' or 'Create Account' instead of 'Register User'"
            },
            {
                "id": "kb_005",
                "category": "Navigation",
                "content": "Always provide a clear way to exit or cancel actions. Users should never feel trapped in the interface.",
                "heuristic_id": "H3",
                "example": "Multi-step wizard has Back button and Cancel option on all steps"
            },
            {
                "id": "kb_006",
                "category": "Consistency",
                "content": "Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform conventions.",
                "heuristic_id": "H4",
                "example": "Use standard platform icons (e.g., magnifying glass for search) and keep terminology consistent (e.g., don't mix 'Delete' and 'Remove')"
            },
            {
                "id": "kb_007",
                "category": "Error Prevention",
                "content": "Prevent errors from occurring in the first place by using constraints and good defaults.",
                "heuristic_id": "H5",
                "example": "Date picker disables past dates for flight departure; numeric fields reject alphabetic characters"
            },
            {
                "id": "kb_008",
                "category": "Recognition over Recall",
                "content": "Minimize the user's memory load by making objects, actions, and options visible. The user should not have to remember information from one part of the dialogue to another.",
                "heuristic_id": "H6",
                "example": "Search bar shows recent searches; Menu items are visible or easily accessible, not hidden deep in sub-menus"
            },
            {
                "id": "kb_009",
                "category": "Flexibility and Efficiency",
                "content": "Accelerators — unseen by the novice user — may often speed up the interaction for the expert user.",
                "heuristic_id": "H7",
                "example": "Support keyboard shortcuts (Ctrl+S to save) and allow users to customize their dashboard layout"
            },
            {
                "id": "kb_010",
                "category": "Aesthetic and Minimalist Design",
                "content": "Dialogues should not contain information which is irrelevant or rarely needed. Every extra unit of information competes with the relevant units.",
                "heuristic_id": "H8",
                "example": "Remove rarely used metadata from the main table view; use ample whitespace to group related elements"
            },
            {
                "id": "kb_011",
                "category": "Error Recovery",
                "content": "Error messages should be expressed in plain language (no codes), precisely indicate the problem, and constructively suggest a solution.",
                "heuristic_id": "H9",
                "example": "Instead of 'Error 503', show 'Connection failed. Please check your internet and Try Again'"
            },
            {
                "id": "kb_012",
                "category": "Help and Documentation",
                "content": "Even though it is better if the system can be used without documentation, it may be necessary to provide help and documentation.",
                "heuristic_id": "H10",
                "example": "Provide contextual tooltips for complex settings and a searchable Help Center"
            }
        ]

        self.knowledge_entries = knowledge_data
        self.logger.info("Loaded knowledge base entries")

    async def retrieve_relevant_context(
        self,
        query: str,
        heuristic_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        if not self.index_initialized:
            await self.initialize()

        relevant_entries = self.knowledge_entries.copy()

        if heuristic_id:
            relevant_entries = [
                e for e in relevant_entries
                if e.get("heuristic_id") == heuristic_id
            ]

        query_lower = query.lower()
        scored_entries = []

        for entry in relevant_entries:
            score = 0
            content = entry["content"].lower()
            category = entry["category"].lower()

            if heuristic_id and entry.get("heuristic_id") == heuristic_id:
                score += 3

            if any(word in content for word in query_lower.split()):
                score += 2

            if any(word in category for word in query_lower.split()):
                score += 1

            if score > 0:
                scored_entries.append((entry, score))

        scored_entries.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in scored_entries[:top_k]]

    async def add_expert_feedback(
        self,
        ui_pattern: str,
        violation_type: str,
        expert_rationale: str,
        heuristic_id: str
    ):
        entry = {
            "id": f"kb_{len(self.knowledge_entries) + 1:03d}",
            "category": f"Expert Feedback - {violation_type}",
            "content": expert_rationale,
            "ui_pattern": ui_pattern,
            "violation_type": violation_type,
            "heuristic_id": heuristic_id,
            "source": "expert_validation",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        self.knowledge_entries.append(entry)
        self.logger.info(f"Added expert feedback entry: {entry['id']}")

    async def get_stats(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self.knowledge_entries),
            "by_heuristic": {},
            "index_initialized": self.index_initialized
        }
