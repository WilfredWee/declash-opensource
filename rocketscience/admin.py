from django.contrib import admin
from rocketscience.models import Debater, Room, Team, DebaterAdmin

# class DebaterInline(admin.StackedInline):
# 	model = Debater
# 	extra = 2

# class TeamInline(admin.StackedInline):
# 	model = Team
# 	extra = 4

# class DebaterAdmin(admin.ModelAdmin):
# 	fields = ['name', 'team', 'nov_pro', 'debate_judge']

# class RoomAdmin(admin.ModelAdmin):
# 	fields = ['location']
# 	inlines = [TeamInline]

# class TeamAdmin(admin.ModelAdmin):
# 	fields = ['room', 'format', 'position']
# 	inlines = [DebaterInline]

admin.site.register(Debater)
admin.site.register(Room)
admin.site.register(Team)
admin.site.register(DebaterAdmin)