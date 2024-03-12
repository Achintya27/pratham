from django.urls import path
from blog.views import BlogView, QuerySearchListView, BlogbyId, UploadImageForBlog, SingleBlogBYID

app_name = 'blog'

urlpatterns = [
    path('admin/create/', BlogView.as_view()),
    path('admin/<uuid:blog_id>', BlogbyId.as_view()),
    path('', QuerySearchListView.as_view()),
    path('<uuid:blog_id>', SingleBlogBYID.as_view()),
    path('upload_image/', UploadImageForBlog.as_view())
]