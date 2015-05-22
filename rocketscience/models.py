from django.db import models
from django.contrib.auth.models import User

class DebaterAdmin(models.Model):
    user = models.OneToOneField(User, related_name='debateradmin')
    institution = models.CharField(max_length=200)

    def __unicode__(self):
        return self.institution + ": " + self.user.username

class Session(models.Model):
    nov_pro_prefs = (
        ('NNPP', 'Novice/Novice, Pro/Pro'),
        ('NPNP', 'Mixed Novice and Pro'),
        ('RAND', 'Random'),
    )

    format_choices = (
        ('AP', 'Asian Parliamentary'),
        ('BP', 'British Parliamentary'),
        ('CP', 'Canadian Parliamentary'),
    )

    reg_date = models.DateTimeField(auto_now_add=True)
    openForReg = models.BooleanField(default=True)
    canEditDebater = models.BooleanField(default=True)
    published = models.BooleanField(default=False)
    finalized = models.BooleanField(default=False)
    partner_pref = models.CharField(
        max_length=4, choices=nov_pro_prefs, blank=False, default='NPNP')
    room_pref = models.CharField(
        max_length=4, choices=nov_pro_prefs, blank=False, default='NNPP')
    owner = models.ForeignKey('DebaterAdmin', related_name='sessions')
    format = models.CharField(max_length=2, choices=format_choices, blank=False)
    
    def __unicode__(self):
        return self.owner.institution + ": " + self.owner.user.username


class Debater(models.Model):
    nov_pro_choices = (
        ('NOV', 'Novice'),
        ('PRO', 'Pro'),
    )
    debate_judge_spectate_choices = (
        ('DEBATE', 'Debate'),
        ('JUDGE', 'Judge'),
        ('DJ', 'Debate/Judge'),
        ('SPEC', 'Spectate'),
    )
    position_choices = (
        ('GV', 'Government'),
        ('OP', 'Opposition'),
        ('OG', 'Opening Government'),
        ('OO', 'Opening Opposition'),
        ('CG', 'Closing Government'),
        ('CO', 'Closing Opposition'),
    )

    reg_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    teammates = models.ManyToManyField('self', blank=True, null=True)
    team = models.ForeignKey(
        'Team', blank=True, null=True, related_name='team_members', on_delete=models.SET_NULL)
    nov_pro = models.CharField(
        max_length=3, choices=nov_pro_choices, blank=False)
    debate_judge_spectate = models.CharField(
        max_length=6, choices=debate_judge_spectate_choices, blank=False)
    session = models.ForeignKey('Session', null=False, blank=False, related_name='debaters')
    position = models.CharField(max_length=2, choices=position_choices, blank=True)
    custom_requests = models.CharField(max_length=500, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Room(models.Model):
    location = models.CharField(max_length=100)
    owner = models.ForeignKey('DebaterAdmin', related_name='rooms')
    group = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.location


class Team(models.Model):
    # position_choices_bp = (
    #   ('OG', 'Opening Government'),
    #   ('OO', 'Opening Opposition'),
    #   ('CG', 'Closing Government'),
    #   ('CO', 'Closing Opposition'),
    #   )
    # position_choices_other = (
    #   ('GV', 'Government'),
    #   ('OP', 'Opposition'),
    #   )

    debate_judge_spectate_choices = (
        ('DEBATE', 'Debate'),
        ('JUDGE', 'Judge'),
        ('DJ', 'Debate/Judge'),
        ('SPEC', 'Spectate'),
    )

    reg_date = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(
        'Room', blank=True, null=True, related_name='teams')
    position = models.CharField(max_length=5, blank=True)
    session = models.ForeignKey('Session', null=False, related_name='teams')
    debate_judge_spectate = models.CharField(
        max_length=6, choices=debate_judge_spectate_choices, blank=False)

    def __unicode__(self):
        return "%i" % self.id
