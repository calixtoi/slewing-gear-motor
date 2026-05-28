from django.contrib import admin
from .models import MotorSupplier, SupplierMotor


@admin.register(MotorSupplier)
class MotorSupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    search_fields = ['name']


@admin.register(SupplierMotor)
class SupplierMotorAdmin(admin.ModelAdmin):
    list_display = ['model_number', 'model_name', 'motor_power', 'motor_speed', 'gearbox_ratio', 'gearbox_output_torque', 'compliant']
    list_filter = ['crane_type', 'compliant', 'supplier']
    search_fields = ['model_number', 'model_name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier', 'model_number', 'model_name', 'crane_type')
        }),
        ('Motor Specifications', {
            'fields': (
                'motor_power', 'motor_speed', 'motor_torque', 'motor_starting_torque',
                'motor_starting_factor', 'motor_voltage_50hz', 'motor_voltage_60hz',
                'motor_frame', 'motor_flange', 'motor_shaft', 'motor_cooling',
                'motor_ip_rating', 'motor_insulation_class', 'motor_efficiency_class',
                'motor_ambient_temp_min', 'motor_ambient_temp_max', 'motor_heater',
                'motor_coating', 'motor_color', 'motor_power_factor'
            )
        }),
        ('Gearbox Specifications', {
            'fields': (
                'gearbox_model', 'gearbox_ratio', 'gearbox_output_speed',
                'gearbox_output_torque', 'gearbox_nominal_torque',
                'gearbox_starting_torque_max', 'gearbox_tip_torque_max',
                'gearbox_efficiency_factor', 'gearbox_output_flange',
                'gearbox_output_shaft', 'gearbox_oil_capacity', 'gearbox_oil_type'
            )
        }),
        ('Compliance & Metadata', {
            'fields': ('compliant', 'compliance_notes', 'pdf_url')
        }),
    )
