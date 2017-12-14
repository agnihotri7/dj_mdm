"""
"""
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    context = {}
    return render(request, 'index.html', context)
