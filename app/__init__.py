# This makes 'app' a Python package and initializes Flask

from flask import Flask

def create_app():
    """
    Application factory pattern — creates and configures the Flask app.
    This pattern makes testing and scaling easier.
    """
    app = Flask(__name__)
    
    # Register routes (we'll create routes.py next)
    from app.routes import medicine_bp
    app.register_blueprint(medicine_bp)
    
    return app# DoseAI Package