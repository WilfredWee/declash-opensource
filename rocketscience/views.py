import random

from rest_framework import permissions
from rocketscience.permissions import IsOwnerOrReadAndPostOnly, IsOwnerOrReadOnly, IsOwnerOrReadOpenedSessionsOnly
from rest_framework import viewsets
from rest_framework.renderers import HTMLFormRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from rocketscience.models import Session, Debater, Team, DebaterAdmin, Room
from rocketscience.serializers import DebaterSerializer, RoomSerializer, TeamSerializer, SessionSerializer, DebaterAdminSerializer

from rocketscience.declasher import DeClasher

class DebaterAdminViewSet(viewsets.ModelViewSet):
    serializer_class = DebaterAdminSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = DebaterAdmin.objects.all()

    def pre_save(self, obj):
        obj.user = self.request.user

class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsOwnerOrReadOpenedSessionsOnly)

    def pre_save(self, obj):
        # self.request.user.debateradmin.sessions.filter(openForReg=True).update(openForReg=False)
        Session.objects.filter(owner__user=self.request.user).update(openForReg=False, finalized=True)
        obj.owner = self.request.user.debateradmin

        if obj.finalized:
            obj.openForReg = False
            obj.published = False
            obj.canEditDebater = False

        if obj.published:
            obj.openForReg = False
            obj.canEditDebater = False

    def get_queryset(self):
        if self.request.user.id is None:
            return Session.objects.filter(Q(finalized=False), Q(openForReg=True) | Q(published=True))
        return Session.objects.filter(owner=self.request.user.debateradmin).filter(finalized=False)

    def retrieve(self, request, pk=None):
        queryset = Session.objects.filter(owner=request.user.debateradmin).filter(finalized=False)
        session = get_object_or_404(queryset, pk=pk)

        if request.QUERY_PARAMS.get('declashify', None) == 'true':
            roomGroupList = request.QUERY_PARAMS.get('roomGroupList', [])
            return DeClasher(session, roomGroupList).declashify()

        serializer = SessionSerializer(session)
        return Response(serializer.data)

class DebaterViewSet(viewsets.ModelViewSet):
    serializer_class = DebaterSerializer
    permission_classes = (IsOwnerOrReadAndPostOnly, IsOwnerOrReadOpenedSessionsOnly)

    def pre_save(self, obj):
        APPosSet = ['GV', 'OP']
        BPPosSet = ['OG', 'OO', 'CG', 'CO']
        if obj.session.format == 'AP':
            obj.position = random.choice(APPosSet)
        elif obj.session.format == 'BP':
            obj.position = random.choice(BPPosSet)

    def post_save(self, obj, created=False):
        if obj.teammates:
            for d in obj.teammates.all():
                obj.position = d.position
                d.debate_judge_spectate = obj.debate_judge_spectate

                for objmate in obj.teammates.all():
                    if (not objmate in d.teammates.all()) and (objmate.id != d.id):
                        d.teammates.add(objmate)

                d.save()
            
            obj.save()



    def get_queryset(self):
        if self.request.user.id is None:
            openedsessions = Session.objects.filter(openForReg=True)
            return Debater.objects.filter(session__in=openedsessions)
        else:
            ownersession = Session.objects.filter(owner=self.request.user.debateradmin)
            return Debater.objects.filter(session__in=ownersession)

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def pre_save(self, obj):
        obj.owner = self.request.user.debateradmin

    def get_queryset(self):
        if self.request.user.id is None:
            return Room.objects.none()
        return self.request.user.debateradmin.rooms.all()

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsOwnerOrReadOpenedSessionsOnly)

    def pre_save(self, obj):
        obj.owner = self.request.user.debateradmin

        APPosSet = ['GV', 'OP']
        BPPosSet = ['OG', 'OO', 'CG', 'CO']

        if not self.request.method in ['PUT', 'PATCH']:
            if obj.session.format == 'AP':
                obj.position = random.choice(APPosSet)
            elif obj.session.format == 'BP':
                obj.position = random.choice(BPPosSet)

    def get_queryset(self):
        publishedsessions = Session.objects.filter(published=True)
        
        if self.request.user.id is None:
            queryset = Team.objects.filter(session__in=publishedsessions)
            sessionID = self.request.QUERY_PARAMS.get('sessionID', None)
            if sessionID:
                queryset = queryset.filter(session_id=sessionID)

        else:
            ownersession = Session.objects.filter(owner=self.request.user.debateradmin, finalized=False)
            queryset = Team.objects.filter(session__in=ownersession)

        return queryset


