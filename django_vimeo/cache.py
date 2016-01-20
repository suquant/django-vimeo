import logging
import xxhash

from django.conf import settings
from django.core.cache import caches, InvalidCacheBackendError
from django.utils.functional import wraps

logger = logging.getLogger(__name__)


def cache_it(expires=None, key_func=None):
    if not expires:
        expires = getattr(settings, 'VIMEO_CACHE_EXPIRES', 300)
    cache = None
    try:
        cache_backend = getattr(settings, 'VIMEO_CACHE_BACKEND', None)
        cache = caches[cache_backend]
    except InvalidCacheBackendError as e:
        logger.warning('Vimeo cache "VIMEO_CACHE_BACKEND" disabled, reason: {}'.format(e.message))
    def wrap(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            if not cache:
                return f(*args, **kwds)
            if key_func:
                key = 'django_vimeo_cache:{}'.format(key_func(*args, **kwds))
            else:
                key = 'django_vimeo_cache:' + f.__name__ + ':' +\
                      unicode(list(args) + list(sorted(kwds.items()))).encode('utf-8')
            key = xxhash.xxh64(key).hexdigest()
            value = cache.get(key)
            if value is None:
                value = f(*args, **kwds)
                cache.set(key, value, expires)
                value = cache.get(key)
                if value is None:
                    raise Exception('failed to fetch cached value, try again')
            return value
        return wrapper
    return wrap
