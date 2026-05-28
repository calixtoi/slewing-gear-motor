from django.urls import path
from . import views

app_name = 'motors'

urlpatterns = [
    path('', views.MotorListView.as_view(), name='list'),
    path('<str:model_number>/', views.MotorDetailView.as_view(), name='detail'),
    path('<str:model_number>/pdf/', views.motor_pdf_export, name='pdf_export'),
]
