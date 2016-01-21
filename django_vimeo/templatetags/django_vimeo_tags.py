import logging
import re

import requests
from django.template import Library, Node
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

from ..exceptions import VideoDoesntExistException

register = Library()

logger = logging.getLogger(__name__)


@register.tag('vimeo')
class VimeoNode(Node):
    """
    Template tag ``vimeo``. It gives access to all
    Keys: https://developer.vimeo.com/apis/oembed#arguments

    Usage (shortcut):
    .. code-block:: html+django
        {% vimeo instance.vimeo_uri [key1=value1, key2=value2...] %}
    Or as a block:
    .. code-block:: html+django
        {% vimeo instance.vimeo_uri [key1=value1, key2=value2...] as VAR %}
            ...
        {% endvideo %}
    Examples:
    .. code-block:: html+django
        {% vimeo instance.vimeo_uri %}
        {% vimeo instance.vimeo_uri width=600 %}
        {% vimeo instance.vimeo_uri autoplay=True loop=True as my_video %}
            HTML: {{ my_video.html }}
            Thumbnail: {{ my_video.thumbnail_url }}
        {% endvideo %}
    """
    error_msg = 'Syntax error. Expected: ``{% video instance.vimeo_uri ' \
                '[key1=val1 key2=val2 ...] [as var] %}``'

    re_option = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')

    def __init__(self, parser, token):
        """
        :param parser: Django template parser
        :type parser: django.template.base.Parser
        :param token: Django template token
        :type token: django.template.base.Token
        """
        self.parser = parser
        self.bits = list(token.split_contents())
        self.tag_name = str(self.pop_bit())
        self.video = self.pop_bit()

        if len(self.bits) > 1 and self.bits[-2] == 'as':
            del self.bits[-2]
            self.variable_name = str(self.pop_bit(-1))
            self.nodelist_file = parser.parse(('end' + self.tag_name, ))
            parser.delete_first_token()
        else:
            self.variable_name = None

        self.options = self.parse_options(self.bits)

    def pop_bit(self, index=0):
        return self.parser.compile_filter(self.bits.pop(index))

    def parse_options(self, bits):
        options = {}
        for bit in bits:
            parsed_bit = self.re_option.match(bit)
            key = smart_str(parsed_bit.group('key'))
            value = self.parser.compile_filter(parsed_bit.group('value'))
            options[key] = value
        return options

    def render(self, context):
        """
        Returns generated HTML.
        :param context: Django template RequestContext
        :type context: django.template.RequestContext
        :return: Rendered HTML with embed video.
        :rtype: django.utils.safestring.SafeText | str
        """
        video = self.video.resolve(context)
        options = self.resolve_options(context)
        try:
            if not self.variable_name:
                return self.embed(video, context=context, **options)
            video_meta = video.meta
            width, height = options.get('width'), options.get('height')
            video_meta.update(
                    {'optimal_file': video.get_optimal_file(width, height),
                     'optimal_picture': video.get_optimal_picture(width, height),
                     'optimal_download': video.get_optimal_download(width, height),
                     'oembed': video.get_oembed(**options)})
            return self.render_block(context, video_meta)
        except requests.Timeout:
            logger.exception('Timeout reached during rendering embed video (`{0}`)'.format(video))
        except VideoDoesntExistException:
            logger.exception('Attempt to render not existing video (`{0}`)'.format(video))

        return ''

    def resolve_options(self, context):
        """
        :param context: Django template RequestContext
        :type context: django.template.RequestContext
        """
        options = {}
        for key in self.options:
            value = self.options[key]
            options[key] = value.resolve(context)
        return options

    def render_block(self, context, data):
        """
        :param context: Django template RequestContext
        :type context: django.template.RequestContext
        :param backend: Given instance inherited from VideoBackend
        :type backend: VideoBackend
        :rtype: django.utils.safestring.SafeText
        """
        context.push()
        context[self.variable_name] = data
        output = self.nodelist_file.render(context)
        context.pop()
        return output

    @classmethod
    def embed(cls, video, context=None, **options):
        """
        Direct render of embed video.
        :param video: video
        :type video: VimeoFieldFile
        :param context: Django template RequestContext
        :type context: django.template.RequestContext | None
        """
        return mark_safe(video.get_embed_code(**options))

    def __iter__(self):
        for node in self.nodelist_file:
            yield node

    def __repr__(self):
        return '<VimeoNode "%s">' % self.url