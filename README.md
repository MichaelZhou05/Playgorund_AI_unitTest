# Canvas TA-Bot

A Canvas-integrated LTI app that indexes course materials into a Vertex AI RAG Engine and generates an interactive Knowledge Graph for students to explore course content.

## 📂 Repository Structure

```
/canvas-ta-bot/
|
|-- /app                   # Main Flask application package
|   |
|   |-- /static/           # CSS, JS, and libraries
|   |   |-- style.css
|   |   |-- app.js         # All frontend JS logic
|   |   |-- vis-network.min.js
|   |
|   |-- /templates/        # Flask HTML templates
|   |   |-- index.html     # Main UI file
|   |
|   |-- /services/         # Core business logic
|   |   |-- __init__.py
|   |   |-- rag_service.py       # Vertex AI RAG SDK calls
|   |   |-- kg_service.py        # networkx graph logic
|   |   |-- firestore_service.py # Firestore operations
|   |   |-- canvas_service.py    # Canvas API calls
|   |
|   |-- __init__.py        # Flask app initialization
|   |-- routes.py          # All Flask API routes
|
|-- requirements.txt       # Python dependencies
|-- service-account.json   # GCP auth key (not tracked)
|-- .gitignore
|-- README.md
```

## 🤝 API Contracts

### Frontend <-> Backend (HTTP API)

| Endpoint | Method | Request Body | Response Body |
|----------|--------|--------------|---------------|
| `/api/initialize-course` | POST | `{ "course_id": "str", "topics": "str" }` | `{ "status": "complete" }` |
| `/api/chat` | POST | `{ "course_id": "str", "query": "str" }` | `{ "answer": "str", "sources": ["str", "str"] }` |
| `/api/get-graph` | GET | Query param: `?course_id=str` | `{ "nodes": "json-str", "edges": "json-str", "data": "json-str" }` |

### Backend Internal API (Python Functions)

#### firestore_service.py
- `get_course_state(course_id: str) -> str`: Returns the STATE (e.g., NEEDS_INIT, ACTIVE)
- `create_course_doc(course_id: str)`: Creates initial doc with status: GENERATING
- `get_course_data(course_id: str) -> DocumentSnapshot`: Fetches the whole course doc
- `finalize_course_doc(course_id: str, data: dict)`: Updates doc with RAG/KG data and sets status: ACTIVE

#### rag_service.py
- `create_and_provision_corpus(files: list) -> str`: Creates corpus, uploads files, returns corpus_id
- `query_rag_corpus(corpus_id: str, query: str) -> (str, list)`: Returns (answer_text, [source_names])

#### kg_service.py
- `build_knowledge_graph(topic_list: list, corpus_id: str, files: list) -> (str, str, str)`: Returns (nodes_json, edges_json, data_json)

#### canvas_service.py
- `get_course_files(course_id: str, token: str) -> list`: Fetches all file objects from Canvas
- `get_syllabus(course_id: str, token: str) -> str`: Fetches syllabus text

## 🚀 Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up GCP credentials:
   - Place your `service-account.json` in the root directory

3. Run the Flask app:
   ```bash
   python -m flask run
   ```

## 👥 Team Roles

- **Role 1 (Frontend)**: `app/templates/index.html` and `app/static/app.js`
- **Role 2 (API Router)**: `app/routes.py`
- **Role 3 (Core Services)**: All files in `app/services/`
