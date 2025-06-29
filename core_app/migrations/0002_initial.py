# Generated by Django 5.2.3 on 2025-06-14 15:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core_app", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="department",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="managed_departments",
                to="users.employee",
                verbose_name="Προϊστάμενος",
            ),
        ),
        migrations.AddField(
            model_name="department",
            name="parent_department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core_app.department",
                verbose_name="Γονικό τμήμα",
            ),
        ),
        migrations.AddField(
            model_name="department",
            name="sdeu_supervisor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="supervised_sdeu",
                to="users.employee",
                verbose_name="Υπεύθυνος ΣΔΕΥ",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="city",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core_app.city",
                verbose_name="Έδρα",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.employee",
                verbose_name="Προϊστάμενος",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="parent_service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core_app.service",
                verbose_name="Γονική υπηρεσία",
            ),
        ),
        migrations.AddField(
            model_name="department",
            name="service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="core_app.service",
                verbose_name="Υπηρεσία",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="service_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core_app.servicetype",
                verbose_name="Τύπος υπηρεσίας",
            ),
        ),
        migrations.AddField(
            model_name="systemsetting",
            name="updated_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.employee",
                verbose_name="Ενημερώθηκε από",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="department",
            unique_together={("name", "service")},
        ),
    ]
