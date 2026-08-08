# Generated migration for Phase 1.3: Medical Model Encryption

from django.db import migrations, models
import apps.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0001_initial'),
    ]

    operations = [
        # Modify Patient fields to use encrypted field types
        migrations.AlterField(
            model_name='patient',
            name='first_name',
            field=apps.core.fields.EncryptedCharField(
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name='patient',
            name='last_name',
            field=apps.core.fields.EncryptedCharField(
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name='patient',
            name='age',
            field=apps.core.fields.EncryptedIntegerField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='patient',
            name='condition',
            field=apps.core.fields.EncryptedTextField(),
        ),
        
        # Add index for medical camp + created_at queries
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(
                fields=['medical_camp', 'created_at'],
                name='medical_pat_medical_created_idx',
            ),
        ),
    ]
