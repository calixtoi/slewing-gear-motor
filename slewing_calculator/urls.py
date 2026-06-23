from django.urls import path, include

urlpatterns = [
    path('', include('calculator.urls')),
    path('motors/', include('motors.urls')),
    # path('torque-curve/', include('torque_curve.urls')),  # Disabled: uses deleted engine.py
]
