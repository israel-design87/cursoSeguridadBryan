# Generated by Django 5.2.3 on 2025-07-04 01:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0011_perfilusuario_apellido_materno_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='perfilusuario',
            options={'ordering': ['apellido_paterno', 'apellido_materno', 'nombre']},
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='nombre_razon_social',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Nombre o razón social'),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='ocupacion_especifica',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='refc_empresa',
            field=models.CharField(blank=True, default='', max_length=13, verbose_name='RFC de la empresa'),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='apellido_materno',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='apellido_paterno',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='curp',
            field=models.CharField(max_length=18, unique=True, validators=[django.core.validators.RegexValidator(message='CURP no tiene un formato válido.', regex='^[A-Z]{4}\\d{6}[HM][A-Z]{5}[A-Z0-9]\\d$')]),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='nombre',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
