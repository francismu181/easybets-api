import os
from flask import Request
import functions_framework
from app import app as flask_app

# Set the environment variable for cloud deployment
os.environ['RUNNING_IN_CLOUD'] = 'true'

@functions_framework.http
def easybets_api(request: Request):
    """HTTP Cloud Function that acts as a wrapper for the Flask app.
    
    This wraps our Flask application to run on Firebase Cloud Functions.
    
    Args:
        request: The request object from Cloud Functions
        
    Returns:
        The response from the Flask app.
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {'Access-Control-Allow-Origin': '*'}
    
    # Create a context for the Flask app to process the request
    with flask_app.request_context(request.environ):
        return flask_app.full_dispatch_request()
