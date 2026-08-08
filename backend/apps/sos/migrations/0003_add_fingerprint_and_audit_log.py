# Generated migration for Phase 1.2: DDoS Protection

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sos', '0002_initial'),  # Assuming this exists; adjust if needed
    ]

    operations = [
        # Modify DeviceFingerprint model
        migrations.CreateModel(
            name='DeviceFingerprint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('fingerprint', models.CharField(db_index=True, help_text='64-character hex string (SHA256 hash)', max_length=64, unique=True)),
                ('ip_address', models.GenericIPAddressField(db_index=True, help_text='IP address where fingerprint was first seen')),
                ('user_agent', models.TextField(blank=True, help_text='User-Agent header')),
                ('device_model', models.CharField(blank=True, help_text='Device model name', max_length=255)),
                ('app_version', models.CharField(blank=True, help_text='App version', max_length=20)),
                ('os_version', models.CharField(blank=True, help_text='OS version', max_length=50)),
            ],
            options={
                'verbose_name': 'Device Fingerprint',
                'verbose_name_plural': 'Device Fingerprints',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create SOSAuditLog model
        migrations.CreateModel(
            name='SOSAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('device_fingerprint', models.CharField(db_index=True, max_length=64)),
                ('device_model', models.CharField(blank=True, max_length=255)),
                ('app_version', models.CharField(blank=True, max_length=20)),
                ('ip_address', models.GenericIPAddressField(db_index=True)),
                ('user_agent', models.TextField(blank=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('radius', models.IntegerField(blank=True, null=True)),
                ('rate_limit_ip_status', models.CharField(choices=[('PASS', 'Passed'), ('REJECT', 'Rejected'), ('WARN', 'Warning')], default='PASS', max_length=20)),
                ('rate_limit_device_status', models.CharField(choices=[('PASS', 'Passed'), ('REJECT', 'Rejected'), ('WARN', 'Warning')], default='PASS', max_length=20)),
                ('geofence_status', models.CharField(choices=[('PASS', 'Passed'), ('REJECT', 'Rejected')], default='PASS', max_length=20)),
                ('result', models.CharField(choices=[('SUCCESS', 'Alert Created'), ('RATE_LIMITED_IP', 'Rate Limited (IP)'), ('RATE_LIMITED_DEVICE', 'Rate Limited (Device)'), ('INVALID_LOCATION', 'Invalid Location'), ('INVALID_FINGERPRINT', 'Invalid Fingerprint'), ('ERROR', 'Error')], db_index=True, max_length=50)),
                ('reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('sos_alert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='sos.sosalert')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sos_audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SOS Audit Log',
                'verbose_name_plural': 'SOS Audit Logs',
                'ordering': ['-created_at'],
            },
        ),
        
        # Add indexes to DeviceFingerprint
        migrations.AddIndex(
            model_name='devicefingerprint',
            index=models.Index(fields=['fingerprint', 'created_at'], name='sos_device_fp_created_idx'),
        ),
        migrations.AddIndex(
            model_name='devicefingerprint',
            index=models.Index(fields=['ip_address', 'created_at'], name='sos_device_ip_created_idx'),
        ),
        
        # Add indexes to SOSAuditLog
        migrations.AddIndex(
            model_name='sosauditlog',
            index=models.Index(fields=['created_at', 'result'], name='sos_audit_created_result_idx'),
        ),
        migrations.AddIndex(
            model_name='sosauditlog',
            index=models.Index(fields=['ip_address', 'created_at'], name='sos_audit_ip_created_idx'),
        ),
        migrations.AddIndex(
            model_name='sosauditlog',
            index=models.Index(fields=['device_fingerprint', 'created_at'], name='sos_audit_fp_created_idx'),
        ),
        migrations.AddIndex(
            model_name='sosauditlog',
            index=models.Index(fields=['result', 'created_at'], name='sos_audit_result_created_idx'),
        ),
    ]
