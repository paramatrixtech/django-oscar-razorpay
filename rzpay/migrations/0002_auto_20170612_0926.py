# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-12 08:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rzpay', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='razorpaytransaction',
            name='basket_id',
            field=models.CharField(blank=True, db_index=True, max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='razorpaytransaction',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='razorpaytransaction',
            name='txnid',
            field=models.CharField(db_index=True, default=b'7637a871af1147368d64cf452714', max_length=32),
        ),
        migrations.AddField(
            model_name='razorpaytransaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='razorpaytransaction',
            name='rz_id',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
    ]
