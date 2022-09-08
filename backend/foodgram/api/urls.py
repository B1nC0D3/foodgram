from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api import views

app_name = 'api'

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientsViewSet, basename='ingredients')
router.register('tags', views.TagsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
