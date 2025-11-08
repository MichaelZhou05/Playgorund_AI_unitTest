"""
Test script for the course initialization pipeline.
Tests the initialize_course logic without running the Flask app.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from app.services import firestore_service, rag_service, kg_service, canvas_service, gcs_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get Canvas API token from environment
CANVAS_TOKEN = os.environ.get('CANVAS_API_TOKEN')


def test_initialize_course(course_id: str, topics: str):
    """
    Test the course initialization pipeline.
    
    Args:
        course_id: The Canvas course ID
        topics: Newline-separated list of topics
        
    Returns:
        dict: Result dictionary with status and info
    """
    try:
        if not course_id:
            raise ValueError("course_id is required")
        
        if not CANVAS_TOKEN:
            raise ValueError("CANVAS_API_TOKEN environment variable not set")
        
        logger.info(f"Starting initialization for course {course_id}")
        logger.info(f"Topics: {topics}")
        
        # Step 1: Create Firestore doc with status: GENERATING
        logger.info("\n" + "="*70)
        logger.info("Step 1: Creating Firestore document...")
        logger.info("="*70)
        firestore_service.create_course_doc(course_id)
        logger.info("✓ Firestore document created with status: GENERATING")
        
        # Step 2: Download course files from Canvas (downloads to local storage)
        logger.info("\n" + "="*70)
        logger.info("Step 2: Fetching course files from Canvas...")
        logger.info("="*70)
        files, indexed_files_map = canvas_service.get_course_files(
            course_id=course_id,
            token=CANVAS_TOKEN,
            download=True  # Downloads files locally and adds local_path
        )
        
        if not files:
            logger.warning(f"No files found for course {course_id}")
            raise ValueError("No course files found")
        
        logger.info(f"✓ Retrieved {len(files)} files from Canvas")
        for f in files[:3]:  # Show first 3 files
            logger.info(f"  - {f.get('display_name')} (ID: {f.get('id')})")
        if len(files) > 3:
            logger.info(f"  ... and {len(files) - 3} more files")
        
        # Step 3: Upload files to Google Cloud Storage (GCS)
        logger.info("\n" + "="*70)
        logger.info("Step 3: Uploading files to Google Cloud Storage...")
        logger.info("="*70)
        files = gcs_service.upload_course_files(files, course_id)
        
        # Count successful uploads
        successful_uploads = sum(1 for f in files if f.get('gcs_uri'))
        logger.info(f"✓ Uploaded {successful_uploads}/{len(files)} files to GCS")
        
        # Step 4: Create RAG corpus and import files from GCS
        logger.info("\n" + "="*70)
        logger.info("Step 4: Creating RAG corpus and importing files...")
        logger.info("="*70)
        corpus_id = rag_service.create_and_provision_corpus(
            files=files,
            corpus_name_suffix=f"Course {course_id}"
        )
        logger.info(f"✓ Created corpus: {corpus_id}")
        
        # Step 5: Build knowledge graph
        logger.info("\n" + "="*70)
        logger.info("Step 5: Building knowledge graph...")
        logger.info("="*70)
        # Split topics string into a list (comma-separated, for consistency with routes.py)
        topic_list = topics.split(",")
        kg_nodes, kg_edges, kg_data = kg_service.build_knowledge_graph(
            topic_list=topic_list,
            corpus_id=corpus_id,
            files=files
        )
        logger.info("✓ Knowledge graph built successfully")
        
        # Step 6: Clean up local files
        logger.info("\n" + "="*70)
        logger.info("Step 6: Cleaning up local files...")
        logger.info("="*70)
        local_dir = os.path.join('app', 'data', 'courses', course_id)
        if os.path.exists(local_dir):
            import shutil
            shutil.rmtree(local_dir)
            logger.info(f"✓ Deleted local directory: {local_dir}")
        else:
            logger.info("✓ No local files to clean up")
        
        # Step 7: Clean up GCS files (optional - comment out if you want to keep them)
        logger.info("\n" + "="*70)
        logger.info("Step 7: Cleaning up GCS files...")
        logger.info("="*70)
        gcs_service.delete_course_files(course_id)
        logger.info("✓ GCS files deleted")
        
        # Step 8: Finalize Firestore document with all data
        logger.info("\n" + "="*70)
        logger.info("Step 8: Finalizing Firestore document...")
        logger.info("="*70)
        update_payload = {
            'corpus_id': corpus_id,
            'indexed_files': indexed_files_map,
            'kg_nodes': kg_nodes,
            'kg_edges': kg_edges,
            'kg_data': kg_data
        }
        firestore_service.finalize_course_doc(course_id, update_payload)
        logger.info("✓ Firestore document updated with status: ACTIVE")
        
        logger.info("\n" + "="*70)
        logger.info(f"🎉 Course {course_id} initialization complete!")
        logger.info("="*70)
        
        result = {
            "status": "complete",
            "corpus_id": corpus_id,
            "files_count": len(files),
            "uploaded_count": successful_uploads
        }
        
        logger.info(f"\nResult: {result}")
        return result
        
    except Exception as e:
        logger.error(f"\n❌ Error initializing course {course_id}: {str(e)}", exc_info=True)
        
        # Try to update Firestore with error status
        try:
            firestore_service.db.collection(firestore_service.COURSES_COLLECTION).document(course_id).update({
                'status': 'ERROR',
                'error_message': str(e)
            })
            logger.info("Updated Firestore with error status")
        except Exception as firestore_error:
            logger.error(f"Failed to update Firestore with error: {firestore_error}")
        
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test parameters
    # Replace these with your actual course ID and topics
    TEST_COURSE_ID = os.environ.get('CANVAS_TEST_COURSE_ID', '12345')
    TEST_TOPICS = """Permutations
Combinations
Binomial Coefficients
Counting Techniques
"""
    
    print("\n" + "="*70)
    print("TESTING COURSE INITIALIZATION PIPELINE")
    print("="*70)
    print(f"Course ID: {TEST_COURSE_ID}")
    print(f"Topics:\n{TEST_TOPICS}")
    print("="*70 + "\n")
    
    # Run the test
    result = test_initialize_course(TEST_COURSE_ID, TEST_TOPICS)
    
    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'complete':
        print(f"Corpus ID: {result.get('corpus_id')}")
        print(f"Files Count: {result.get('files_count')}")
        print(f"Uploaded Count: {result.get('uploaded_count')}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*70)
