# Generated by Django 4.2.4 on 2023-10-05 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminview', '0003_color_size_productproperties'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]