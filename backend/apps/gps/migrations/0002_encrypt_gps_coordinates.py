# Generated migration for Phase 1.3: GPS Model Encryption

from django.db import migrations, models
import apps.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gps', '0001_initial'),
    ]

    operations = [
        # Modify GpsPing location fields to use encrypted types
        # Note: timestamp (created_at) is NOT encrypted to support time-range queries
        
        migrations.AlterField(
            model_name='gpsping',
            name='latitude',
            field=apps.core.fields.EncryptedFloatField(),
        ),
        migrations.AlterField(
            model_name='gpsping',
            name='longitude',
            field=apps.core.fields.EncryptedFloatField(),
        ),
        migrations.AlterField(
            model_name='gpsping',
            name='accuracy',
            field=apps.core.fields.EncryptedIntegerField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='gpsping',
            name='altitude',
            field=apps.core.fields.EncryptedFloatField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='gpsping',
            name='speed',
            field=apps.core.fields.EncryptedFloatField(
                blank=True,
                null=True,
            ),
        ),
    ]
