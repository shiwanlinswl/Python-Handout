from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = []

router.register(r'areas', views.AreasViewSet, base_name='areas')

urlpatterns += router.urls
