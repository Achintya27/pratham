# Generated by Django 5.0 on 2024-02-20 06:45

import utility.malicious_validator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='blog_description',
            field=models.TextField(max_length=4194304),
        ),
        migrations.AlterField(
            model_name='blog',
            name='blog_title',
            field=models.CharField(max_length=256, unique=True, validators=[utility.malicious_validator.validate_no_malicious_content]),
        ),
        migrations.AlterField(
            model_name='blog',
            name='blog_url',
            field=models.CharField(max_length=512, unique=True, validators=[utility.malicious_validator.validate_no_malicious_content]),
        ),
    ]