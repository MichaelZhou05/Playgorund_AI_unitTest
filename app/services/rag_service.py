"""
RAG Service
Handles all Vertex AI RAG Engine operations.
"""
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils.resources import RagCorpus, RagFile
from vertexai.generative_models import GenerativeModel
import os
import io
import requests
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

# Initialize Vertex AI with environment variables
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')

if project_id:
    vertexai.init(project=project_id, location=location)
    logger.info(f"Vertex AI initialized: project={project_id}, location={location}")
else:
    logger.warning("GOOGLE_CLOUD_PROJECT not set - Vertex AI not initialized")


def create_and_provision_corpus(files: list, canvas_token: str) -> str:
    """
    Creates a new RAG corpus and uploads all course files.
    
    Args:
        files: List of file objects from Canvas API (with keys: id, display_name, url, etc.)
        canvas_token: Canvas API token for downloading files
        
    Returns:
        The corpus resource name (string) e.g., "projects/.../ragCorpora/..."
        
    Raises:
        Exception: If corpus creation or file upload fails
    """
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    try:
        # Create a new RAG corpus
        logger.info("Creating new RAG corpus...")
        corpus = rag.create_corpus(
            display_name=f"Canvas Course Corpus - {len(files)} files"
        )
        corpus_name = corpus.name
        logger.info(f"Created corpus: {corpus_name}")
        
        # Upload each file to the corpus
        for file in files:
            try:
                file_id = file.get('id')
                display_name = file.get('display_name', f"file_{file_id}")
                download_url = file.get('url')
                html_url = file.get('html_url', '')
                
                logger.info(f"Uploading file: {display_name} (ID: {file_id})")
                
                # Download file content from Canvas
                headers = {'Authorization': f'Bearer {canvas_token}'}
                response = requests.get(download_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Create in-memory file object
                file_bytes = io.BytesIO(response.content)
                file_bytes.name = display_name  # Set name attribute for upload
                
                # Import file to RAG corpus with metadata
                rag.import_files(
                    corpus_name=corpus_name,
                    paths=[file_bytes],
                    chunk_size=512,  # Optimal chunk size for retrieval
                    chunk_overlap=100,  # Overlap for context continuity
                    metadata={
                        'file_id': str(file_id),
                        'display_name': display_name,
                        'canvas_url': html_url
                    }
                )
                
                logger.info(f"Successfully uploaded: {display_name}")
                
            except Exception as e:
                logger.error(f"Failed to upload file {file.get('display_name')}: {str(e)}")
                # Continue with other files even if one fails
                continue
        
        logger.info(f"Corpus provisioning complete: {corpus_name}")
        return corpus_name
        
    except Exception as e:
        logger.error(f"Failed to create and provision corpus: {str(e)}")
        raise


def query_rag_corpus(corpus_id: str, query: str) -> Tuple[str, List[str]]:
    """
    Queries the RAG corpus and returns an answer with sources.
    
    Args:
        corpus_id: The RAG corpus resource name
        query: The user's question
        
    Returns:
        Tuple of (answer_text, list of source names)
        
    Raises:
        Exception: If query fails
    """
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    try:
        logger.info(f"Querying RAG corpus: {query[:100]}...")
        
        # Retrieve relevant contexts from the corpus
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_id,
                )
            ],
            text=query,
            similarity_top_k=10,  # Retrieve top 10 relevant chunks
            vector_distance_threshold=0.5,  # Similarity threshold
        )
        
        # Extract context text and citations
        contexts = response.contexts.contexts
        context_texts = [context.text for context in contexts]
        
        # Extract unique source files
        citations = []
        for context in contexts:
            if hasattr(context, 'source_metadata') and context.source_metadata:
                display_name = context.source_metadata.get('display_name')
                if display_name and display_name not in citations:
                    citations.append(display_name)
        
        logger.info(f"Retrieved {len(contexts)} context chunks from {len(citations)} sources")
        
        # Generate answer using Gemini with retrieved contexts
        model = GenerativeModel("gemini-1.5-flash")
        
        # Construct prompt with context and query
        combined_context = "\n\n".join(context_texts)
        prompt = f"""You are a helpful teaching assistant for a course. Answer the student's question using ONLY the provided course materials.

Course Materials Context:
{combined_context}

Student Question: {query}

Instructions:
1. Answer based ONLY on the provided context
2. Be clear, concise, and educational
3. If the context doesn't contain enough information, say so
4. Cite specific sources when possible

Answer:"""

        response = model.generate_content(prompt)
        answer_text = response.text
        
        logger.info(f"Generated answer with {len(citations)} citations")
        
        return (answer_text, citations)
        
    except Exception as e:
        logger.error(f"Failed to query RAG corpus: {str(e)}")
        raise


