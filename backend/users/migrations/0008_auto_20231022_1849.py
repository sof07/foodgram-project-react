# Generated by Django 3.2.3 on 2023-10-22 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20231002_0915'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='authorsubscription',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='authorsubscription',
            constraint=models.UniqueConstraint(fields=('author', 'subscriber'), name='AuthorSubscription'),
        ),
    ]
