from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from posts.models import Group, Post
from .permissions import IsAuthor
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.select_related('author', 'group')
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):

    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]

    def perform_create(self, serializer):
        pk = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=pk)
        serializer.save(author=post.author, post=post)

    def get_queryset(self):
        pk = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=pk)
        return post.comments.all()
