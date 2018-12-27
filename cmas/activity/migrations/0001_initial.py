# Generated by Django 2.1.4 on 2018-12-27 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('content', models.TextField(max_length=5000)),
                ('stime', models.DateTimeField()),
                ('ftime', models.DateTimeField()),
                ('ctime', models.DateTimeField(auto_now_add=True)),
                ('rtime', models.DateTimeField(auto_now=True)),
                ('act_type', models.CharField(max_length=10)),
                ('max_num', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Mnotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('content', models.CharField(max_length=200)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('is_delete', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sysnotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
