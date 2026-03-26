from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Haiku',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('haiku', models.CharField(max_length=1000)),
                ('created_at', models.DateField()),
                ('haiku_picture', models.ImageField(blank=True, null=True, upload_to='haiku_pictures/')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bio', models.CharField(blank=True, default='', max_length=100)),
                ('profile_picture', models.ImageField(blank=True, default='profile_pictures/default_pic.png', null=True, upload_to='profile_pictures/')),
                ('created_at', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField()),
                ('haiku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='five_seven_five_app.Haiku')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='haiku',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='five_seven_five_app.Profile'),
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField()),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_text', models.CharField(max_length=100)),
                ('created_at', models.DateField()),
                ('haiku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='five_seven_five_app.Haiku')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]