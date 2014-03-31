
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
import socketio.sdjango

socketio.sdjango.autodiscover()

urlpatterns = patterns("game.views",
    url("^socket\.io", include(socketio.sdjango.urls)),
    url("^board", TemplateView.as_view(template_name="tic-tac-toe.html"), name="board"),
    url("^$", "index", name="index"),
)
