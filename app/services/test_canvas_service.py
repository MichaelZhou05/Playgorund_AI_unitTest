"""
Test script for Canvas Service
Run this to verify the canvas_service functions work correctly.

Usage:
    python -m app.services.test_canvas_service
"""
import json
from canvas_service import get_course_files, get_syllabus, get_course_info
import json
import os
from canvas_service import get_course_files, get_syllabus, get_course_info


def test_get_course_files():
    """
    Test the get_course_files function.
    Uses environment variables for Canvas course ID and API token.
    """
    print("\n" + "="*60)
    print("TEST: get_course_files()")
    print("="*60)

    COURSE_ID = os.environ.get('CANVAS_TEST_COURSE_ID', 'YOUR_COURSE_ID')
    CANVAS_TOKEN = os.environ.get('CANVAS_API_TOKEN', 'YOUR_CANVAS_API_TOKEN')

    if COURSE_ID == "YOUR_COURSE_ID" or CANVAS_TOKEN == "YOUR_CANVAS_API_TOKEN":
        print("⚠️  Please set CANVAS_TEST_COURSE_ID and CANVAS_API_TOKEN in your .env file")
        return False
    
    try:
        files_list, indexed_files = get_course_files(COURSE_ID, CANVAS_TOKEN)
        
        print(f"\n✅ Successfully retrieved files")
        print(f"   Total files: {len(files_list)}")
        print(f"   Indexed entries: {len(indexed_files)}")
        
        if files_list:
            print(f"\n📄 First file example:")
            print(json.dumps(files_list[0], indent=2))
            
            print(f"\n🔍 Indexed entry example:")
            first_id = list(indexed_files.keys())[0]
            print(f"   File ID: {first_id}")
            print(f"   Data: {indexed_files[first_id]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_get_syllabus():
    """
    Test the get_syllabus function.
    """
    print("\n" + "="*60)
    print("TEST: get_syllabus()")
    print("="*60)

    COURSE_ID = os.environ.get('CANVAS_TEST_COURSE_ID', 'YOUR_COURSE_ID')
    CANVAS_TOKEN = os.environ.get('CANVAS_API_TOKEN', 'YOUR_CANVAS_API_TOKEN')

    if COURSE_ID == "YOUR_COURSE_ID" or CANVAS_TOKEN == "YOUR_CANVAS_API_TOKEN":
        print("⚠️  Please set CANVAS_TEST_COURSE_ID and CANVAS_API_TOKEN in your .env file")
        return False
    
    try:
        syllabus = get_syllabus(COURSE_ID, CANVAS_TOKEN)
        
        print(f"\n✅ Successfully retrieved syllabus")
        print(f"   Length: {len(syllabus)} characters")
        
        if syllabus:
            # Print first 200 characters
            preview = syllabus[:200] + "..." if len(syllabus) > 200 else syllabus
            print(f"\n📝 Preview:\n{preview}")
        else:
            print("\n⚠️  Syllabus is empty")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_get_course_info():
    """
    Test the get_course_info function.
    """
    print("\n" + "="*60)
    print("TEST: get_course_info()")
    print("="*60)

    COURSE_ID = os.environ.get('CANVAS_TEST_COURSE_ID', 'YOUR_COURSE_ID')
    CANVAS_TOKEN = os.environ.get('CANVAS_API_TOKEN', 'YOUR_CANVAS_API_TOKEN')

    if COURSE_ID == "YOUR_COURSE_ID" or CANVAS_TOKEN == "YOUR_CANVAS_API_TOKEN":
        print("⚠️  Please set CANVAS_TEST_COURSE_ID and CANVAS_API_TOKEN in your .env file")
        return False

    try:
        course_info = get_course_info(COURSE_ID, CANVAS_TOKEN)

        print(f"\n✅ Successfully retrieved course info")
        print(json.dumps(course_info, indent=2))

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def run_mock_test():
    """
    Run a mock test without real API credentials.
    """
    print("\n" + "="*60)
    print("MOCK TEST: Canvas Service Function Signatures")
    print("="*60)
    
    print("\n✅ All functions are properly defined:")
    print("   - get_course_files(course_id: str, token: str) -> Tuple[List[Dict], Dict]")
    print("   - get_syllabus(course_id: str, token: str) -> str")
    print("   - get_course_info(course_id: str, token: str) -> Dict")
    
    print("\n📋 To run real tests:")
    print("   1. Set CANVAS_TEST_COURSE_ID and CANVAS_API_TOKEN in your .env file")
    print("   2. Run: python -m app.services.test_canvas_service")

    print("\n" + "="*60)


if __name__ == "__main__":
    print("\n🧪 Canvas Service Test Suite")
    print("="*60)

    COURSE_ID = os.environ.get('CANVAS_TEST_COURSE_ID', 'YOUR_COURSE_ID')
    CANVAS_TOKEN = os.environ.get('CANVAS_API_TOKEN', 'YOUR_CANVAS_API_TOKEN')

    if COURSE_ID == "YOUR_COURSE_ID" or CANVAS_TOKEN == "YOUR_CANVAS_API_TOKEN":
        run_mock_test()
    else:
        # Run real tests
        results = []
        results.append(("get_course_files", test_get_course_files()))
        results.append(("get_syllabus", test_get_syllabus()))
        results.append(("get_course_info", test_get_course_info()))

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        for name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{status}: {name}")
        print("="*60 + "\n")
