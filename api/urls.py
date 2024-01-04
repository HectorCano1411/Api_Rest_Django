from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NuevoRegistroListCreateView, NuevoRegistroRetrieveUpdateDestroyView, TransferenciaListCreateView, TransferenciaRetrieveUpdateDestroyView

urlpatterns = [
    # Otras URL de tu aplicación...
    path('api/nuevoregistro/', NuevoRegistroListCreateView.as_view(), name='nuevoregistro-list-create'),
    path('api/nuevoregistro/<int:pk>/', NuevoRegistroRetrieveUpdateDestroyView.as_view(), name='nuevoregistro-retrieve-update-destroy'),
    path('api/transferencia/', TransferenciaListCreateView.as_view(), name='transferencia-list-create'),
    path('api/transferencia/<int:pk>/', TransferenciaRetrieveUpdateDestroyView.as_view(), name='transferencia-retrieve-update-destroy'),
]
