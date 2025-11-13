from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_remove_user_academic_qualification_remove_user_age_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrequest',
            name='signature',
            field=models.ImageField(upload_to='request_photos/', null=True, blank=True),
        ),
    ]

