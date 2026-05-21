from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0005_motorcalculation_spec_efficiency_class_spec_voltage'),
    ]

    operations = [
        migrations.AddField(
            model_name='motorcalculation',
            name='bevel_efficiency',
            field=models.FloatField(default=0.95),
        ),
        migrations.AlterField(
            model_name='motorcalculation',
            name='torque_check',
            field=models.CharField(max_length=30),
        ),
    ]
