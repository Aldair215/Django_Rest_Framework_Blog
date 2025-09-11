from django.urls import path

from .views import (
    PostListView, 
    PostDetailView, 
    PostHeadingsView,
    IncrementPostClickView
    )

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('post/', PostDetailView.as_view(), name='post-detail'),
    path('posts/headings/', PostHeadingsView.as_view(), name='post-headings'),
    path('post/increment-click/', IncrementPostClickView.as_view(), name='increment-post-clicks'),
]

