# Generated by Django 4.2 on 2025-03-15 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_usermessage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usermessage',
            old_name='message_text',
            new_name='content',
        ),
    ]
