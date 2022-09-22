# Generated by Django 4.0.2 on 2022-02-21 23:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import todos_los_nodos.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IPDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(unique=True, verbose_name='nombre')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4', unique=True, verbose_name='IP')),
                ('notas', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Nodo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.SlugField(max_length=10, unique=True)),
                ('port', models.CharField(blank=True, max_length=6, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Invalid port format', regex='([0-9]/){1,2}[0-9]+')])),
                ('notas', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.SlugField(unique=True)),
                ('descripcion', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=40)),
                ('apellidos', models.CharField(max_length=40)),
                ('login', models.SlugField(max_length=15, unique=True)),
                ('notas', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Telefono',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ext', models.CharField(blank=True, max_length=4, null=True, unique=True)),
                ('modelo', models.CharField(max_length=4)),
                ('serie', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('mac', todos_los_nodos.fields.MacField(unique=True)),
                ('notas', models.TextField(blank=True)),
                ('nodo', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos_los_nodos.nodo')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos_los_nodos.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('ipdevice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='todos_los_nodos.ipdevice')),
                ('tipo', models.CharField(choices=[('FA', 'FastEthernet'), ('GI', 'GigabyteEthernet')], max_length=2)),
                ('poe', models.BooleanField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='todos_los_nodos.site')),
            ],
            options={
                'verbose_name_plural': 'Switches',
            },
            bases=('todos_los_nodos.ipdevice',),
        ),
        migrations.AddField(
            model_name='nodo',
            name='switch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos_los_nodos.switch'),
        ),
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('ipdevice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='todos_los_nodos.ipdevice')),
                ('tipo', models.CharField(choices=[('PC', 'PC'), ('LAP', 'Lap'), ('MAC', 'Mac'), ('CAM', 'Camara')], max_length=3)),
                ('mac', todos_los_nodos.fields.MacField(unique=True)),
                ('nodo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos_los_nodos.nodo')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos_los_nodos.usuario')),
            ],
            bases=('todos_los_nodos.ipdevice',),
        ),
        migrations.CreateModel(
            name='AP',
            fields=[
                ('ipdevice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='todos_los_nodos.ipdevice')),
                ('nodo', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos_los_nodos.nodo')),
            ],
            options={
                'verbose_name': 'AP',
                'verbose_name_plural': 'APs',
            },
            bases=('todos_los_nodos.ipdevice',),
        ),
        migrations.AddConstraint(
            model_name='nodo',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('port__isnull', True), ('switch__isnull', True)), models.Q(('port__isnull', False), ('switch__isnull', False)), _connector='OR'), name='port_xnor_switch'),
        ),
    ]
