import os
import uuid
from django.db import models
from django.core.exceptions import ValidationError
import magic

def validate_file_type(file):
    """Validador personalizado para tipos de archivo"""
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    allowed_extensions = ['.pdf', '.doc', '.docx']
    
    # Validar extensión
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f'Tipo de archivo no permitido. Solo se permiten: {", ".join(allowed_extensions)}'
        )
    
    # Validar MIME type usando python-magic
    try:
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        mime_type = magic.from_buffer(file_content, mime=True)
        
        if mime_type not in allowed_types:
            raise ValidationError(
                f'Tipo de archivo no válido. MIME type detectado: {mime_type}'
            )
    except Exception as e:
        raise ValidationError(f'Error al validar el archivo: {str(e)}')

def validate_file_size(file):
    """Validador de tamaño de archivo"""
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(f'El archivo es demasiado grande. Tamaño máximo: 10MB')

def upload_to(instance, filename):
    """Función para generar path de upload único"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('cvs', filename)

class CVDocument(models.Model):
    """Modelo para documentos CV"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processed', 'Procesado'),
        ('error', 'Error'),
    ]
    
    original_filename = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=upload_to,
        validators=[validate_file_type, validate_file_size]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Documento CV'
        verbose_name_plural = 'Documentos CV'
    
    def __str__(self):
        return f'{self.original_filename} - {self.uploaded_at.strftime("%Y-%m-%d %H:%M")}'
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.original_filename = self.file.name
            
            # Detectar MIME type
            try:
                file_content = self.file.read()
                self.file.seek(0)
                self.mime_type = magic.from_buffer(file_content, mime=True)
            except Exception:
                self.mime_type = 'unknown'
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
