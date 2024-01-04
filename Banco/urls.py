from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from api import views as api_views
from iniciar import views as iniciar_views

router = DefaultRouter()
router.register(r'nuevoregistro', api_views.NuevoRegistroViewSet)
router.register(r'transferencia', api_views.TransferenciaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', iniciar_views.custom_login, name='custom_login'),
    path('iniciar/', include('iniciar.urls')),
    path('transferencias/', include('transferencias.urls')),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
