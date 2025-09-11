from django.db import models
import uuid

# Create your models here.

class Media(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    media_type = models.CharField(max_length=30, choices=MEDIA_TYPES)
