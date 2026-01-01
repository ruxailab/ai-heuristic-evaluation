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
    },
    HeuristicId.H4_CONSISTENCY_AND_STANDARDS: {
        "name": "Consistency and Standards",
        "description": "Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform and industry conventions.",
        "measurable_criteria": [
            {
                "id": "H4.1",
                "description": "Consistent button dimensions",
                "evaluation": "Buttons of the same type (primary, secondary) should have uniform width/height",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H4.2",
                "description": "Consistent typography",
                "evaluation": "Similar elements (headings, body text, labels) use consistent font sizes and styles",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H4.3",
                "description": "Consistent color usage",
                "evaluation": "Same colors used for same purposes (e.g., primary action buttons same color)",
                "severity_weights": {"critical": 8, "major": 5, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H4.4",
                "description": "Consistent terminology",
                "evaluation": "Same terms used for same actions across the interface (not mix of Save/Submit, Delete/Remove)",
                "severity_weights": {"critical": 8, "major": 5, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H4.5",
                "description": "Platform conventions followed",
                "evaluation": "UI follows established platform patterns (navigation placement, icon usage)",
                "severity_weights": {"critical": 10, "major": 6, "minor": 3, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H5_ERROR_PREVENTION: {
        "name": "Error Prevention",
        "description": "Even better than good error messages is a careful design which prevents a problem from occurring in the first place.",
        "measurable_criteria": [
            {
                "id": "H5.1",
                "description": "Input validation before submission",
                "evaluation": "Form fields validate input format before allowing submission (email, phone, required fields)",
                "severity_weights": {"critical": 10, "major": 6, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H5.2",
                "description": "Constraints on input fields",
                "evaluation": "Input fields have appropriate constraints (max length, input type, allowed characters)",
                "severity_weights": {"critical": 8, "major": 5, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H5.3",
                "description": "Confirmation for high-risk actions",
                "evaluation": "Irreversible or significant actions require explicit confirmation",
                "severity_weights": {"critical": 10, "major": 7, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H5.4",
                "description": "Default values and suggestions",
                "evaluation": "Fields provide sensible defaults or suggestions to reduce user errors",
                "severity_weights": {"critical": 4, "major": 3, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H5.5",
                "description": "Disable invalid options",
                "evaluation": "Options that are not available are disabled rather than hidden, preventing confusion",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H6_RECOGNITION_RATHER_THAN_RECALL: {
        "name": "Recognition Rather Than Recall",
        "description": "Minimize the user's memory load by making objects, actions, and options visible. The user should not have to remember information from one part of the dialogue to another.",
        "measurable_criteria": [
            {
                "id": "H6.1",
                "description": "Menu options visible",
                "evaluation": "Important navigation and actions are visible or easily retrievable without memory load",
                "severity_weights": {"critical": 8, "major": 5, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H6.2",
                "description": "Contextual help",
                "evaluation": "Instructions or help text is visible in context when relevant",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H7_FLEXIBILITY_AND_EFFICIENCY_OF_USE: {
        "name": "Flexibility and Efficiency of Use",
        "description": "Accelerators—unseen by the novice user—may often speed up the interaction for the expert user such that the system can cater to both inexperienced and experienced users.",
        "measurable_criteria": [
            {
                "id": "H7.1",
                "description": "Shortcuts and accelerators",
                "evaluation": "Keyboard shortcuts or quick actions available for frequent tasks",
                "severity_weights": {"critical": 4, "major": 3, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H7.2",
                "description": "Customization options",
                "evaluation": "Users can tailor frequent actions or views to their needs",
                "severity_weights": {"critical": 4, "major": 3, "minor": 2, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H8_AESTHETIC_AND_MINIMALIST_DESIGN: {
        "name": "Aesthetic and Minimalist Design",
        "description": "Dialogues should not contain information which is irrelevant or rarely needed. Every extra unit of information in a dialogue competes with the relevant units of information.",
        "measurable_criteria": [
            {
                "id": "H8.1",
                "description": "Minimalist layout",
                "evaluation": "Visual layout is not cluttered; white space is used effectively",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H8.2",
                "description": "High signal-to-noise ratio",
                "evaluation": "Content is focused on the user's current task; irrelevant info is removed",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H9_HELP_USERS_RECOGNIZE_RECOVER_FROM_ERRORS: {
        "name": "Help Users Recognize, Diagnose, and Recover from Errors",
        "description": "Error messages should be expressed in plain language (no codes), precisely indicate the problem, and constructively suggest a solution.",
        "measurable_criteria": [
            {
                "id": "H9.1",
                "description": "Plain language errors",
                "evaluation": "Error messages use human-readable language, not codes",
                "severity_weights": {"critical": 10, "major": 6, "minor": 3, "cosmetic": 1}
            },
            {
                "id": "H9.2",
                "description": "Constructive solutions",
                "evaluation": "Errors suggest how to fix the problem, not just what went wrong",
                "severity_weights": {"critical": 10, "major": 7, "minor": 3, "cosmetic": 1}
            }
        ]
    },
    HeuristicId.H10_HELP_AND_DOCUMENTATION: {
        "name": "Help and Documentation",
        "description": "Even though it is better if the system can be used without documentation, it may be necessary to provide help and documentation.",
        "measurable_criteria": [
            {
                "id": "H10.1",
                "description": "Easy to search help",
                "evaluation": "Help documentation is easy to search and navigate",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            },
            {
                "id": "H10.2",
                "description": "Task-focused documentation",
                "evaluation": "Documentation focuses on user tasks and concrete steps",
                "severity_weights": {"critical": 6, "major": 4, "minor": 2, "cosmetic": 1}
            }
        ]
    }
}
