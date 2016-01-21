from django.db import models

from django_vimeo import fields


class ExampleModel(models.Model):
    vimeo_uri = fields.VimeoField(null=True, blank=True)


