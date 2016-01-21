import math
import operator

from django import forms
from django.db import models
from django.db.models.fields import files

from .storage import VimeoFileStorage


class VimeoFieldFile(files.FieldFile):
    def get_meta(self):
        return self.storage.get_meta(self.name)
    meta = property(get_meta)

    def get_oembed(self, **options):
        return self.storage.get_oembed(self.name, **options)
    oembed = property(get_oembed)

    def get_embed_code(self, **options):
        return self.storage.get_embed_code(self.name, **options)

    def _get_optimal_index(self, iterable, width=None, height=None):
        sizes = [(i, r.get('width', 0), r.get('height', 0)) for i, r in enumerate(iterable)]
        if width and height:
            distances = (
                (r[0], math.sqrt(math.pow(r[1] - width, 2) + math.pow(r[2] - height, 2))) for r in sizes
            )
            return sorted(distances, key=operator.itemgetter(1))[0][0]
        elif width:
            key = 1
            val = width
        elif height:
            key = 2
            val = height
        distances = (
            (r[0], math.pow(val - r[key], 2)) for r in sizes
        )
        return sorted(distances, key=operator.itemgetter(1))[0][0]

    def get_optimal_file(self, width=None, height=None):
        iterable = self.meta.get('files', [])
        return iterable[self._get_optimal_index(iterable, width, height)] if iterable else None

    def get_optimal_picture(self, width=None, height=None):
        pictures = self.meta.get('pictures', {})
        if not pictures:
            return None
        iterable = pictures.get('sizes', [])
        return iterable[self._get_optimal_index(iterable, width, height)] if iterable else None

    def get_optimal_download(self, width=None, height=None):
        iterable = self.meta.get('download', [])
        return iterable[self._get_optimal_index(iterable, width, height)] if iterable else None


class VimeoField(models.FileField):
    """
    Model field for vimeo video. Descendant of
    :py:class:`django.db.models.FileField`.
    """
    attr_class = VimeoFieldFile

    def __init__(self, *args, **kwargs):
        defaults = {'storage': VimeoFileStorage()}
        defaults.update(kwargs)
        super(VimeoField, self).__init__(*args, **defaults)

    def formfield(self, **kwargs):
        defaults = {'form_class': VimeoFormField}
        defaults.update(kwargs)
        return super(VimeoField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(VimeoField, self).deconstruct()
        return name, path, args, kwargs

    def south_field_triple(self):
        name, path, args, kwargs = self.deconstruct()
        return '{}.{}'.format(path, name), args, kwargs


class VimeoFormField(forms.FileField):
    """
    Form field for vimeo video. Descendant of
    :py:class:`django.forms.FileField`
    """
    pass
