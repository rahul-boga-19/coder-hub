# Generated by Django 4.2 on 2025-03-20 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('date_subscribed', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterModelTable(
            name='project',
            table='Projects',
        ),
    ]
