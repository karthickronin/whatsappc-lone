from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *
from django.views.generic.base import RedirectView

urlpatterns = [
    path('home/', home,name = 'home'),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('',RedirectView.as_view(url = '/home')),
    
    # path('create_friend/', create_friend,name = 'create_friend'),
    
    # path('friend_list/', friend_list,name = 'friend_list'),
    
    # path('chat/<str:room_name>/', start_chat, name='start_chat'),
]
