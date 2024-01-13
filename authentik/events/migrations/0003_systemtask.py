# Generated by Django 5.0.1 on 2024-01-13 20:14

import uuid

from django.db import migrations, models

import authentik.core.models


class Migration(migrations.Migration):
    dependencies = [
        ("authentik_events", "0002_alter_notificationtransport_mode"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemTask",
            fields=[
                (
                    "expires",
                    models.DateTimeField(default=authentik.core.models.default_token_duration),
                ),
                ("expiring", models.BooleanField(default=True)),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField()),
                ("uid", models.TextField(null=True)),
                ("start_timestamp", models.DateTimeField(auto_now_add=True)),
                ("finish_timestamp", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.TextField(
                        choices=[
                            ("unknown", "Unknown"),
                            ("successful", "Successful"),
                            ("warning", "Warning"),
                            ("error", "Error"),
                        ]
                    ),
                ),
                ("description", models.TextField(null=True)),
                ("messages", models.JSONField()),
                ("task_call_module", models.TextField()),
                ("task_call_func", models.TextField()),
                ("task_call_args", models.JSONField(default=list)),
                ("task_call_kwargs", models.JSONField(default=dict)),
            ],
            options={
                "verbose_name": "System Task",
                "verbose_name_plural": "System Tasks",
                "permissions": [("rerun_task", "Rerun task")],
                "default_permissions": ["view"],
                "unique_together": {("name", "uid")},
            },
        ),
    ]
