# AI Heuristic Evaluation System

An AI-powered heuristic evaluation tool that systematically evaluates digital interfaces against Nielsen's 10 Usability Heuristics using computer vision and LLMs.

## Overview

This system combines Microsoft's OmniParser for UI element detection with LLM-based analysis to provide automated heuristic evaluation. It integrates seamlessly with RUXAILAB's existing UX testing platform.

## Features

### Phase 1 Implementation (Complete)

**Nielsen's Heuristics H1-H3 Mapped**
- H1: Visibility of System Status
- H2: Match Between System and Real World
- H3: User Control and Freedom

**UI Element Detection Pipeline**
- OmniParser integration for detecting UI components
- Structured element classification (buttons, inputs, links, etc.)
- Layout hierarchy analysis

**Heuristic Evaluation Engine**
- Rule-based violation detection
- Severity scoring (Critical, Major, Minor, Cosmetic)
- 0-100 scoring per heuristic with explanations

**RAG-Based Knowledge Base**
- Expert-validated evaluation patterns
- Continuous learning from feedback
- Context-aware evaluation assistance

**Firebase Integration**
- Callable Cloud Functions for RUXAILAB integration
- Firestore storage for evaluation results
- Seamless API layer

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    RUXAILAB Frontend                     │
│              (Vue 3 + Vuetify)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Firebase Cloud Functions                     │
│  • evaluateHeuristicAI  • detectUIElements               │
│  • getHeuristicsMetadata  • getKnowledgeBaseStats        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AI Heuristic Evaluation Service              │
│              (FastAPI + Python)                          │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ OmniParser   │  │ Heuristic    │  │ RAG Knowledge│  │
│  │ Client       │  │ Engine       │  │ Base         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Using the Development Script

```bash
chmod +x start-dev.sh
./start-dev.sh
```

This will start:
- RUXAILAB Vue.js app on http://localhost:8081
- AI Heuristic API on http://localhost:8000
- Firebase emulators on http://127.0.0.1:4000
- API docs at http://localhost:8000/docs

### Manual Setup

1. **Start AI Heuristic Service**
```bash
cd ai-heuristic-evaluation
pip install -r requirements.txt
python main.py
```

2. **Start RUXAILAB**
```bash
cd ../RUXAILAB
npm install
firebase emulators:start
npm run serve
```

## API Endpoints

### Health Check
- `GET /health/` - Service health status

### UI Element Detection
- `POST /api/v1/heuristic/detect-elements` - Detect UI elements in image
- `POST /api/v1/heuristic/analyze` - Analyze interface structure

### Heuristic Evaluation
- `POST /api/v1/evaluation/evaluate` - Evaluate heuristics on UI
- `GET /api/v1/evaluation/heuristics` - Get heuristics metadata
- `GET /api/v1/evaluation/knowledge-base/stats` - Get knowledge base stats

## Integration with RUXAILAB

### Step 1: Use the Client Library

```javascript
import AIHeuristicEvaluationClient from './path/to/AIHeuristicEvaluationClient';

const client = new AIHeuristicEvaluationClient();

// Evaluate a UI screenshot
const result = await client.evaluateImage(imageData, studyId, questionId);
console.log(result.data);
```

### Step 2: Display Results

Results are stored in Firestore collection `ai_heuristic_evaluations` with structure:

```json
{
  "studyId": "study_123",
  "questionId": "question_456",
  "aiEvaluation": {
    "overall_score": 75.5,
    "heuristic_scores": [
      {
        "heuristic_id": "H1",
        "score": 80,
        "percentage": 80.0,
        "violations": [
          {
            "heuristic_id": "H1",
            "criterion_id": "H1.2",
            "severity": "major",
            "description": "Button lacks hover state",
            "affected_elements": ["Submit"],
            "recommendation": "Add hover state for feedback"
          }
        ],
        "explanation": "Score 80/100 - 1 violation: major: Button lacks hover state"
      }
    ],
    "total_violations": 1,
    "critical_issues": 0
  },
  "createdAt": "2024-01-01T00:00:00Z",
  "source": "ai_heuristic"
}
```

