import uuid
from django.db import models
from user.models import User
from utility.field import UnixTimestampField
from utility.malicious_validator import validate_no_malicious_content
from django.core.validators import FileExtensionValidator


class Blog(models.Model):
    """
        Blog  Model
         : customize the table name with meta Class db_table name
         : ordering in json data
    """
    Status_Choices = (("draft", "draft"),
                      ("saved", "saved"),
                      ("published", "published"),
                      ("unpublished", "unpublished"))
    blog_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    blog_title = models.CharField(max_length=256,unique=True, validators=[validate_no_malicious_content])
    blog_description = models.TextField(max_length=4194304)
    blog_image = models.FileField(upload_to='blogs/', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'gif', 'tiff', 'tif', 'bmp', 'svg', 'webp', 'ico', 'psd', 'raw','avif'])])
    seo_description = models.CharField(max_length=256, blank=True, null=True, validators=[validate_no_malicious_content])
    blog_url = models.CharField(max_length=512, unique=True,validators=[validate_no_malicious_content])
    status = models.CharField(max_length=16, choices=Status_Choices)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_updated')
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_created')
    created_at = UnixTimestampField(auto_now_add=True, null=True)
    updated_at = UnixTimestampField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['blog_id', 'blog_title', 'blog_url', 'seo_description', 'blog_description', 'blog_image', 'status', 'created_by',
                    'updated_by', 'created_at', 'updated_at', 'is_active']

        db_table = 'blog'
    def __str__(self) -> str:
        return self.blog_title
