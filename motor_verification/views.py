from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from .models import MotorSupplier
from .forms import MotorSupplierForm, PdfUploadForm, TextPasteForm
from .validators import validate_supplier, get_supplier_summary
from .extractors import extract_from_text, extract_from_pdf, use_openai_extraction
from cover.models import DesignParameters


class MotorVerificationListView(ListView):
    """Display all supplier motors in comparison table."""
    model = MotorSupplier
    template_name = 'motor_verification/list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        design = DesignParameters.get_or_create_default()

        # Validate each supplier and compute summaries
        suppliers_with_validation = []
        for supplier in context['suppliers']:
            validation = validate_supplier(supplier, design)
            summary = get_supplier_summary(supplier, design)
            suppliers_with_validation.append({
                'supplier': supplier,
                'validation': validation,
                'summary': summary,
            })

        context['suppliers_with_validation'] = suppliers_with_validation
        context['design'] = design

        return context


class SupplierAddView(CreateView):
    """Add a new motor supplier via manual entry, text extraction, or PDF upload."""
    model = MotorSupplier
    form_class = MotorSupplierForm
    template_name = 'motor_verification/add_edit.html'
    success_url = reverse_lazy('verification-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'add'
        if self.request.POST:
            if 'extract_from_text' in self.request.POST:
                context['text_form'] = TextPasteForm(self.request.POST)
            elif 'extract_from_pdf' in self.request.POST:
                context['pdf_form'] = PdfUploadForm(self.request.POST, self.request.FILES)
            else:
                context['pdf_form'] = PdfUploadForm()
                context['text_form'] = TextPasteForm()
        else:
            context['pdf_form'] = PdfUploadForm()
            context['text_form'] = TextPasteForm()
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Motor supplier '{form.cleaned_data['supplier_name']}' added successfully.")
        return super().form_valid(form)


class SupplierEditView(UpdateView):
    """Edit an existing motor supplier."""
    model = MotorSupplier
    form_class = MotorSupplierForm
    template_name = 'motor_verification/add_edit.html'
    success_url = reverse_lazy('verification-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'edit'
        context['pdf_form'] = PdfUploadForm()
        context['text_form'] = TextPasteForm()
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Motor supplier '{form.cleaned_data['supplier_name']}' updated successfully.")
        return super().form_valid(form)


class SupplierDeleteView(DeleteView):
    """Delete a motor supplier."""
    model = MotorSupplier
    template_name = 'motor_verification/confirm_delete.html'
    success_url = reverse_lazy('verification-list')

    def delete(self, request, *args, **kwargs):
        supplier = self.get_object()
        messages.success(request, f"Motor supplier '{supplier.supplier_name}' deleted.")
        return super().delete(request, *args, **kwargs)


class ExtractFromTextView(View):
    """Extract supplier data from pasted text via AJAX."""
    def post(self, request):
        form = TextPasteForm(request.POST)
        if form.is_valid():
            raw_text = form.cleaned_data['raw_text']
            use_ai = form.cleaned_data.get('use_ai', False)

            # Try AI extraction first if requested
            extracted_data = None
            if use_ai:
                extracted_data = use_openai_extraction(raw_text)

            # Fall back to regex if AI not used or failed
            if extracted_data is None:
                extracted_data = extract_from_text(raw_text)

            return JsonResponse({
                'status': 'success',
                'extracted_data': extracted_data,
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)


class ExtractFromPdfView(View):
    """Extract supplier data from uploaded PDF via AJAX."""
    def post(self, request):
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf_file']

            # Check file size (max 10 MB)
            if pdf_file.size > 10 * 1024 * 1024:
                return JsonResponse({
                    'status': 'error',
                    'error': 'File size exceeds 10 MB limit',
                }, status=400)

            extracted_data = extract_from_pdf(pdf_file)

            if 'error' in extracted_data:
                return JsonResponse({
                    'status': 'error',
                    'error': extracted_data['error'],
                }, status=400)

            return JsonResponse({
                'status': 'success',
                'extracted_data': extracted_data,
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)
