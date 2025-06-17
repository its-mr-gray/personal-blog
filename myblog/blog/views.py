from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Post
from .permissions import IsOwnerOrReadOnly
from .serializers import PostSerializer


# Create your views here.
class PostFilter(filters.FilterSet):
    post_title = filters.CharFilter(lookup_expr="icontains")
    author__username = filters.CharFilter(
        field_name="author__username", lookup_expr="icontains"
    )

    class Meta:
        model = Post
        fields = ["post_title", "author__username", "created_date"]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["post_title", "post_content", "author__username"]
    ordering_fields = ["created_date", "post_title"]
    ordering = ["-created_date"]
    filterset_class = PostFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
