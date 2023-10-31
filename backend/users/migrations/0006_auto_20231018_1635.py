# Generated by Django 3.2.3 on 2023-10-18 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_follow_unique_author_follower'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_author_follower',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author', 'follower'), name='unique_follow'),
        ),
    ]
