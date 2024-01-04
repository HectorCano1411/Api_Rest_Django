# transferencias/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('crear_transferencia/', views.crear_transferencia, name='crear_transferencia'),
    path('aprobar_transferencia/<int:transferencia_id>/', views.aprobar_transferencia, name='aprobar_transferencia'),
    path('detalles_transferencia/<int:transferencia_id>/', views.detalles_transferencia, name='detalles_transferencia'),
    
]
