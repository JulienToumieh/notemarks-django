# Generated by Django 5.1.7 on 2025-03-25 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Notemarks', '0006_notemark_contents'),
    ]

    operations = [
        migrations.AddField(
            model_name='notemark',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Notemarks.book'),
        ),
    ]
