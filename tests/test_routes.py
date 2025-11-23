import unittest
from unittest.mock import patch
import json

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

@patch('app.routes.firestore_service')
def test_launch_needs_init(mock_firestore_service, client):
    """Test the launch endpoint when course needs initialization"""
    mock_firestore_service.get_course_state.return_value = 'NEEDS_INIT'
    response = client.get('/launch?course_id=123&user_id=456&role=instructor')
    assert response.status_code == 200
    assert b'NEEDS_INIT' in response.data

@patch('app.routes.firestore_service')
def test_launch_active_student(mock_firestore_service, client):
    """Test the launch endpoint for an active course with a student"""
    mock_firestore_service.get_course_state.return_value = 'ACTIVE'
    response = client.get('/launch?course_id=123&user_id=456&role=student')
    assert response.status_code == 200
    assert b'student_view' in response.data

@patch('app.routes.firestore_service')
def test_launch_active_instructor(mock_firestore_service, client):
    """Test the launch endpoint for an active course with an instructor"""
    mock_firestore_service.get_course_state.return_value = 'ACTIVE'
    response = client.get('/launch?course_id=123&user_id=456&role=instructor')
    assert response.status_code == 200
    assert b'teacher_view' in response.data

@patch('app.routes.firestore_service')
@patch('app.routes.gemini_service')
def test_chat(mock_gemini_service, mock_firestore_service, client):
    """Test the chat endpoint"""
    mock_firestore_service.get_course_data.return_value.to_dict.return_value = {'corpus_id': 'test_corpus'}
    mock_gemini_service.generate_answer_with_context.return_value = ("Test answer", [])
    
    response = client.post('/api/chat', json={'course_id': '123', 'query': 'What is a test?'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['answer'] == 'Test answer'

@patch('app.routes.firestore_service')
@patch('app.routes.canvas_service')
@patch('app.routes.gcs_service')
@patch('app.routes.rag_service')
@patch('app.routes.kg_service')
@patch('app.routes.gemini_service')
def test_initialize_course(mock_gemini, mock_kg, mock_rag, mock_gcs, mock_canvas, mock_firestore, client):
    """Test the initialize course endpoint"""
    mock_canvas.get_course_files.return_value = ([{'id': '1', 'display_name': 'file1.pdf', 'local_path': '/fake/path'}], {'1': {}})
    mock_gcs.upload_course_files.return_value = [{'id': '1', 'display_name': 'file1.pdf', 'gcs_uri': 'gs://bucket/file1.pdf'}]
    mock_rag.create_and_provision_corpus.return_value = "corpus_id_123"
    mock_kg.build_knowledge_graph.return_value = ("nodes", "edges", "data")

    response = client.post('/api/initialize-course', json={'course_id': '123'})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'complete'
    assert data['corpus_id'] == 'corpus_id_123'

@patch('app.routes.firestore_service')
def test_get_graph(mock_firestore, client):
    """Test the get graph endpoint"""
    mock_firestore.get_course_data.return_value.get.side_effect = ['nodes', 'edges', 'data', 'indexed_files']

    response = client.get('/api/get-graph?course_id=123')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['nodes'] == 'nodes'
    assert data['edges'] == 'edges'
    assert data['data'] == 'data'

@patch('app.routes.gcs_service')
def test_download_source(mock_gcs, client):
    """Test the download source endpoint"""
    mock_gcs.generate_signed_url.return_value = "http://signed-url"
    
    response = client.get('/api/download-source?gcs_uri=gs://bucket/file.pdf')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['download_url'] == "http://signed-url"

@patch('app.routes.analytics_logging_service')
def test_rate_answer(mock_analytics, client):
    """Test the rate answer endpoint"""
    response = client.post('/api/rate-answer', json={'log_doc_id': '123', 'rating': 'helpful'})
    assert response.status_code == 200
    mock_analytics.rate_answer.assert_called_with('123', 'helpful')

@patch('app.routes.kg_service')
@patch('app.routes.firestore_service')
def test_remove_topic(mock_firestore, mock_kg, client):
    """Test the remove topic endpoint"""
    mock_firestore.get_course_data.return_value.exists = True
    mock_firestore.get_course_data.return_value.to_dict.return_value = {'status': 'ACTIVE', 'kg_nodes': '[]', 'kg_edges': '[]', 'kg_data': '{}'}
    mock_kg.remove_topic_from_graph.return_value = ("new_nodes", "new_edges", "new_data")

    response = client.post('/api/remove-topic', json={'course_id': '123', 'topic_id': 'topic_1'})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

@patch('app.routes.analytics_logging_service')
def test_log_node_click(mock_analytics, client):
    """Test the log node click endpoint"""
    response = client.post('/api/log-node-click', json={'course_id': '123', 'node_id': 'node_1', 'node_label': 'Node 1'})
    assert response.status_code == 200
    mock_analytics.log_kg_node_click.assert_called_with(course_id='123', node_id='node_1', node_label='Node 1', node_type=None)

@patch('app.routes.analytics_reporting_service')
def test_get_analytics(mock_reporting, client):
    """Test the get analytics endpoint"""
    mock_reporting.get_analytics_report.return_value = {'status': 'complete'}
    response = client.get('/api/analytics/123')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'complete'

@patch('app.routes.analytics_reporting_service')
def test_run_analytics(mock_reporting, client):
    """Test the run analytics endpoint"""
    mock_reporting.run_daily_analytics.return_value = {'status': 'complete'}
    response = client.post('/api/analytics/run', json={'course_id': '123'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'complete'

@patch('app.routes.kg_service')
@patch('app.routes.firestore_service')
def test_add_topic(mock_firestore, mock_kg, client):
    """Test the add topic endpoint"""
    mock_firestore.get_course_data.return_value.exists = True
    mock_firestore.get_course_data.return_value.to_dict.return_value = {
        'status': 'ACTIVE', 'corpus_id': 'corpus1', 'kg_nodes': '[]', 'kg_edges': '[]', 'kg_data': '{}'
    }
    mock_kg.add_topic_to_graph.return_value = ("new_nodes", "new_edges", "new_data")

    response = client.post('/api/add-topic', json={'course_id': '123', 'topic_name': 'New Topic'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

