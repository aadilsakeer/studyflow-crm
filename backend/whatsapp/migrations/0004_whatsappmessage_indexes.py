from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0003_whatsappmessage_lead_whatsappmessage_message_type_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(
                fields=['company', '-created_at'],
                name='wa_msg_company_created_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(
                fields=['lead', '-created_at'],
                name='wa_msg_lead_created_idx',
            ),
        ),
    ]
