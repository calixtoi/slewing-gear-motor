from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_datasheet, name='upload_datasheet'),
    path('save/', views.save_calculation, name='save_calculation'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/StandardPF/', views.suppliers, {'crane_filter': 'standard_pf'}, name='suppliers_standard_pf'),
    path('suppliers/PF-XXL/', views.suppliers, {'crane_filter': 'pf_xxl'}, name='suppliers_pf_xxl'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/delete/', views.delete_calculation, name='delete_calculation'),
    path('formulas/', views.formulas, name='formulas'),
    path('comparison/', views.comparison, name='comparison'),
    path('requirements/', views.requirements, name='requirements'),
    path('examples/', views.worked_examples, name='worked_examples'),
    path('motors/<str:system_type>/', views.motor_list, name='motor_list'),
    path('motors/<str:system_type>/create/', views.motor_create, name='motor_create'),
    path('motor/<int:pk>/', views.motor_detail, name='motor_detail'),
    path('api/calculate/', views.calculate_ajax, name='calculate_ajax'),
]
