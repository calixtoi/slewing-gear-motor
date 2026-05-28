from django.urls import path, include

urlpatterns = [
    path('', include('calculator.urls')),
    path('motors/', include('motors.urls')),
]
