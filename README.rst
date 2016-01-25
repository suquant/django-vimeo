django-vimeo
==================

Django module for easy embedding Vimeo videos into app.

.. image:: https://travis-ci.org/suquant/django-vimeo.svg?branch=master
    :target: https://travis-ci.org/suquant/django-vimeo
.. image:: https://coveralls.io/repos/suquant/django-vimeo/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/suquant/django-vimeo?branch=master


Quick start
************

#. Install ``django-vimeo``:

   ::

      pip install django-vimeo


   or from sources

   ::

      pip install git+https://github.com/suquant/django-vimeo.git


#. Add ``django_vimeo`` to ``INSTALLED_APPS`` in your Django settings.

#. Add credentials into settings.

   Create new application in https://developer.vimeo.com/apps

   ::

      VIMEO_CLIENT_ID = 'client id'
      VIMEO_CLIENT_SECRET = 'client secret'
      VIMEO_ACCESS_TOKEN = 'access token'

   For activate use cache

   ::

      VIMEO_CACHE_BACKEND = 'default' # Default: None
      VIMEO_CACHE_EXPIRES = 300 # Default: 300 seconds


      "If 'VIMEO_CACHE_BACKEND' not setted or 'None', cache will be not used"

#. Usage of template tags:

   ::

      {% load django_vimeo_tags %}

      The video tag:
      {% vimeo instance.video width=600 as video %}
         <video width="600" loop="loop" autoplay="autoplay" poster="{{ video.optimal_picture.link }}">
             <source src="{{ video.optimal_file.link_secure }}" type='{{ video.optimal_file.type }}'>
             {% trans 'tag "video" not supported by your browser' %}
             <a href="{{ video.optimal_download.link }}">{% trans 'download video' %}</a>.
         </video>
      {% endvimeo %}

      Or embed shortcut:
      {% vimeo instance.video width=600 %}

#. Usage of model fields

   ::

      from django.db import models
      from django_vimeo import fields


      class ExampleModel(models.Model):
         video = fields.VimeoField(null=True, blank=True)
