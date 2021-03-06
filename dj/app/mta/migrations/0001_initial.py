# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-16 19:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cause', models.TextField()),
                ('start', models.DateTimeField()),
                ('stop', models.DateTimeField(blank=True, null=True)),
                ('is_rush', models.NullBooleanField()),
                ('is_weekend', models.NullBooleanField()),
                ('length', models.PositiveIntegerField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DelayAlert',
            fields=[
                ('alert_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='mta.Alert')),
            ],
            bases=('mta.alert',),
        ),
        migrations.AddField(
            model_name='line',
            name='mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mta.Mode'),
        ),
        migrations.AddField(
            model_name='alert',
            name='line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mta.Line'),
        ),
    ]
