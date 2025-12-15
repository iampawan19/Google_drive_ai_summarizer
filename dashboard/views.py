"""
Dashboard Views
Handles UI rendering and communication with FastAPI service
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import requests
import csv
import json
from io import StringIO


def index(request):
    """Render main dashboard page"""
    return render(request, 'dashboard/index.html')


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
