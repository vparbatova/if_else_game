from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('question/', views.question_view, name='question'),
    path('reset/', views.reset_game, name='reset_game'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('result/', views.game_result, name='game_result'),
    path('', views.register, name='home'),
]
