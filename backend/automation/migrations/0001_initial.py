import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0004_task_management'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowAlertLog',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('alert_key', models.CharField(
                    db_index=True,
                    max_length=160,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.company',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'indexes': [
                    models.Index(
                        fields=['company', '-created_at'],
                        name='workflow_alert_co_created_idx',
                    ),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('alert_key', 'user'),
                        name='uniq_workflow_alert_per_user',
                    ),
                ],
            },
        ),
    ]
