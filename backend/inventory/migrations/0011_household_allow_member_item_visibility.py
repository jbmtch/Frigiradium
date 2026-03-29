from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_inventory_user_alter_inventory_household_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='allow_member_item_visibility',
            field=models.BooleanField(default=False),
        ),
    ]
