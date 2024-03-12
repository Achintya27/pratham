from rest_framework import serializers
from blog.models import Blog
import os
from uuid import uuid4
from django.core.validators import FileExtensionValidator

class BlogSerializer(serializers.ModelSerializer):
    """
        Blog Serializer
        We modify the create method to make active blog
    """
    class Meta :
        model =Blog
        fields = '__all__'

    def create(self, validated_data):
        blog = super().create(validated_data)
        # change is_active to Ture
        blog.is_active = True
        blog.save()
        return blog

class BlogListSerializer(serializers.ModelSerializer):
    """
            Blog list Serializer
            We modify the blog fields
    """
    class Meta:
        model = Blog
        fields = ['blog_id', 'blog_title', 'blog_image', 'blog_url', 'status', 'created_at', 'updated_at']





class ImageFileSerializer(serializers.Serializer):
    """
            Blog image upload Serializer
            We modify the save method to save image in media/blogs folder
    """
    image = serializers.FileField(validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'gif', 'tiff', 'tif', 'bmp', 'svg', 'webp', 'ico', 'psd', 'raw', 'avif'])])

    def save(self, **kwargs):
        image = self.validated_data['image']
        # path to save image
        base_path = os.path.join('media', 'blogs')
        # name of image
        image_extension = os.path.splitext(image.name)[-1].lower()

        name = str(uuid4()) + image_extension
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        # save image at destination
        with open(os.path.join(base_path, name), 'wb') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        return name


