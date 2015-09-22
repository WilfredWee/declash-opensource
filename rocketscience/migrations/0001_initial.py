# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Debater',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reg_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=200)),
                ('nov_pro', models.CharField(max_length=3, choices=[(b'NOV', b'Novice'), (b'PRO', b'Pro')])),
                ('debate_judge_spectate', models.CharField(max_length=6, choices=[(b'DEBATE', b'Debate'), (b'JUDGE', b'Judge'), (b'DJ', b'Debate/Judge'), (b'SPEC', b'Spectate')])),
                ('position', models.CharField(blank=True, max_length=2, choices=[(b'GV', b'Government'), (b'OP', b'Opposition'), (b'OG', b'Opening Government'), (b'OO', b'Opening Opposition'), (b'CG', b'Closing Government'), (b'CO', b'Closing Opposition')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DebaterAdmin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('institution', models.CharField(max_length=200)),
                ('user', models.OneToOneField(related_name='debateradmin', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(max_length=100)),
                ('group', models.IntegerField(default=0, blank=True)),
                ('owner', models.ForeignKey(related_name='rooms', to='rocketscience.DebaterAdmin')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reg_date', models.DateTimeField(auto_now_add=True)),
                ('openForReg', models.BooleanField(default=True)),
                ('canEditDebater', models.BooleanField(default=True)),
                ('published', models.BooleanField(default=False)),
                ('finalized', models.BooleanField(default=False)),
                ('partner_pref', models.CharField(default=b'NPNP', max_length=4, choices=[(b'NNPP', b'Novice/Novice, Pro/Pro'), (b'NPNP', b'Mixed Novice and Pro'), (b'RAND', b'Random')])),
                ('room_pref', models.CharField(default=b'NNPP', max_length=4, choices=[(b'NNPP', b'Novice/Novice, Pro/Pro'), (b'NPNP', b'Mixed Novice and Pro'), (b'RAND', b'Random')])),
                ('format', models.CharField(max_length=2, choices=[(b'AP', b'Asian Parliamentary'), (b'BP', b'British Parliamentary'), (b'CP', b'Canadian Parliamentary')])),
                ('owner', models.ForeignKey(related_name='sessions', to='rocketscience.DebaterAdmin')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reg_date', models.DateTimeField(auto_now_add=True)),
                ('position', models.CharField(max_length=5, blank=True)),
                ('debate_judge_spectate', models.CharField(max_length=6, choices=[(b'DEBATE', b'Debate'), (b'JUDGE', b'Judge'), (b'DJ', b'Debate/Judge'), (b'SPEC', b'Spectate')])),
                ('room', models.ForeignKey(related_name='teams', blank=True, to='rocketscience.Room', null=True)),
                ('session', models.ForeignKey(related_name='teams', to='rocketscience.Session')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='debater',
            name='session',
            field=models.ForeignKey(related_name='debaters', to='rocketscience.Session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='debater',
            name='team',
            field=models.ForeignKey(related_name='team_members', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rocketscience.Team', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='debater',
            name='teammates',
            field=models.ManyToManyField(related_name='teammates_rel_+', null=True, to='rocketscience.Debater', blank=True),
            preserve_default=True,
        ),
    ]
