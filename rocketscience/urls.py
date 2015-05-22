from django.conf.urls import patterns, url, include
from rocketscience import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'sessions', views.SessionViewSet, base_name='session')
router.register(r'debaters', views.DebaterViewSet, base_name='debater')
router.register(r'rooms', views.RoomViewSet, base_name='room')
router.register(r'teams', views.TeamViewSet, base_name='team')
router.register(r'debateradmins', views.DebaterAdminViewSet, base_name='debateradmin')

urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                                namespace='rest_framework')),
    )
