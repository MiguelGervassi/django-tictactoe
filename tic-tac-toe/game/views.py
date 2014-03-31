from socketio import socketio_manage
from django.template import Context, loader, RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

def index(request, template="index.html"):
    """
    Index - play against unbeatable AI.
    """
    context = {"grid": range(1,10)}
    return render(request, template, context)