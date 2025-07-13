from django import forms
from .models import CVDocument

class CVUploadForm(forms.ModelForm):
    """Formulario para subir documentos CV"""
    
    class Meta:
        model = CVDocument
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'multiple': False,
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].label = 'Seleccionar archivo CV'
        self.fields['file'].help_text = 'Formatos permitidos: PDF, DOC, DOCX. Tamaño máximo: 10MB'
    
    def clean_file(self):
        """Validación adicional del archivo"""
        file = self.cleaned_data.get('file')
        
        if not file:
            raise forms.ValidationError('Debe seleccionar un archivo.')
        
        # Validaciones adicionales ya están en el modelo
        return file
