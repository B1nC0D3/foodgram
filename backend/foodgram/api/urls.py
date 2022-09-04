from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
