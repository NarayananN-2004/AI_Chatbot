from django.contrib import admin
from django.urls import path


from home.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/',login_page, name='login'),
    path('register/',register, name='register'),
    path('chat/',ask_gemini, name='ask_gemini'),
    path('logout/',logout_page, name='logout_page'),
    path("jarvis-chat/",jarvis_chat, name="jarvis_chat"),
]
