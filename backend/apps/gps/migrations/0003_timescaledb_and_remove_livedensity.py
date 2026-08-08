from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('gps', '0002_encrypt_gps_coordinates'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LiveDensity',
        ),
        migrations.RunSQL(
            sql="SELECT create_hypertable('gps_gpsping', 'created_at', if_not_exists => TRUE);",
            reverse_sql=""
        ),
    ]
