# Generated migration for Phase 1.3: Decryption Audit Log

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_auditlog_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecryptionAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('service_account', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('record_type', models.CharField(
                    choices=[('User', 'User PII'), ('Patient', 'Patient Medical Record'), ('GPS', 'GPS Location')],
                    db_index=True,
                    max_length=50,
                )),
                ('record_id', models.IntegerField(db_index=True)),
                ('field_name', models.CharField(max_length=100)),
                ('result', models.CharField(
                    choices=[('success', 'Successful'), ('failure', 'Failed')],
                    db_index=True,
                    max_length=20,
                )),
                ('reason', models.CharField(blank=True, max_length=500, null=True)),
                ('ip_address', models.CharField(default='unknown', max_length=50)),
                ('user_agent', models.TextField(default='unknown')),
                ('request_path', models.CharField(blank=True, max_length=500, null=True)),
                ('key_version', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        
        # Add indexes for searchability
        migrations.AddIndex(
            model_name='decryptionauditlog',
            index=models.Index(fields=['timestamp'], name='audit_decry_timestam_idx'),
        ),
        migrations.AddIndex(
            model_name='decryptionauditlog',
            index=models.Index(fields=['user_id'], name='audit_decry_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='decryptionauditlog',
            index=models.Index(fields=['record_id'], name='audit_decry_record_id_idx'),
        ),
        migrations.AddIndex(
            model_name='decryptionauditlog',
            index=models.Index(fields=['record_type', 'record_id'], name='audit_decry_record_type_id_idx'),
        ),
        migrations.AddIndex(
            model_name='decryptionauditlog',
            index=models.Index(fields=['user_id', 'timestamp'], name='audit_decry_user_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='decryptionauditlog',
            index=models.Index(fields=['result', 'timestamp'], name='audit_decry_result_timestamp_idx'),
        ),
        
        # Add check constraint for timestamp (immutability enforcement)
        migrations.AddConstraint(
            model_name='decryptionauditlog',
            constraint=models.CheckConstraint(
                check=models.Q(('timestamp__isnull', False)),
                name='decryption_audit_timestamp_not_null',
            ),
        ),
    ]
