from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from .models import SupplierMotor, MotorSupplier
from .pdf_export import generate_motor_pdf


class MotorListView(ListView):
    model = SupplierMotor
    template_name = 'motors/motor_list.html'
    context_object_name = 'motors'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = MotorSupplier.objects.all()
        return context


class MotorDetailView(DetailView):
    model = SupplierMotor
    template_name = 'motors/motor_detail.html'
    context_object_name = 'motor'
    slug_field = 'model_number'
    slug_url_kwarg = 'model_number'


def motor_pdf_export(request, model_number):
    motor = get_object_or_404(SupplierMotor, model_number=model_number)
    pdf_buffer = generate_motor_pdf(motor)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{motor.model_number}_specs.pdf"'
    return response
