from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('formulas/', views.formulas, name='formulas'),
    path('comparison/', views.comparison, name='comparison'),
    path('requirements/', views.requirements, name='requirements'),
    path('motors/<str:system_type>/', views.motor_list, name='motor_list'),
    path('motors/<str:system_type>/create/', views.motor_create, name='motor_create'),
    path('motor/<int:pk>/', views.motor_detail, name='motor_detail'),
]
