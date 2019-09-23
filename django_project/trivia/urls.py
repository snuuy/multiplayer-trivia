from django.urls import path
from . import views

urlpatterns = [
	path('', views.home_view, name='home'),
	path('register/', views.register_view, name='register'),
	path('login/', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('matchmaking/', views.matchmaking_view, name='matchmaking'),
	path('game/', views.game_view, name='game'),
	path('api/login/', views.login_api_view, name='loginapi'),
	path('api/register/', views.register_api_view, name='registerapi'),
	path('api/findgame/', views.findgame_view, name='findgameapi'),
	path('api/gameinfo/', views.gameinfo_view, name='gameinfoapi'),
	path('api/selectanswer/', views.selectanswer_view, name='selectanswerapi'),
	path('api/wait/', views.wait_view, name='waitapi'),
	path('api/cancelgame/', views.cancelgame_view, name='cancelapi'),
]