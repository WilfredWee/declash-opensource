from rest_framework import serializers
from django.contrib.auth.models import User
from rocketscience.models import Debater, Room, Team, Session, DebaterAdmin
import autocomplete_light

class DebaterAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = DebaterAdmin
        fields = ('id', 'institution', 'user', 'sessions', 'rooms')

class DebaterSerializer(serializers.ModelSerializer):
    openedsessions = Session.objects.filter(openForReg=True)
    # teammates = serializers.HyperlinkedRelatedField(many=True, required=False,
    #                                               view_name='debater-detail',
    #                                               queryset=Debater.objects.filter(session__in=openedsessions))
    # session =  serializers.HyperlinkedRelatedField(many=False, required=False, view_name='session-detail',
    # queryset=openedsessions)
    session = serializers.PrimaryKeyRelatedField(
        many=False, required=True)
    teammates = serializers.PrimaryKeyRelatedField(many=True, required=False,
        queryset=Debater.objects.filter(session__in=openedsessions))


    class Meta:
        model = Debater
        fields = ('id', 'name', 'teammates', 'team',
                  'nov_pro', 'debate_judge_spectate', 'session', 'position', 'custom_requests')

    def validate_debate_judge_spectate(self, attrs, source):
        djs = attrs[source]
        try:
            teammates = attrs['teammates']
        except KeyError:
            return attrs

        if teammates and (djs == 'JUDGE' or djs == 'SPEC'):
            raise serializers.ValidationError(
                'You chose to judge/spectate. You may not have teammates.')
        return attrs


    def validate_session(self, attrs, source):
        session = attrs[source]
        if not session.openForReg:
            raise serializers.ValidationError('Session is closed.')
        return attrs


    def validate_teammates(self, attrs, source):

        def check_mate_session(session1, session2):
            if session1 == session2:
                return session1
            return False

        teammates = attrs[source]

        for d in teammates:
            if d.debate_judge_spectate == 'JUDGE' or d.debate_judge_spectate == 'SPEC' :
                raise serializers.ValidationError(
                    'Your chosen teammate has chosen to judge/spectate. Pairing up is not possible.')
        try:
            session = attrs['session']
        except KeyError:
            try:
                session = self.object.session
            except AttributeError:
                raise serializers.ValidationError(
                    'Could not get session, it might be closed.')
        format = session.format
        if not teammates:
            return attrs
        elif format == 'AP' and len(teammates) > 2:
            raise serializers.ValidationError(
                'You have chosen too many teammates.')
        elif (format == 'BP' or format == 'CP') and len(teammates) > 1:
            raise serializers.ValidationError(
                'You have chosen too many teammates.')
        elif format == 'AP' and len(teammates) <= 2:
            for mate in teammates:
                if mate.teammates.exists():
                    raise serializers.ValidationError(
                        'Your teammates already have at least a partner.')
                if mate.team and mate.team.exists():
                    raise serializers.ValidationError(
                        'Your chosen partner has already been assigned a team.')
        elif (format == 'BP' or format == 'CP') and len(teammates) <= 1:
            for mate in teammates:
                if mate.teammates.exists():
                    raise serializers.ValidationError(
                        'Your chosen partner already has a partner.')
                if mate.team and mate.team.exists():
                    raise serializers.ValidationError(
                        'Your chosen partner has already been assigned a team.')

        if reduce(check_mate_session, map(lambda mate: mate.session, teammates), session) == False:
            raise serializers.ValidationError(
                'Session is not the same as teammates.')
        else:
            return attrs



class RoomSerializer(serializers.ModelSerializer):
    ownername = serializers.Field(source='owner.user.username')

    class Meta:
        model = Room
        fields = ('id', 'location', 'ownername', 'group')


class TeamSerializer(serializers.ModelSerializer):
    # team_members = serializers.HyperlinkedRelatedField(
    #     many=True, view_name='debater-detail',
    #     required=False)

    session = serializers.PrimaryKeyRelatedField(required=True)
    team_members = serializers.PrimaryKeyRelatedField(
        many=True, required=True)
    room = serializers.PrimaryKeyRelatedField(required=True)
    room_location = serializers.Field(source='room.location')
    debaters = serializers.SerializerMethodField('get_debaters')

    class Meta:
        model = Team
        fields = ('id', 'room', 'room_location',
                  'position', 'session', 'team_members', 'debaters')
        depth = 1

    def get_debaters(self, obj):
        return list(Debater.objects.filter(team=obj))

    def validate_team_members(self, attrs, source):
        members = attrs[source]
        session = attrs['session']

        for d in members:
            if d.debate_judge_spectate == 'JUDGE' or d.debate_judge_spectate == 'SPEC':
                raise serializers.ValidationError(
                    'Cannot have a debater that wants to Judge/Spectate to be assigned in a team.')

        if session.format == 'AP':
            debaterCount = 3
        else:
            debaterCount = 2

        if len(members) != debaterCount:
            raise serializers.ValidationError(
                'There must be exactly 2 debaters in a team.')

        for d in members:
            if d.teammates:
                d.teammates.clear()
        return attrs

    def validate_room(self, attrs, source):
        room = attrs[source]
        session = attrs['session']

        if session.format == 'BP':
            maxTeamCount = 4
        else:
            maxTeamCount = 2

        if len(Team.objects.filter(room=room, session=session)) >= maxTeamCount:
            raise serializers.ValidationError(
                'Room is full.')
        return attrs

    def validate_position(self, attrs, source):
        position = attrs[source]
        try:
            room = attrs['room']
            session = attrs['session']
        except KeyError:
            raise serializers.ValidationError(
                'Must assign a room/session when creating a team.')

        if session.format == 'CP':
            for t in Team.objects.filter(room=room, session=session):
                if t.position == position:
                    raise serializers.ValidationError(
                        'Cannot have same positions in a room.')
        return attrs



class SessionSerializer(serializers.ModelSerializer):
    # openedsessions = Session.objects.filter(openForReg=True)
    owner = serializers.Field(source='owner.user.username')
    institution = serializers.Field(source='owner.institution')
    # debaters = DebaterSerializer(many=True, required=False)
    teams = TeamSerializer(many=True, required=False)

    def validate_openForReg(self, attrs, source):
        try:
            published = self.object.published
            finalized = self.object.finalized
        except AttributeError:
            try:
                published = attrs['published']
                finalized = attrs['finalized']
            except:
                published = False
                finalized = False

        openForReg = attrs[source]

        if openForReg:
            if finalized:
                raise serializers.ValidationError(
                    'Cannot permanently close session when it is open for registration')
            if published:
                raise serializers.ValidationError(
                    'Cannot publish teams when it is open for registration')
        return attrs


    class Meta:
        model = Session
        fields = ('id', 'reg_date', 'debaters', 'teams', 'owner',
            'institution','openForReg','canEditDebater', 'finalized',
            'published', 'partner_pref', 'room_pref', 'format')
        read_only_fields = ('id', 'reg_date', 'canEditDebater', 'debaters')
        depth = 1

