"""
Canvas API Service
Handles all Canvas API calls for fetching course materials.
"""
import requests


CANVAS_API_BASE = "https://canvas.instructure.com/api/v1"


def get_course_files(course_id: str, token: str) -> list:
    """
    Fetches all files from a Canvas course.
    
    Args:
        course_id: The Canvas course ID
        token: Canvas API access token
        
    Returns:
        List of file objects with id, name, url, etc.
    """
    # TODO: Implement Canvas API call
    # GET /api/v1/courses/:course_id/files
    
    return []


def get_syllabus(course_id: str, token: str) -> str:
    """
    Fetches the syllabus text from a Canvas course.
    
    Args:
        course_id: The Canvas course ID
        token: Canvas API access token
        
    Returns:
        Syllabus text (string)
    """
    # TODO: Implement Canvas API call
    # GET /api/v1/courses/:course_id
    # Extract syllabus_body from response
    
    return ""
