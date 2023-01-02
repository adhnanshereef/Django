from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('createroom', views.createRoom, name="createroom"),
    path('updateroom/<str:pk>/', views.updateRoom, name="updateroom"),
    path('deleteroom/<str:pk>/', views.deleteRoom, name="deleteroom"),
    path('deletemessage/<str:pk>/', views.deleteMessage, name="deletemsg"),
    path('<str:username>', views.profile, name="profile"),
]