## Example Usage

### Python Client

```python
import requests

# Upload and evaluate an image
with open('screenshot.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/evaluation/evaluate',
        files={'image': f}
    )

result = response.json()
print(f"Overall Score: {result['data']['overall_score']}")
print(f"Violations: {result['data']['total_violations']}")
```

### JavaScript Client (RUXAILAB)

```javascript
// Convert image to base64
const imageData = await fileToBase64(screenshotFile);

// Call evaluation function
const result = await client.evaluateImage(imageData, studyId, questionId);

// Display results in RUXAILAB UI
displayEvaluationResults(result.data);
```

## Evaluation Criteria

### H1: Visibility of System Status
- **H1.1**: Loading states visible (weight: 10)
- **H1.2**: System feedback for actions (weight: 10)
- **H1.3**: Progress indicators for processes (weight: 8)

### H2: Match Between System and Real World
- **H2.1**: Familiar icons and metaphors (weight: 8)
- **H2.2**: Natural language over technical terms (weight: 6)
- **H2.3**: User mental model organization (weight: 10)

### H3: User Control and Freedom
- **H3.1**: Undo/redo functionality (weight: 10)
- **H3.2**: Clear navigation exit points (weight: 10)
- **H3.3**: Confirmation for destructive actions (weight: 10)

## Scoring Algorithm

Each heuristic is scored 0-100 based on:
1. Count of violations per criterion
2. Severity level (Critical: 10, Major: 6, Minor: 3, Cosmetic: 1)
3. Total deduction from 100

Example:
```
H1 Score = 100 - (H1.2_violations * 10 + H1.1_violations * 8)
```

## Future Enhancements (Phases 2-4)

- **Phase 2**: Complete H4-H10 implementation
- **Phase 3**: PDF/JSON report generation, dataset benchmarking
- **Phase 4**: Full RUXAILAB UI integration, deployment

## Environment Configuration

Create `.env` file in `ai-heuristic-evaluation/` directory:

```env
OPENAI_API_KEY=your_openai_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/serviceAccountKey.json
LOG_LEVEL=INFO
```

## Project Structure

```
ai-heuristic-evaluation/
├── main.py                          # FastAPI entry point
├── requirements.txt                  # Python dependencies
├── app/
│   ├── core/
│   │   ├── config.py                # Configuration settings
│   │   └── constants.py             # Nielsen's heuristics definitions
│   ├── services/
│   │   ├── omniparser_client.py     # UI element detection
│   │   ├── heuristic_engine.py      # Evaluation engine
│   │   └── rag_knowledge_base.py    # RAG system
│   ├── api/
│   │   └── routes/                  # API endpoints
│   └── utils/
│       └── logging_config.py        # Logging setup
└── firebase-functions/
    ├── index.js                     # Cloud Functions
    ├── package.json
    └── AIHeuristicEvaluationClient.js  # RUXAILAB client library
```

## Logging

Logs are written to:
- Console output (development)
- `logs/app.log` (file logging)

## Testing

### Run API Tests

```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Interactive API docs
```

### Test with Sample Image

```python
import requests

with open('test_screenshot.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/evaluation/evaluate',
        files={'image': f}
    )
    print(response.json())
```

## Contributing

This is part of the RUXAILAB GSoC 2024 project. To contribute:

1. Follow the existing code patterns
2. Add comprehensive logging
3. Include tests for new features
4. Update documentation

## License

Part of RUXAILAB project - see main repository for license details.

## References

- Nielsen, J. (1994). "10 Usability Heuristics for User Interface Design"
- OmniParser: A Simple Screen Parsing Tool (Microsoft Research, 2024)
- Baymard Institute - LLM UX Evaluation Study (2023)
