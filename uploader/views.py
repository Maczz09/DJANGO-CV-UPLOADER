import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from .models import CVDocument
from .forms import CVUploadForm
import json

logger = logging.getLogger(__name__)

class CVUploadView(View):
    """Vista principal para subir CVs con patrones de resiliencia"""
    
    def get(self, request):
        """Mostrar formulario de upload"""
        form = CVUploadForm()
        documents = CVDocument.objects.all()[:10]  # Últimos 10 documentos
        
        context = {
            'form': form,
            'documents': documents,
        }
        return render(request, 'uploader/upload.html', context)
    
    def post(self, request):
        """Procesar upload de archivo"""
        form = CVUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Patrón de resiliencia: Transacción atómica
                    document = form.save(commit=False)
                    document.status = 'pending'
                    document.save()
                    
                    # Simular procesamiento
                    document.status = 'processed'
                    document.save()
                    
                    logger.info(f'Archivo subido exitosamente: {document.original_filename}')
                    messages.success(request, f'Archivo "{document.original_filename}" subido exitosamente.')
                    
                    return redirect('upload')
                    
            except ValidationError as e:
                logger.error(f'Error de validación: {str(e)}')
                messages.error(request, f'Error de validación: {str(e)}')
            except Exception as e:
                logger.error(f'Error inesperado al subir archivo: {str(e)}')
                messages.error(request, 'Error inesperado al procesar el archivo. Inténtelo nuevamente.')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        # Si hay errores, mostrar formulario con errores
        documents = CVDocument.objects.all()[:10]
        context = {
            'form': form,
            'documents': documents,
        }
        return render(request, 'uploader/upload.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class AjaxUploadView(View):
    """Vista AJAX para upload con mejor UX"""
    
    def post(self, request):
        """Upload via AJAX"""
        try:
            if 'file' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No se ha seleccionado ningún archivo.'
                }, status=400)
            
            form = CVUploadForm(request.POST, request.FILES)
            
            if form.is_valid():
                with transaction.atomic():
                    document = form.save()
                    logger.info(f'Archivo subido via AJAX: {document.original_filename}')
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Archivo "{document.original_filename}" subido exitosamente.',
                        'document': {
                            'id': document.id,
                            'filename': document.original_filename,
                            'size': document.get_file_size_display(),
                            'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M'),
                            'status': document.get_status_display(),
                        }
                    })
            else:
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f'{field}: {error}')
                
                return JsonResponse({
                    'success': False,
                    'error': '; '.join(errors)
                }, status=400)
                
        except Exception as e:
            logger.error(f'Error en AJAX upload: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor. Inténtelo nuevamente.'
            }, status=500)

def delete_document(request, document_id):
    """Eliminar documento"""
    if request.method == 'POST':
        try:
            document = get_object_or_404(CVDocument, id=document_id)
            filename = document.original_filename
            
            # Eliminar archivo físico
            if document.file:
                document.file.delete()
            
            document.delete()
            
            logger.info(f'Documento eliminado: {filename}')
            messages.success(request, f'Documento "{filename}" eliminado exitosamente.')
            
        except Exception as e:
            logger.error(f'Error al eliminar documento: {str(e)}')
            messages.error(request, 'Error al eliminar el documento.')
    
    return redirect('upload')

def health_check(request):
    """Health check endpoint para monitoreo"""
    try:
        # Verificar base de datos
        CVDocument.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': '2024-01-01T00:00:00Z'
        })
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
