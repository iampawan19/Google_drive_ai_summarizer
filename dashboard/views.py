"""
Dashboard Views
Handles UI rendering and communication with FastAPI service
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import csv
import json
import os
from io import StringIO
import sys

# Add ai_service to path
sys.path.append(os.path.join(settings.BASE_DIR, 'ai_service'))
from ai_service.drive_client import GoogleDriveClient


def index(request):
    """Render main dashboard page"""
    # Check if user is authenticated with Google
    is_authenticated = os.path.exists(os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.pickle'))
    context = {
        'is_authenticated': is_authenticated,
        'folder_id': os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    }
    return render(request, 'dashboard/index.html', context)


def oauth_authorize(request):
    """
    Initiate Google OAuth2 authorization flow
    Redirects user to Google consent page
    """
    try:
        authorization_url, state = GoogleDriveClient.get_authorization_url()
        # Store state in session for validation
        request.session['oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        return HttpResponse(f'Error initiating OAuth: {str(e)}', status=500)


def oauth_callback(request):
    """
    Handle OAuth2 callback from Google
    Exchanges authorization code for access token
    """
    try:
        # Get the full callback URL
        authorization_response = request.build_absolute_uri()
        
        # Get state from session for validation
        state = request.session.get('oauth_state')
        
        # Exchange code for credentials
        credentials = GoogleDriveClient.handle_oauth_callback(
            authorization_response, 
            state
        )
        
        # Clear state from session
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        # Redirect to dashboard with success message
        return redirect('/?auth=success')
        
    except Exception as e:
        return HttpResponse(f'OAuth callback error: {str(e)}', status=500)


@csrf_exempt
@require_http_methods(["POST"])
def summarize(request):
    """
    Handle summarization request
    Forwards request to FastAPI service and returns results
    """
    try:
        # Get parameters from request
        data = json.loads(request.body)
        folder_id = data.get('folder_id')
        file_types = data.get('file_types', ['pdf', 'docx', 'txt'])
        
        if not folder_id:
            return JsonResponse({
                'error': 'folder_id is required'
            }, status=400)
        
        # Call FastAPI service
        fastapi_url = f"{settings.FASTAPI_SERVICE_URL}/summarize"
        
        response = requests.post(
            fastapi_url,
            json={
                'folder_id': folder_id,
                'file_types': file_types
            },
            timeout=300  # 5 minute timeout for large folders
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Store results in session for CSV download
            request.session['last_results'] = result
            
            return JsonResponse(result)
        else:
            return JsonResponse({
                'error': f'FastAPI service error: {response.text}'
            }, status=response.status_code)
            
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'error': 'Cannot connect to AI service. Make sure FastAPI is running.'
        }, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({
            'error': 'Request timeout. The folder may be too large.'
        }, status=504)
    except Exception as e:
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def download_csv(request):
    """
    Download results as CSV file
    Uses data stored in session from last summarize request
    """
    try:
        # Get results from session
        results = request.session.get('last_results')
        
        if not results:
            return HttpResponse(
                'No results available. Please run a summarization first.',
                status=400
            )
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['File Name', 'Type', 'Size', 'Summary', 'Status'])
        
        # Write data rows
        for file_data in results.get('files', []):
            writer.writerow([
                file_data.get('name', ''),
                file_data.get('type', ''),
                file_data.get('size', ''),
                file_data.get('summary', ''),
                file_data.get('status', '')
            ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="summaries.csv"'
        
        return response
        
    except Exception as e:
        return HttpResponse(
            f'Error generating CSV: {str(e)}',
            status=500
        )
