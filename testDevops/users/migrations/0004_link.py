# Generated by Django 3.2 on 2021-05-05 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_generate_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_link', models.URLField()),
                ('shortened_link', models.URLField(blank=True, null=True)),
                ('clicks', models.IntegerField(default=0)),
            ],
        ),
    ]
