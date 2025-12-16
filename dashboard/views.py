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
from io import StringIO, BytesIO
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime

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
            
            # Add Google Drive URLs to each file
            for file_data in result.get('files', []):
                if 'id' in file_data:
                    file_data['url'] = f"https://drive.google.com/file/d/{file_data['id']}/view"
            
            # Store results in session for CSV/PDF download
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
        writer.writerow(['File Name', 'Type', 'Size', 'Summary', 'File URL', 'Status'])
        
        # Write data rows
        for file_data in results.get('files', []):
            writer.writerow([
                file_data.get('name', ''),
                file_data.get('type', ''),
                file_data.get('size', ''),
                file_data.get('summary', ''),
                file_data.get('url', ''),
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


@require_http_methods(["GET"])
def download_pdf(request):
    """
    Download results as PDF file
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
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        )
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph('Google Drive AI Summarizer Report', title_style))
        elements.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        files = results.get('files', [])
        total = len(files)
        successful = len([f for f in files if f.get('status') == 'success'])
        errors = len([f for f in files if f.get('status') == 'error'])
        
        stats_data = [
            ['Total Files', 'Successful', 'Errors'],
            [str(total), str(successful), str(errors)]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Files section
        elements.append(Paragraph('File Summaries', heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Process each file
        for idx, file_data in enumerate(files, 1):
            # File header
            file_name = file_data.get('name', 'Unknown')
            file_type = file_data.get('type', '').split('/')[-1]
            status = file_data.get('status', 'unknown')
            
            # Create file info paragraph
            file_header = f"<b>{idx}. {file_name}</b> ({file_type})"
            elements.append(Paragraph(file_header, normal_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Status
            status_color = '#155724' if status == 'success' else '#721c24'
            status_text = f'<font color="{status_color}"><b>Status:</b> {status.upper()}</font>'
            elements.append(Paragraph(status_text, normal_style))
            elements.append(Spacer(1, 0.05*inch))
            
            # File URL (if available)
            if 'url' in file_data:
                url_text = f'<b>Link:</b> <link href="{file_data["url"]}" color="blue">{file_data["url"]}</link>'
                elements.append(Paragraph(url_text, normal_style))
                elements.append(Spacer(1, 0.05*inch))
            
            # Summary
            summary = file_data.get('summary', 'No summary available')
            # Wrap text to prevent overflow
            summary_style = ParagraphStyle(
                'Summary',
                parent=normal_style,
                fontSize=9,
                leading=12,
                leftIndent=20,
                rightIndent=20,
                spaceAfter=10
            )
            elements.append(Paragraph(f'<b>Summary:</b>', normal_style))
            elements.append(Paragraph(summary, summary_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Add page break after every 3 files for better readability
            if idx % 3 == 0 and idx < len(files):
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF from buffer
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="summaries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        return response
        
    except Exception as e:
        return HttpResponse(
            f'Error generating PDF: {str(e)}',
            status=500
        )
