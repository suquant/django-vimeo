import datetime
import operator
import os
from tempfile import NamedTemporaryFile

import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property
from vimeo import VimeoClient

from .cache import cache_it
from .exceptions import SpaceNotEnoughtException
from .exceptions import UnknownIdException


@deconstructible
class VimeoFileStorage(Storage):
    def __init__(self, client_id=None, client_secret=None, access_token=None):
        if not client_id:
            client_id = getattr(settings, 'VIMEO_CLIENT_ID', None)
        if not client_secret:
            client_secret = getattr(settings, 'VIMEO_CLIENT_SECRET', None)
        if not access_token:
            access_token = getattr(settings, 'VIMEO_ACCESS_TOKEN', None)
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.oembed_url = getattr(settings, 'VIMEO_OEMBED_URL',
                                  'https://vimeo.com/api/oembed.json')
        self.video_url_pattern = getattr(settings, 'VIMEO_VIDEO_URL_PATTERN',
                                         'https://vimeo.com/{}')

    @cached_property
    def client(self):
        return VimeoClient(token=self.access_token, key=self.client_id, secret=self.client_secret)

    def _upload_quota_check(self, size):
        res = self.client.get('/me')
        self._raise_for_status(res)
        res = res.json()
        if 'upload_quota' in res and \
                        res.get('upload_quota', {}).get('space', {}).get('free', 0) < size:
            freeMb = res.get('upload_quota', {}).get('space', {}).get('free', 0) / 1048576
            usedMb = res.get('upload_quota', {}).get('space', {}).get('used', 0) / 1048576
            maxMb = res.get('upload_quota', {}).get('space', {})('max', 0) / 1048576
            sizeMb = size / 1048576
            raise SpaceNotEnoughtException(
                'Space on vimeo not enought for {} MB (free: {} MB, used: {} MB, max: {} MB)'
                    .format(sizeMb, freeMb, usedMb, maxMb)
            )

    def _raise_for_status(self, res):
        if res.status_code == 404:
            raise UnknownIdException(res.reason)
        res.raise_for_status()

    @cache_it()
    def get_meta(self, path):
        res = self.client.get(path)
        self._raise_for_status(res)
        return res.json()

    @cache_it()
    def get_oembed(self, path, **options):
        defaults = {'url': self.video_url_pattern.format(path.split('/')[-1])}
        defaults.update(options)
        res = requests.get(self.oembed_url, params=defaults)
        self._raise_for_status(res)
        return res.json()

    def get_embed_code(self, path, **options):
        oembed = self.get_oembed(path, **options)
        return oembed.get('html')

    def get_valid_name(self, name):
        valid_name = name
        if valid_name and valid_name[0] == '.':
            valid_name = valid_name[1:]
        return valid_name

    def get_available_name(self, name, max_length=None):
        return self.get_valid_name(name)

    def path(self, name):
        return name

    def delete(self, name):
        self.client.delete(name)

    def exists(self, name):
        return self.client.get(name).ok

    def size(self, name):
        res = self.client.get(name)
        self._raise_for_status(res)
        res = res.json()
        large_files = sorted(res.get('files'), key=operator.itemgetter('size'), reverse=True)
        return large_files[0].get('size', 0) if large_files else 0

    def url(self, name):
        res = self.client.get(name)
        res.raise_for_status()
        res = res.json()
        large_files = sorted(res.get('files'), key=operator.itemgetter('size'), reverse=True)
        return large_files[0].get('link_secure') if large_files else None

    def accessed_time(self, name):
        res = self.client.get(name)
        res.raise_for_status()
        res = res.json()
        utc_datetime = res.get('modified_time')
        return datetime.strptime(utc_datetime, '%Y-%m-%dT%H:%M:%SZ')

    def created_time(self, name):
        res = self.client.get(name)
        res.raise_for_status()
        res = res.json()
        utc_datetime = res.get('created_time')
        return datetime.strptime(utc_datetime, '%Y-%m-%dT%H:%M:%SZ')

    def modified_time(self, name):
        return self.accessed_time(name)

    def _save(self, name, content):
        size = content.size
        self._upload_quota_check(size)
        uploaded_uri = None
        if hasattr(content, 'temporary_file_path'):
            tmp_file_path = content.temporary_file_path()
            uploaded_uri = self.client.upload(tmp_file_path)
        else:
            try:
                tmp_file = NamedTemporaryFile(delete=False)
                for chunk in content.chunks():
                    if not chunk:
                        continue
                    tmp_file.write(chunk)
                tmp_file.close()
                uploaded_uri = self.client.upload(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)
        return uploaded_uri
