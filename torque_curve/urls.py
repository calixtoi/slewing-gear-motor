from django.urls import path
from . import views

urlpatterns = [
    path('',      views.torque_curve_index, name='torque_curve'),
    path('ajax/', views.torque_curve_ajax,  name='torque_curve_ajax'),
]
