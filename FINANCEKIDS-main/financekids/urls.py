from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('aprendizaje/<int:tema>/', views.aprendizaje, name='aprendizaje'),
    path('completar/<int:tema>/', views.completar_tema, name='completar_tema'),
    path('juego1/', views.juego1, name='juego1'),
    path('preguntas1/', views.preguntas1, name='preguntas1'),
    path('juego2/', views.juego2, name='juego2'),
    path('preguntas2/', views.preguntas2, name='preguntas2'),
]