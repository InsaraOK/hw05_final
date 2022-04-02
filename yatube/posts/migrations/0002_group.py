# Generated by Django 2.2.19 on 2022-02-22 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('slug', models.FilePathField(path='/group/slug')),
                ('description', models.TextField()),
            ],
        ),
    ]
