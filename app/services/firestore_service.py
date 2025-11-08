"""
Firestore Service
Handles all Cloud Firestore operations for course data persistence.
"""
from google.cloud import firestore


# Initialize Firestore client
db = firestore.Client()
COURSES_COLLECTION = 'courses'


def get_course_state(course_id: str) -> str:
    """
    Returns the current state of the course.
    
    Args:
        course_id: The Canvas course ID (context_id)
        
    Returns:
        One of: 'NEEDS_INIT', 'NOT_READY', 'GENERATING', 'ACTIVE'
    """
    doc = db.collection(COURSES_COLLECTION).document(course_id).get()
    
    if not doc.exists:
        # TODO: Determine if user is professor or student
        # For now, return NEEDS_INIT
        return 'NEEDS_INIT'
    
    status = doc.get('status')
    if status == 'GENERATING':
        return 'GENERATING'
    elif status == 'ACTIVE':
        return 'ACTIVE'
    else:
        return 'NOT_READY'


def create_course_doc(course_id: str):
    """
    Creates the initial course document with GENERATING status.
    
    Args:
        course_id: The Canvas course ID
    """
    db.collection(COURSES_COLLECTION).document(course_id).set({
        'status': 'GENERATING'
    })


def get_course_data(course_id: str):
    """
    Fetches the complete course document.
    
    Args:
        course_id: The Canvas course ID
        
    Returns:
        DocumentSnapshot containing all course data
    """
    return db.collection(COURSES_COLLECTION).document(course_id).get()


def finalize_course_doc(course_id: str, data: dict):
    """
    Updates the course document with all RAG/KG data and sets status to ACTIVE.
    
    Args:
        course_id: The Canvas course ID
        data: Dictionary containing corpus_id, indexed_files, kg_nodes, kg_edges, kg_data
    """
    db.collection(COURSES_COLLECTION).document(course_id).update({
        'status': 'ACTIVE',
        'corpus_id': data.get('corpus_id'),
        'indexed_files': data.get('indexed_files'),
        'kg_nodes': data.get('kg_nodes'),
        'kg_edges': data.get('kg_edges'),
        'kg_data': data.get('kg_data')
    })
