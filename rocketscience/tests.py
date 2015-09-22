import random

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rocketscience.models import *

# Create your tests here.

class DeClasherTestCase(APITestCase):
    def test_declashify(self):
        def test_declashify_specific(format, partner_pref, room_pref, username):
            # Login, then create a session.
            user = User.objects.create_user(username, 'tester@test.com', 'tester')
            dAdmin = DebaterAdmin.objects.create(
                user=user,
                institution='testInst')
            self.client.force_authenticate(user=user)

            sessionCreateData = {'partner_pref':partner_pref, 'room_pref': room_pref, 'format': format}
            sessionCreateResponse = self.client.post('/api/sessions/', sessionCreateData, format='json')
            sessionID = sessionCreateResponse.data['id']
            self.assertEqual(sessionCreateResponse.status_code, status.HTTP_201_CREATED)

            # Create a bunch of debaters
            djs = ['DEBATE', 'DJ', 'JUDGE', 'SPEC']
            djsNoJudge = ['DEBATE', 'DJ']
            novpro = ['NOV', 'PRO']
            position = ['GV', 'OP']
            teamPos = position[:]
            workRoom = None
            teamAcc = 0
            randomRange = random.randrange(100, 300) 

            # Create debaters with no teammates
            for i in range(0, randomRange):
                debaterData = {'name': 'testDebater',
                    'teammates': [],
                    'nov_pro': random.choice(novpro),
                    'debate_judge_spectate': random.choice(djs),
                    'session': sessionID,
                    'position': random.choice(position),
                    }
                debaterCreateResponse = self.client.post('/api/debaters/',
                    debaterData, format='json')
                # print(debaterCreateResponse.data)
                self.assertEqual(debaterCreateResponse.status_code, status.HTTP_201_CREATED)

            # Create debaters with 1 teammate
            randomRange = random.randrange(100, 300) 
            for i in range(0, randomRange):
                teammate = {'name': 'testTeammate',
                    'teammates': [],
                    'nov_pro': random.choice(novpro),
                    'debate_judge_spectate': random.choice(djsNoJudge),
                    'session': sessionID,
                    'position': random.choice(position),
                    }
                teammateCreateResponse = self.client.post('/api/debaters/',
                    teammate, format='json')
                self.assertEqual(teammateCreateResponse.status_code, status.HTTP_201_CREATED)
                teammateID = teammateCreateResponse.data['id']

                debater = {'name': 'testDebater',
                    'teammates': [teammateID],
                    'nov_pro': random.choice(novpro),
                    'debate_judge_spectate': random.choice(djsNoJudge),
                    'session': sessionID,
                    'position': random.choice(position),
                    }
                debaterCreateResponse = self.client.post('/api/debaters/',
                    debater, format='json')
                self.assertEqual(debaterCreateResponse.status_code, status.HTTP_201_CREATED)
                debaterID = debaterCreateResponse.data['id']

                if format != 'AP':
                    teamRandom = random.randrange(100)
                    if teamRandom < 25:
                        if teamRandom < 5 or teamAcc == 0:
                            workRoom = None
                            workRoom = Room.objects.create(
                                owner=dAdmin,
                                location='boo',
                                group=0)
                        
                        teamAcc+=1
                        if format == 'BP':
                            teamPos = ['GV']

                        team = {
                        'team_members': [teammateID, debaterID],
                        'position': teamPos.pop(),
                        'room': workRoom.id,
                        'session': sessionID
                        }

                        teamCreateResponse = self.client.post('/api/teams/',
                            team, format='json')
                        self.assertEqual(teamCreateResponse.status_code, status.HTTP_201_CREATED)

                        if format == 'BP' and teamAcc == 4:
                            teamAcc = 0
                        elif format != 'BP' and teamAcc == 2:
                            teamAcc = 0
                            teamPos = position[:]



            # Create debaters with 2 teammates.
            if format == 'AP':
                randomRange = random.randrange(100, 300) 
                for i in range(0, randomRange):
                    teammate1 = {'name': 'testTeammate1',
                        'teammates': [],
                        'nov_pro': random.choice(novpro),
                        'debate_judge_spectate': random.choice(djsNoJudge),
                        'session': sessionID,
                        'position': random.choice(position),
                        }
                    teammate1CreateResponse = self.client.post('/api/debaters/',
                        teammate1, format='json')
                    self.assertEqual(teammate1CreateResponse.status_code, status.HTTP_201_CREATED)
                    teammate1ID = teammate1CreateResponse.data['id']

                    teammate2 = {'name': 'testTeammate2',
                        'teammates': [],
                        'nov_pro': random.choice(novpro),
                        'debate_judge_spectate': random.choice(djsNoJudge),
                        'session': sessionID,
                        'position': random.choice(position),
                        }

                    teammate2CreateResponse = self.client.post('/api/debaters/',
                        teammate2, format='json')
                    self.assertEqual(teammate2CreateResponse.status_code, status.HTTP_201_CREATED)
                    teammate2ID = teammate2CreateResponse.data['id']

                    debater = {'name': 'testDebater',
                        'teammates': [teammate1ID, teammate2ID],
                        'nov_pro': random.choice(novpro),
                        'debate_judge_spectate': random.choice(djs),
                        'session': sessionID,
                        'position': random.choice(position),
                        }

                    debaterCreateResponse = self.client.post('/api/debaters/',
                        teammate1, format='json')
                    self.assertEqual(debaterCreateResponse.status_code, status.HTTP_201_CREATED)
                    debaterID = debaterCreateResponse.data['id']

                    teamRandom = random.randrange(100)
                    if teamRandom < 25:
                        if teamRandom < 5 or teamAcc == 0:
                            workRoom = None
                            workRoom = Room.objects.create(
                                owner=dAdmin,
                                location='boo',
                                group=0)
                        
                        teamAcc+=1

                        team = {
                        'team_members': [teammate1ID, teammate2ID, debaterID],
                        'position': random.choice(position),
                        'room': workRoom.id,
                        'session': sessionID,
                        }


                        teamCreateResponse = self.client.post('/api/teams/',
                            team, format='json')
                        self.assertEqual(teamCreateResponse.status_code, status.HTTP_201_CREATED)

                        if teamAcc == 2:
                            teamAcc = 0

            # Close the session
            sessionURL = '/api/sessions/' + str(sessionID) + '/'
            sessionCloseResponse = self.client.patch(sessionURL, {'openForReg': False}, format='json')
            self.assertEqual(sessionCloseResponse.status_code, status.HTTP_200_OK)

            declashifyURL = sessionURL + '?declashify=true/'
            declashifyResponse = self.client.get(sessionURL, {'declashify': 'true'}, format='json')

            sessionGetResponse = self.client.get(sessionURL)
            # f = open('C:/Users/WilfredAdmin/Desktop/testoutput.txt', 'w')
            # f.write(str(sessionGetResponse))
            # f.close()
            self.assertEqual(declashifyResponse.status_code, status.HTTP_200_OK)
            return sessionGetResponse

        res = test_declashify_specific('AP', 'NNPP', 'RAND', 'tester1')
        f = open('C:/Users/WilfredAdmin/Desktop/APNNPP.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('AP', 'NPNP', 'RAND', 'tester2')
        f = open('C:/Users/WilfredAdmin/Desktop/APNPNP.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('AP', 'RAND', 'RAND', 'tester3')
        f = open('C:/Users/WilfredAdmin/Desktop/APRAND.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('BP', 'NPNP', 'RAND', 'tester4')
        f = open('C:/Users/WilfredAdmin/Desktop/BPNPNP.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('BP', 'NNPP', 'RAND', 'tester5')
        f = open('C:/Users/WilfredAdmin/Desktop/BPNNPP.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('BP', 'RAND', 'RAND', 'tester6')
        f = open('C:/Users/WilfredAdmin/Desktop/BPRAND.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('CP', 'NPNP', 'RAND', 'tester7')
        f = open('C:/Users/WilfredAdmin/Desktop/CPNPNP.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('CP', 'NNPP', 'RAND', 'tester8')
        f = open('C:/Users/WilfredAdmin/Desktop/CPNNPP.txt', 'w')
        f.write(str(res))
        res = test_declashify_specific('CP', 'RAND', 'RAND', 'tester9')
        f = open('C:/Users/WilfredAdmin/Desktop/CPRAND.txt', 'w')
        f.write(str(res))



