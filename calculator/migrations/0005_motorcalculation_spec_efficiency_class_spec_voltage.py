from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0004_motorcalculation_spec_ambient_temp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='motorcalculation',
            name='spec_efficiency_class',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='motorcalculation',
            name='spec_voltage',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
