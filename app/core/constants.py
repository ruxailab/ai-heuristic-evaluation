from enum import Enum

class SeverityLevel(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"

class HeuristicId(Enum):
    H1_VISIBILITY_OF_SYSTEM_STATUS = "H1"
    H2_MATCH_BETWEEN_SYSTEM_AND_REAL_WORLD = "H2"
    H3_USER_CONTROL_AND_FREEDOM = "H3"
    H4_CONSISTENCY_AND_STANDARDS = "H4"
    H5_ERROR_PREVENTION = "H5"
    H6_RECOGNITION_RATHER_THAN_RECALL = "H6"
    H7_FLEXIBILITY_AND_EFFICIENCY_OF_USE = "H7"
    H8_AESTHETIC_AND_MINIMALIST_DESIGN = "H8"
    H9_HELP_USERS_RECOGNIZE_RECOVER_FROM_ERRORS = "H9"
    H10_HELP_AND_DOCUMENTATION = "H10"

NIELSEN_HEURISTICS = {
    HeuristicId.H1_VISIBILITY_OF_SYSTEM_STATUS: {
        "name": "Visibility of System Status",
        "description": "The design should always keep users informed about what is going on, through appropriate feedback within a reasonable amount of time.",
        "measurable_criteria": [
            {
                "id": "H1.1",
                "description": "Loading states visible",
                "evaluation": "Check if loading indicators are present during async operations",
                "severity_weights": {"critical": 10, "major": 5, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H1.2",
                "description": "System feedback for user actions",
                "evaluation": "Verify visual/audio feedback for button clicks, form submissions, etc.",
                "severity_weights": {"critical": 10, "major": 6, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H1.3",
                "description": "Progress indicators for multi-step processes",
                "evaluation": "Check for progress bars, step counters in wizards, forms, checkouts",
                "severity_weights": {"critical": 8, "major": 5, "minor": 2, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H2_MATCH_BETWEEN_SYSTEM_AND_REAL_WORLD: {
        "name": "Match Between System and Real World",
        "description": "The design should speak the users' language. Use words, phrases, and concepts familiar to the user, rather than internal jargon.",
        "measurable_criteria": [
            {
                "id": "H2.1",
                "description": "Use of familiar icons and metaphors",
                "evaluation": "Icons should match real-world conventions (house for home, gear for settings)",
                "severity_weights": {"critical": 8, "major": 5, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H2.2",
                "description": "Natural language instead of technical terms",
                "evaluation": "User-facing text uses everyday language, not technical jargon",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H2.3",
                "description": "Information organization follows user mental models",
                "evaluation": "Content grouped logically from user's perspective",
                "severity_weights": {"critical": 10, "major": 6, "minor": 3, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H3_USER_CONTROL_AND_FREEDOM: {
        "name": "User Control and Freedom",
        "description": "Users often perform actions by mistake. They need a clearly marked 'emergency exit' to leave the action without having to go through an extended process.",
        "measurable_criteria": [
            {
                "id": "H3.1",
                "description": "Undo/redo functionality available",
                "evaluation": "Users can reverse actions easily (back button, cancel, undo)",
                "severity_weights": {"critical": 10, "major": 7, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H3.2",
                "description": "Clear navigation exit points",
                "evaluation": "Users can exit processes without being trapped",
                "severity_weights": {"critical": 10, "major": 7, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H3.3",
                "description": "Confirmation for destructive actions",
                "evaluation": "Delete/remove actions have confirmation dialogs",
                "severity_weights": {"critical": 10, "major": 6, "minor": 2, "cosmetic": 1}
            }
        ]
    }
}
