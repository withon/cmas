# Generated by Django 2.1.4 on 2018-12-10 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='ctime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='ftime',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='activity',
            name='rtime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='stime',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='mnotice',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='sysnotice',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
