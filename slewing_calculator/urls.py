from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.views import HomeView
from cover.views import CoverView
from motor_cycle_calc.views import MotorCycleCalcView
from ideal_parameters.views import IdealParametersView
from motor_verification.views import (
    MotorVerificationListView,
    SupplierAddView,
    SupplierEditView,
    SupplierDeleteView,
    ExtractFromTextView,
    ExtractFromPdfView,
)
from formula_library.views import FormulaLibraryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('cover/', CoverView.as_view(), name='cover'),
    path('calc/', MotorCycleCalcView.as_view(), name='calc'),
    path('parameters/', IdealParametersView.as_view(), name='parameters'),
    path('verification/', MotorVerificationListView.as_view(), name='verification-list'),
    path('verification/add/', SupplierAddView.as_view(), name='supplier-add'),
    path('verification/<int:pk>/edit/', SupplierEditView.as_view(), name='supplier-edit'),
    path('verification/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier-delete'),
    path('verification/extract-text/', ExtractFromTextView.as_view(), name='extract-text'),
    path('verification/extract-pdf/', ExtractFromPdfView.as_view(), name='extract-pdf'),
    path('formulas/', FormulaLibraryView.as_view(), name='formulas'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
