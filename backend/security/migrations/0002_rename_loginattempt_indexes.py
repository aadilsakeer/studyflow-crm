from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0001_initial'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='loginattempt',
            new_name='security_lo_created_e5f131_idx',
            old_name='security_lo_created_idx',
        ),
        migrations.RenameIndex(
            model_name='loginattempt',
            new_name='security_lo_ip_addr_053fc4_idx',
            old_name='security_lo_ip_success_idx',
        ),
    ]
