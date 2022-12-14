from api import serializers
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from posts.models import Subscribe
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    def _create_subsribe(self, author, request):
        if Subscribe.objects.filter(author=author, follower=request.user).exists():
            return (
                {'errors': 'Вы уже подписаны на этого пользователя'}, 
                status.HTTP_400_BAD_REQUEST)
        subscribe = Subscribe.objects.create(author=author, follower=request.user)
        serializer = serializers.SubscribeSerializer(subscribe, context={'request': request})
        return serializer.data, None

    def _delete_subscribe(self, author, request):
        subscribe = Subscribe.objects.filter(author=author, follower=request.user)
        if not subscribe.exists():
            return (
                {'errors': 'Вы уже отписались от этого пользователя'}, 
                status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return None, status.HTTP_204_NO_CONTENT

    @action(methods=('POST', 'DELETE'), detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        author = User.objects.get(id=id)
        if request.method == 'POST':
            data, status = self._create_subsribe(author, request)
            return Response(data, status=status)
        data, status = self._delete_subscribe(author, request)
        return Response(data, status=status)

    @action(methods=('GET',), detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        subs = Subscribe.objects.filter(follower=request.user)
        page = self.paginate_queryset(subs)
        if page is not None:
            print(page)
            serializer = serializers.SubscribeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.SubscribeSerializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
