"""
Firestore Service
Handles all Cloud Firestore operations for course data persistence.
"""
from google.cloud import firestore
import os
import logging

logger = logging.getLogger(__name__)

# Get GCP configuration from environment
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')

# Initialize Firestore client
# If GOOGLE_APPLICATION_CREDENTIALS is set, it will be used automatically
# Otherwise, it will use Application Default Credentials (ADC)
try:
    if PROJECT_ID:
        db = firestore.Client(project=PROJECT_ID)
        logger.info(f"Firestore initialized for project: {PROJECT_ID}")
    else:
        db = firestore.Client()
        logger.warning("GOOGLE_CLOUD_PROJECT not set, using default project")
except Exception as e:
    logger.error(f"Failed to initialize Firestore: {e}")
    db = None

COURSES_COLLECTION = 'courses'


def _ensure_db():
    """Ensure database is initialized."""
    if db is None:
        raise RuntimeError(
            "Firestore not initialized. Please check GOOGLE_CLOUD_PROJECT "
            "and GOOGLE_APPLICATION_CREDENTIALS environment variables."
        )


def get_course_state(course_id: str) -> str:
    """
    Returns the current state of the course.
    
    Args:
        course_id: The Canvas course ID (context_id)
        
    Returns:
        One of: 'NEEDS_INIT', 'GENERATING', 'ACTIVE'
    """
    _ensure_db()
    doc = db.collection(COURSES_COLLECTION).document(course_id).get()
    
    if not doc.exists:
        return 'NEEDS_INIT'
    status = doc.get('status')
    if status == 'GENERATING':
        return 'GENERATING'
    elif status == 'ACTIVE':
        return 'ACTIVE'
    else:
        return 'NOT_READY'



def create_course_doc(course_id: str) -> None:
    """
    Creates the initial course document with GENERATING status.
    
    Args:
        course_id: The Canvas course ID
    """
    _ensure_db()
    #sets status to GENERATING
    db.collection(COURSES_COLLECTION).document(course_id).set({
        'status': 'GENERATING'
    })


# returns the google.cloud.firestore.document.DocumentSnapshot class
def get_course_data(course_id: str):
    """
    Fetches the complete course document.
    
    Args:
        course_id: The Canvas course ID
        
    Returns:
        DocumentSnapshot containing all course data
    """
    _ensure_db()
    return db.collection(COURSES_COLLECTION).document(course_id).get()




# call with dictionary of:
# corpus_id, indexed_files, kg_nodes, kg_edges, kg_data
def finalize_course_doc(course_id: str, data: dict) -> None:
    """
    Updates the course document with all RAG/KG data and sets status to ACTIVE.
    
    Args:
        course_id: The Canvas course ID
        data: Dictionary containing corpus_id, indexed_files, kg_nodes, kg_edges, kg_data
    """
    _ensure_db()
    db.collection(COURSES_COLLECTION).document(course_id).update({
        'status': 'ACTIVE',
        'corpus_id': data.get('corpus_id'),
        'indexed_files': data.get('indexed_files'),
        'kg_nodes': data.get('kg_nodes'),
        'kg_edges': data.get('kg_edges'),
        'kg_data': data.get('kg_data')
    })



if __name__ == "__main__":
    # Test Firestore credentials and connection
    from dotenv import load_dotenv
    
    print("="*70)
    print("FIRESTORE SERVICE TEST")
    print("="*70)
    
    # Load environment variables
    load_dotenv()
    
    # Re-initialize after loading env
    PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    print(f"\nEnvironment Variables:")
    print(f"  GOOGLE_CLOUD_PROJECT: {PROJECT_ID or 'NOT SET'}")

    db = firestore.Client(project=PROJECT_ID)
    test_course_id = 'test_course_12345'

    print(f"Creating course document for {test_course_id}...")
    create_course_doc(test_course_id)
    print("Course document created.")
    state = get_course_state(test_course_id)
    print(f"Course state: {state}")
    
    mock_data = {
        'corpus_id': 'mock_corpus_001',
        'indexed_files': {'file1.pdf': 'gcs://bucket/file1.pdf'},
        'kg_nodes': [{'id': 'node1', 'label': 'Topic 1'}],
        'kg_edges': [{'source': 'node1', 'target': 'node2', 'relation': 'related_to'}],
        'kg_data': {'summary': 'This is a mock knowledge graph.'}
    }
    finalize_course_doc(test_course_id, mock_data)

    course_data = get_course_data(test_course_id)
    print(f"\nFinal Course Document Data for {test_course_id}:")
    print(course_data.to_dict())