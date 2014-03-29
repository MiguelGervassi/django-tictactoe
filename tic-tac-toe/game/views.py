from socketio import socketio_manage
from django.template import Context, loader, RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

def rooms(request, template="tic-tac-toe.html"):
    """
    Homepage - lists all rooms.
    """
    context = {"rooms": [1,2]}
    return render(request, template, context_instance=RequestContext(request))


# def room(request, slug, template="room.html"):
#     """
#     Show a room.
#     """
#     context = {"room": get_object_or_404(ChatRoom, slug=slug)}
#     return render(request, template, context)

# def create(request):
#     """
#     Handles post from the "Add room" form on the homepage, and
#     redirects to the new room.
#     """
#     name = request.POST.get("name")
#     if name:
#         room, created = ChatRoom.objects.get_or_create(name=name)
#         return redirect(room)
#     return redirect(rooms)
