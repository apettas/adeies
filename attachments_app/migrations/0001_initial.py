# Generated by Django 5.2.3 on 2025-06-14 15:50

import attachments_app.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LeaveAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to=attachments_app.models.upload_to_path,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["pdf", "jpg", "jpeg"]
                            )
                        ],
                        verbose_name="Αρχείο",
                    ),
                ),
                (
                    "original_file_name",
                    models.CharField(
                        max_length=255, verbose_name="Αρχικό όνομα αρχείου"
                    ),
                ),
                (
                    "file_size",
                    models.PositiveIntegerField(verbose_name="Μέγεθος αρχείου (bytes)"),
                ),
                (
                    "file_type",
                    models.CharField(max_length=10, verbose_name="Τύπος αρχείου"),
                ),
                (
                    "file_hash",
                    models.CharField(
                        blank=True, max_length=64, verbose_name="Hash αρχείου"
                    ),
                ),
                ("description", models.TextField(verbose_name="Περιγραφή συνημμένου")),
                (
                    "attachment_type",
                    models.CharField(
                        choices=[
                            ("SUPPORTING_DOCUMENT", "Δικαιολογητικό έγγραφο"),
                            ("APPLICATION_PDF", "PDF αίτησης"),
                            ("DECISION_PDF", "PDF απόφασης"),
                            ("PROTOCOL_PDF", "PDF με πρωτόκολλο"),
                            ("SELF_DECLARATION", "Υπεύθυνη δήλωση"),
                            ("MEDICAL_CERTIFICATE", "Ιατρική βεβαίωση"),
                            ("BLOOD_DONATION_CERTIFICATE", "Βεβαίωση αιμοδοσίας"),
                        ],
                        default="SUPPORTING_DOCUMENT",
                        max_length=50,
                        verbose_name="Τύπος συνημμένου",
                    ),
                ),
                (
                    "is_sensitive",
                    models.BooleanField(
                        default=False,
                        help_text="Για αναρρωτικές άδειες",
                        verbose_name="Ευαίσθητο αρχείο",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Δημιουργήθηκε"
                    ),
                ),
            ],
            options={
                "verbose_name": "Συνημμένο Αρχείο",
                "verbose_name_plural": "Συνημμένα Αρχεία",
            },
        ),
    ]
