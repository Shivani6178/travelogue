# Generated by Django 4.1 on 2022-09-19 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0007_alter_customerprofile_nationa_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprofile',
            name='profile_img',
            field=models.ImageField(blank=True, null=True, upload_to='profile'),
        ),
    ]
