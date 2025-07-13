from django.contrib import admin
from .models import CVDocument

@admin.register(CVDocument)
class CVDocumentAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'file_size', 'mime_type', 'status', 'uploaded_at']
    list_filter = ['status', 'mime_type', 'uploaded_at']
    search_fields = ['original_filename']
    readonly_fields = ['uploaded_at', 'file_size', 'mime_type']
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()
    get_file_size_display.short_description = 'Tamaño'
