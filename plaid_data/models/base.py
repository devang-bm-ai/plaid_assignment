from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RequestModel(BaseModel):
    request_id = models.CharField(max_length=32, null=True)

    class Meta:
        abstract = True