def query_rag_with_history(corpus_id: str, history: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Queries the RAG corpus with conversational history for context-aware answers.
    
    Args:
        corpus_id: The RAG corpus resource name
        history: List of message dicts with 'role' and 'content' keys
                 e.g., [{'role': 'user', 'content': 'What is...?'}, 
                        {'role': 'assistant', 'content': 'Answer...'}]
        
    Returns:
        Tuple of (answer_text, list of source names)
        
    Raises:
        Exception: If query fails
    """
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    if not history:
        raise ValueError("History cannot be empty")
    
    try:
        # Get the last user message for RAG retrieval
        last_user_message = None
        for msg in reversed(history):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content')
                break
        
        if not last_user_message:
            raise ValueError("No user message found in history")
        
        logger.info(f"Querying with history context: {last_user_message[:100]}...")
        
        # Retrieve relevant contexts based on latest query
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_id,
                )
            ],
            text=last_user_message,
            similarity_top_k=10,
            vector_distance_threshold=0.5,
        )
        
        # Extract context text and citations
        contexts = response.contexts.contexts
        context_texts = [context.text for context in contexts]
        
        # Extract unique source files
        citations = []
        for context in contexts:
            if hasattr(context, 'source_metadata') and context.source_metadata:
                display_name = context.source_metadata.get('display_name')
                if display_name and display_name not in citations:
                    citations.append(display_name)
        
        logger.info(f"Retrieved {len(contexts)} context chunks from {len(citations)} sources")
        
        # Generate answer using Gemini with full conversation history
        model = GenerativeModel("gemini-1.5-flash")
        
        # Construct prompt with history and context
        combined_context = "\n\n".join(context_texts)
        
        # Build conversation history string
        history_str = ""
        for msg in history[:-1]:  # All messages except the last
            role = "Student" if msg.get('role') == 'user' else "Assistant"
            history_str += f"{role}: {msg.get('content')}\n\n"
        
        prompt = f"""You are a helpful teaching assistant for a course. Answer the student's question using the provided course materials and conversation history.

Course Materials Context:
{combined_context}

Previous Conversation:
{history_str}

Current Student Question: {last_user_message}

Instructions:
1. Consider the conversation history for context
2. Answer based on the provided course materials
3. Be clear, concise, and educational
4. Maintain conversational flow from previous messages
5. If you need to refer back to previous answers, do so naturally

Answer:"""

        response = model.generate_content(prompt)
        answer_text = response.text
        
        logger.info(f"Generated conversational answer with {len(citations)} citations")
        
        return (answer_text, citations)
        
    except Exception as e:
        logger.error(f"Failed to query RAG corpus with history: {str(e)}")
        raise


def get_suggested_questions(topic: str) -> List[str]:
    """
    Generates AI-suggested follow-up questions for a given topic.
    
    Args:
        topic: The topic or subject area
        
    Returns:
        List of suggested question strings
        
    Raises:
        Exception: If question generation fails
    """
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
    
    try:
        logger.info(f"Generating suggested questions for topic: {topic}")
        
        model = GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""Generate 3 thoughtful follow-up questions that a student might have about the topic: "{topic}"

Requirements:
1. Questions should be educational and promote deeper understanding
2. Questions should be specific and relevant to the topic
3. Questions should be suitable for a teaching assistant to answer
4. Each question should be on a new line
5. Do not number the questions

Topic: {topic}

Questions:"""

        response = model.generate_content(prompt)
        
        # Parse response into list of questions
        questions = [q.strip() for q in response.text.strip().split('\n') if q.strip()]
        
        # Remove any numbering that might have been added
        cleaned_questions = []
        for q in questions:
            # Remove common numbering patterns
            import re
            cleaned = re.sub(r'^\d+[\.)]\s*', '', q)
            cleaned = re.sub(r'^[-*]\s*', '', cleaned)
            if cleaned:
                cleaned_questions.append(cleaned)
        
        logger.info(f"Generated {len(cleaned_questions)} suggested questions")
        
        return cleaned_questions[:3]  # Return max 3 questions
        
    except Exception as e:
        logger.error(f"Failed to generate suggested questions: {str(e)}")
        raise
