from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index,name="index"),
    path('profile/<str:username>', views.profile, name='profile'),
    path('editprofile/<int:id>', views.editprofile, name='editprofile'),
    path("register",views.register,name="register"),
    path("login",views.user_login,name='login'),
    path("logout",views.logout_profile,name="logout")
]