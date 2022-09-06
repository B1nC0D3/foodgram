from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import RecipeViewSet, IngredientsViewSet

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientsViewSet)

urlpatterns = [
    path('api/', include(router.urls))
]
