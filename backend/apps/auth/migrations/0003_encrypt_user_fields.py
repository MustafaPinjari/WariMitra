# Generated migration for Phase 1.3: User Model Encryption

from django.db import migrations, models
import apps.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0002_alter_permission_options'),
    ]

    operations = [
        # Add new encrypted columns for User PII
        migrations.AddField(
            model_name='user',
            name='email_hash',
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                max_length=64,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='phone_hash',
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                max_length=64,
                null=True,
            ),
        ),
        
        # Modify existing fields to use encrypted field types
        # Note: Django doesn't support changing field types directly in some cases
        # This is a data migration approach that preserves backwards compatibility
        
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=apps.core.fields.EncryptedCharField(
                blank=True,
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=apps.core.fields.EncryptedCharField(
                blank=True,
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=apps.core.fields.EncryptedEmailField(
                blank=True,
                max_length=254,
                searchable=True,
                unique=False,
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=apps.core.fields.EncryptedPhoneField(
                blank=True,
                max_length=20,
                searchable=True,
            ),
        ),
    ]
