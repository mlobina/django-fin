# Generated by Django 3.1.2 on 2021-06-07 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20210606_1256'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name', 'price'], 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterField(
            model_name='collection',
            name='created',
            field=models.DateField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='updated',
            field=models.DateField(auto_now=True, verbose_name='дата обновления'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created',
            field=models.DateField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated',
            field=models.DateField(auto_now=True, verbose_name='дата обновления'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created',
            field=models.DateField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='product',
            name='updated',
            field=models.DateField(auto_now=True, verbose_name='дата обновления'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='created',
            field=models.DateField(auto_now_add=True, verbose_name='дата создания'),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='updated',
            field=models.DateField(auto_now=True, verbose_name='дата обновления'),
        ),
    ]
