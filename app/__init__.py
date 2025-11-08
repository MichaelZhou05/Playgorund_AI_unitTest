"""
Flask application initialization.
This module creates and configures the Flask app instance.
"""
from flask import Flask
import os


def create_app():
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Register routes
    with app.app_context():
        from . import routes
        
    return app
