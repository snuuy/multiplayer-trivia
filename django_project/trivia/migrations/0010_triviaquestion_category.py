# Generated by Django 2.2 on 2019-04-23 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trivia', '0009_auto_20190423_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='triviaquestion',
            name='category',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]