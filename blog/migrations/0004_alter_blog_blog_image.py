# Generated by Django 5.0 on 2024-02-27 04:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_blog_blog_description_alter_blog_blog_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='blog_image',
            field=models.FileField(upload_to='blogs/', validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'gif', 'tiff', 'tif', 'bmp', 'svg', 'webp', 'ico', 'psd', 'raw'])]),
        ),
    ]
