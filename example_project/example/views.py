from django.shortcuts import render

from . import models


def home(request):
    m = models.ExampleModel.objects.latest('pk')
    return render(request, 'home.html', {'instance': m})
