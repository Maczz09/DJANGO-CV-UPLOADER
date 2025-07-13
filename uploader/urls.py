from django.urls import path
from . import views

urlpatterns = [
    path('', views.CVUploadView.as_view(), name='upload'),
    path('ajax-upload/', views.AjaxUploadView.as_view(), name='ajax_upload'),
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('health/', views.health_check, name='health_check'),
]
