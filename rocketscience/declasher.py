#DeClasher classes and methods
import math
import random
from rocketscience.models import Session, Room, Team, Debater
from rocketscience.serializers import SessionSerializer
from rest_framework.response import Response

class DeClasher:
    def __init__(self, session, roomGroupList):
        self.session = session
        self.requiredProJudges = 0
        self.roomGroupList = roomGroupList
        self.debatingRoomCount = 0
        self.debaters = list(session.debaters.all())
        self.teams = list(session.teams.filter(debate_judge_spectate="DEBATE"))
        self.createdTeams = []

        self.noOfRooms = 0


        roomList = []
        if session.teams.count() > 0:
            for t in session.teams.all():
                if not t.room in roomList:
                    roomList.append(t.room)


        self.requiredProJudges = len(roomList)

    # Must return a serialized Response
    def declashify(self):
        if self.session.format == 'AP':
            return self.declashifyAP()
        elif self.session.format == 'BP':
            return self.declashifyBP()
        elif self.session.format == 'CP':
            return self.declashifyCP()

        serializer = SessionSerializer(self.session)
        return Response(serializer.data)

    def checkAndSwitchJudge(self, relevantDebaters, roomSize):
        def switchToJudge(amtToSwitch, debaterQueryset):
            if amtToSwitch > 0:
                queryset = debaterQueryset.filter(teammates__isnull=True)
                iterateAmt = min(queryset.count(), amtToSwitch)

                for d in queryset[:iterateAmt]:
                    d.debate_judge_spectate='JUDGE'
                    amtToSwitch -= 1
                    d.save()

            if amtToSwitch > 0:
                queryset = debaterQueryset.filter(teammates__isnull=False)

                iterateAmt = amtToSwitch

                for d in queryset[:iterateAmt]:
                    if d.teammates.all():
                        d.debate_judge_spectate='JUDGE'
                        amtToSwitch-=1
                        d2 = d.teammates.all()[0]
                        if amtToSwitch > 0:
                            d2.debate_judge_spectate='JUDGE'
                            d2.save()
                            amtToSwitch-=1
                        d.teammates.remove(d2)
                        d.save()
                        d2.save()
                        if amtToSwitch == 0:
                            break
            return amtToSwitch

        relevantDebatersCount = relevantDebaters.count()
        # Start by seeing how many judges we need and how many judges we have.
        needJudgeCount = relevantDebatersCount/roomSize
        remainderDebaterCount = relevantDebatersCount % roomSize
        haveJudgeCount = self.session.debaters.filter(
            debate_judge_spectate='JUDGE',
            nov_pro='PRO').count()

        # print('needJudgeCount: ' + str(needJudgeCount))
        # print('remainderDebaterCount: ' + str(remainderDebaterCount))
        # print('haveJudgeCount: ' + str(haveJudgeCount))

        # Variables
        DJProCount = 0
        DJNovCount = 0
        DProCount = 0

        # Accumulators
        DJProToSwitch = 0
        DJNovToSwitch = 0
        DProToSwitch = 0

        # First, set the DJ that are Pro to Judge

        # RemainderDebaterCount >= 0 after this 'if' block executes.
        if haveJudgeCount < needJudgeCount:
            # diffJudgeCount = needJudgeCount - haveJudgeCount
            DJProCount = self.session.debaters.filter(
                debate_judge_spectate='DJ',
                nov_pro='PRO',
                team__isnull=True).count()


            # You are dealing with the remainders, don't have to worry about needJudgeCount
            if  DJProCount >= remainderDebaterCount:
                DJProToSwitch += remainderDebaterCount
                haveJudgeCount += remainderDebaterCount
                remainderDebaterCount = 0

                # The amount of DJPro left after taking into account of remainder.
                DJProCount = DJProCount - DJProToSwitch
                # remainderDebaterCount == 0
                while (haveJudgeCount < needJudgeCount) and (DJProCount > 0):
                    if DJProCount >= roomSize:
                        DJProToSwitch += roomSize
                        haveJudgeCount += roomSize
                        needJudgeCount -= 1
                        DJProCount -= roomSize
                    else:
                        DJProToSwitch += DJProCount
                        haveJudgeCount += DJProCount
                        needJudgeCount -= 1
                        remainderDebaterCount = roomSize - DJProCount
                        DJProCount = 0


            # If DJPro < remainders
            # You are dealing with the remainders, don't have to worry about needJudgeCount
            else:
                DJProToSwitch += DJProCount
                haveJudgeCount += DJProCount
                remainderDebaterCount -= DJProCount


        # Exhausted DJPro, now transfer DJNov
        if haveJudgeCount < needJudgeCount:
            # print('DJProCount must be zero, count: ' + str(DJProCount))
            DJNovCount = self.session.debaters.filter(
                debate_judge_spectate='DJ',
                nov_pro='NOV',
                team__isnull=True).count()

            if  DJNovCount >= remainderDebaterCount:
                DJNovToSwitch += remainderDebaterCount
                remainderDebaterCount = 0

                # The amount of DJNov left after taking into account of remainder.
                DJNovCount = DJNovCount - DJNovToSwitch
                # remainderDebaterCount == 0
                while haveJudgeCount < needJudgeCount and DJNovCount > 0:
                    if DJNovCount >= roomSize:
                        DJNovToSwitch += roomSize
                        needJudgeCount -= 1
                        DJNovCount -= roomSize
                    else:
                        DJNovToSwitch += DJNovCount
                        needJudgeCount -= 1 #do we see a possible problem here?
                        remainderDebaterCount = roomSize - DJNovCount
                        DJNovCount = 0

            # If DJNov < remainders
            # You are dealing with the remainders, don't have to worry about needJudgeCount
            else:
                DJNovToSwitch += DJNovCount
                remainderDebaterCount -= DJNovCount
                DJNovCount = 0

        # Exhausted DJNov, now deal with DPro
        if haveJudgeCount < needJudgeCount:
            DProCount = self.session.debaters.filter(
                debate_judge_spectate='DEBATE',
                nov_pro='PRO',
                team__isnull=True).count()

            # You are dealing with the remainders, don't have to worry about needJudgeCount
            if  DProCount >= remainderDebaterCount:
                DProToSwitch += remainderDebaterCount
                haveJudgeCount += remainderDebaterCount
                remainderDebaterCount = 0

                # The amount of DJPro left after taking into account of remainder.
                DProCount = DProCount - DProToSwitch

                # remainderDebaterCount == 0
                while haveJudgeCount < needJudgeCount and DProCount > 0:
                    if DProCount >= roomSize:
                        DProToSwitch += roomSize
                        haveJudgeCount += roomSize
                        needJudgeCount -= 1
                        DProCount -= roomSize
                    else:
                        DProToSwitch += DProCount
                        haveJudgeCount += DProCount
                        needJudgeCount -= 1
                        remainderDebaterCount = roomSize - DProCount
                        DProCount = 0

            # If DJPro < remainders
            # You are dealing with the remainders, don't have to worry about needJudgeCount
            else:
                DProToSwitch += DProCount
                haveJudgeCount += DProCount
                remainderDebaterCount -= DProCount
                DProCount = 0

        # remainderDebater at this point are: DNov
        # DNovCount must >= remainderDebaterCount

        # I'm not sure if I want to worry about remainderType just yet...


        DJProToSwitch = switchToJudge(DJProToSwitch, relevantDebaters.filter(debate_judge_spectate='DJ', nov_pro='PRO'))
        DJNovToSwitch = switchToJudge(DJNovToSwitch, relevantDebaters.filter(debate_judge_spectate='DJ', nov_pro='NOV'))
        DProToSwitch = switchToJudge(DProToSwitch, relevantDebaters.filter(debate_judge_spectate='DEBATE', nov_pro='PRO'))

        # print('DJProToSwitch: ' + str(DJProToSwitch))
        # print('DJNovToSwitch: ' + str(DJNovToSwitch))
        # print('DProToSwitch: ' + str(DProToSwitch))


        self.debatingRoomCount = needJudgeCount
        # Might be a good idea to print out needJudgeCount, debug it.



    def checkAndSwitchJudge2(self):
        def sortJudgePriority(debater):
            if debater.nov_pro == "PRO" and debater.debate_judge_spectate == "DJ":
                if (debater.teammates is not None) and len(debater.teammates.all()) <= 0:
                    return 9100
                else:
                    return 9000
            elif debater.nov_pro == "NOV" and debater.debate_judge_spectate == "DJ":
                return 8000
            elif debater.nov_pro == "PRO" and debater.debate_judge_spectate == "DEBATE":
                return 7000
            else:
                return 6000


        relevantDebaters = filter(lambda debater: debater.debate_judge_spectate in ["DEBATE", "DJ"], self.debaters)

        requiredProJudgeCount = len(relevantDebaters) / 8
        haveProJudgeCount = len(filter(lambda debater: debater.debate_judge_spectate == "JUDGE", self.debaters))

        if haveProJudgeCount >= requiredProJudgeCount:
            return

        needProJudgeCount = requiredProJudgeCount - haveProJudgeCount

        sortedDebaters = sorted(relevantDebaters, key=sortJudgePriority)

        debatersToSwitch = sortedDebaters[:needProJudgeCount]

        # TODO:Figure out how many to minus from here.

        for debater in debatersToSwitch:
            debater.debate_judge_spectate = "JUDGE"
            debater.save()

        self.debaters = Debater.objects.filter(session=self.session.id)




    def pairUp(self, relevantDebaters):
        threeMembersMode = (self.session.format == 'AP')

        # loneDebaters is a Queryset, leftOvers is a list of debaters
        def pairUpNNPP(loneDebaters, leftOvers):
            inc = 3 if threeMembersMode else 2
            assert len(leftOvers) < inc

            loneDebaters = list(loneDebaters)
            random.shuffle(loneDebaters)

            # If total amount of debaters cannot make a team,
            # Straight away return the left over.
            if (len(loneDebaters) + len(leftOvers)) < inc:
                leftOvers = loneDebaters + leftOvers

            else:
                # Deal with left-overs, take an extra loneDebater if needed in AP.
                if leftOvers:
                    partner = loneDebaters.pop()
                    team = Team.objects.create(
                        session=self.session,
                        debate_judge_spectate='DEBATE')
                    if not team:
                        raise Error("yo")

                    partner.team = team
                    partner.save()
                    for leftOverDebater in leftOvers:
                        leftOverDebater.team = team
                        leftOverDebater.save()


                    if threeMembersMode and len(leftOvers) == 1:
                        # Since leftOvers is 1, we should have at least 2 loneDebaters.
                        if len(loneDebaters) > 0:
                            partner = loneDebaters.pop()
                            partner.team = team
                            partner.save()
                        else:
                            print('Error, this should not have happened.')

                    # You should have exhausted leftOvers here.
                    leftOvers = []

                assert len(leftOvers) ==  0
                for i in range(0, len(loneDebaters), inc):
                        # if i is before or at the end of list offset by teammates count in a team
                        if i < (len(loneDebaters) - (inc - 1)):
                            team = Team.objects.create(
                                session=self.session,
                                debate_judge_spectate='DEBATE',
                                position=loneDebaters[i].position)
                            if not team:
                                raise Error("yo")
                            loneDebaters[i].team = team
                            loneDebaters[i+1].team = team
                            loneDebaters[i].save()
                            loneDebaters[i+1].save()

                            if threeMembersMode:
                                loneDebaters[i+2].team = team
                                loneDebaters[i+2].save()
                        else:
                            # construct leftover list based on amount of leftover
                            if i == len(loneDebaters) - 1:
                                leftOvers = [loneDebaters[i]]
                                break
                            else:
                                leftOvers = [loneDebaters[i], loneDebaters[i+1]]
                                break

            return leftOvers

        def pairUpNPNP(loneDebaters):
            loneNovices = list(loneDebaters.filter(nov_pro='NOV'))
            lonePros = list(loneDebaters.filter(nov_pro='PRO'))

            iterateAmt = min(len(loneNovices), len(lonePros))

            if not threeMembersMode:
                for i in range(0, iterateAmt):
                    team = Team.objects.create(
                        session=self.session,
                        debate_judge_spectate='DEBATE',
                        position=loneNovices[i].position)
                    if not team:
                        raise Error("yo")
                    loneNovices[i].team = team
                    lonePros[i].team = team
                    loneNovices[i].save()
                    lonePros[i].save()

            else:
                div3Amt = iterateAmt/3
                novSwitch = True

                i = 0
                while div3Amt > 0:
                    team = Team.objects.create(
                        session=self.session,
                        debate_judge_spectate='DEBATE',
                        position=loneNovices[i].position)
                    if not team:
                        raise Error("yo")

                    div3Amt -= 1
                    if novSwitch:
                        loneNovices[i].team = team
                        loneNovices[i+1].team = team
                        lonePros[i].team = team
                        novSwitch = False
                        loneNovices[i].save()
                        loneNovices[i+1].save()
                        lonePros[i].save()
                        i+=1

                    else:
                        lonePros[i].team = team
                        lonePros[i+1].team = team
                        loneNovices[i+1].team = team
                        novSwitch = True
                        lonePros[i].save()
                        lonePros[i+1].save()
                        loneNovices[i+1].save()
                        i+=2

            leftOvers = pairUpNNPP(loneDebaters, [])
            return leftOvers

        # Pair up debaters who already have selected their teammates.
        teammateAcc = []
        incompleteTeamAcc = []
        withMates = relevantDebaters.exclude(teammates__isnull=True)


        for d in withMates:
            # If debater is not in a team and not already paired up by this loop
            if (not d.team) and (not (d in teammateAcc)):
                team = Team.objects.create(
                    session=self.session,
                    debate_judge_spectate='DEBATE',
                    position=d.position)
                if not team:
                        raise Error("yo")

                if threeMembersMode and d.teammates.all().count() < 2:
                    incompleteTeamAcc.append(team)

                for mate in d.teammates.all():
                    mate.team = team
                    mate.save()
                    teammateAcc.append(mate)

                d.team = team
                d.save()
                team.save()


        # Complete the incomplete team, team has at least 2 members
        if threeMembersMode:
            for team in incompleteTeamAcc:
                debaterProNov = team.team_members.all()[0].nov_pro
                if debaterProNov == 'PRO':
                    getProNov = 'NOV'
                else:
                    getProNov = 'PRO'

                lastDebater = relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DEBATE',
                    nov_pro=getProNov).order_by('?')

                # If lastDebater doesn't exist, don't set debate_judge_spectate requirement
                if not lastDebater:
                    lastDebater = relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    nov_pro=getProNov).order_by('?')

                    # If lastDebater still doesn't exist, don't set nov_pro requirement
                    if not lastDebater:
                        lastDebater = relevantDebaters.filter(
                        teammates__isnull=True,
                        team__isnull=True).order_by('?')

                lastDebater = lastDebater.all()[0]

                lastDebater.team = team
                lastDebater.save()

        # leftOver is an array of single debater for AP + BP, an array of 1 or 2 debaters for CP
        partner_pref = self.session.partner_pref
        if partner_pref == 'NNPP':
            leftOvers = pairUpNNPP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DEBATE',
                    nov_pro='NOV').distinct(),
                [])

            leftOvers = pairUpNNPP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DEBATE',
                    nov_pro='PRO').distinct(),
                leftOvers)

            leftOvers = pairUpNNPP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DJ',
                    nov_pro='NOV').distinct(),
                leftOvers)

            leftOvers = pairUpNNPP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DJ',
                    nov_pro='PRO').distinct(),
                leftOvers)

        elif partner_pref == 'NPNP':
            leftOvers = pairUpNPNP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DEBATE').order_by('?'))

            if leftOvers:
                leftOvers = pairUpNPNP(
                    relevantDebaters.filter(
                        teammates__isnull=True,
                        team__isnull=True).order_by('debate_judge_spectate'))
            else:
                leftOvers = pairUpNPNP(
                    relevantDebaters.filter(
                        team__isnull=True,
                        teammates__isnull=True).order_by('?'))

        elif partner_pref == 'RAND':
            leftOvers = pairUpNNPP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DEBATE').distinct(),
                None)

            leftOvers = pairUpNNPP(
                relevantDebaters.filter(
                    teammates__isnull=True,
                    team__isnull=True,
                    debate_judge_spectate='DJ').distinct(),
                leftOvers)


    def pairUp2(self):
        def sortDebatePriority(debater):
            if debater.debate_judge_spectate == "DEBATE":
                if debater.nov_pro == "NOV":
                    return 9000
                else:
                    return 8000
            else:
                if debater.nov_pro == "NOV":
                    return 7000
                else:
                    return 6000

        debaters = filter(lambda debater: debater.debate_judge_spectate in ["DEBATE", "DJ"]
            and not debater.team, self.debaters)

        noOfDebatersToLose = len(debaters) % 8

        sortedDebaters = sorted(debaters, key=sortDebatePriority)

        if noOfDebatersToLose <= 0:
            debatingDebaters = sortedDebaters[:]
        else:
            debatingDebaters = sortedDebaters[:-noOfDebatersToLose]

        self.noOfRooms = len(debatingDebaters) / 8

        # Pair up all with teammates
        for debater in debatingDebaters:
            if debater.team:
                continue

            teammates = list(debater.teammates.all())
            if teammates and teammates[0] in debatingDebaters:
                team = Team.objects.create(
                    session=self.session,
                    debate_judge_spectate="DEBATE")

                self.createdTeams.append(team)

                debater.team = team
                debater.save()

                teammate = debatingDebaters[debatingDebaters.index(teammates[0])]
                teammate.team = team
                teammate.save()


        def sortByNovPro(debater):
            if debater.nov_pro == "NOV":
                return 9000
            else:
                return 8000

        debatingDebaters = sorted(debatingDebaters, key=sortByNovPro)

        partner_pref = self.session.partner_pref
        if partner_pref == "NNPP":
            for i in range(0, debatingDebaters):
                debater = debatingDebaters[i]
                if debater.team:
                    continue
                team = Team.objects.create(
                    session=self.session,
                    debate_judge_spectate="DEBATE")

                self.createdTeams.append(team)

                debater.team = team
                debater.save()

                if i == len(debatingDebaters) - 1:
                    continue

                debatingDebaters[i + 1].team = team
                debatingDebaters[i + 1].save()

        else:
            startIndex = 0
            endIndex = len(debatingDebaters) - 1

            while (endIndex - startIndex) >= 1:
                while startIndex < len(debatingDebaters) and debatingDebaters[startIndex].team:
                    startIndex = startIndex + 1

                while endIndex >= 0 and debatingDebaters[endIndex].team:
                    endIndex = endIndex - 1

                if endIndex > startIndex:
                    firstDebater = debatingDebaters[startIndex]
                    secondDebater = debatingDebaters[endIndex]

                    team = Team.objects.create(
                        session=self.session,
                        debate_judge_spectate="DEBATE")

                    self.createdTeams.append(team)

                    firstDebater.team = team
                    firstDebater.save()
                    secondDebater.team = team
                    secondDebater.save()




    def assign2TeamRooms(self):
        # Assign assigned rooms first
        halfRoomList = []
        usedRoomIDList = []

        # Get a list of rooms where there is only 1 assigned team
        for t in self.session.teams.filter(room__isnull=False):
            if not t.room in map(lambda tup: tup[0], halfRoomList):
                halfRoomList.append((t.room, t.position))
                usedRoomIDList.append(t.room.id)
                self.debatingRoomCount-=1
            else:
                for tup in halfRoomList:
                    if tup[0] == t.room:
                        halfRoomList.remove(tup)

        # Fill the assigned rooms with teams that are not specifically assigned
        teamsNoRoom = self.session.teams.filter(room__isnull=True)
        if halfRoomList:
            for t in teamsNoRoom.order_by('team_members__debate_judge_spectate'):
                if halfRoomList:
                    roomPosTuple = halfRoomList.pop()
                    if roomPosTuple[1] == t.team_members.all()[0].position:
                        halfRoomList.append(roomPosTuple)
                    else:
                        t.room = roomPosTuple[0]
                        t.position = t.team_members.all()[0].position
                        t.save()
                else:
                    break

        if halfRoomList:
            for t in teamsNoRoom.order_by('team_members__debate_judge_spectate'):
                if halfRoomList:
                    roomPosTuple = halfRoomList.pop()

                    t.room = roomPosTuple[0]
                    if roomPosTuple[1] == 'GV':
                        t.position = 'OP'
                    else:
                        t.position = 'GV'
                    t.save()
                else:
                    break


        # Start assigning non-assigned debaters
        # First, get the appropriate rooms.
        if self.roomGroupList:
            roomQuery = Room.objects.filter(group__in=self.roomGroupList, owner=self.session.owner
                ).exclude(id__in=usedRoomIDList)
        else:
            roomQuery = Room.objects.filter(owner=self.session.owner
                ).exclude(id__in=usedRoomIDList)

        for t in teamsNoRoom:
            t.position = t.team_members.all()[0].position

        gvTeams = teamsNoRoom.filter(position='GV')
        opTeams = teamsNoRoom.filter(position='OP')

        gvTeams = list(gvTeams)
        opTeams = list(opTeams)
        iterateAmt = min(len(gvTeams), len(opTeams))

        roomList = list(roomQuery)
        roomIndex = 0

        for i in range(0, iterateAmt):
            if (i < len(roomList)) and self.debatingRoomCount:
                gvTeams[i].room = roomList[i]
                opTeams[i].room = roomList[i]

                gvTeams[i].save()
                opTeams[i].save()
                self.debatingRoomCount-=1
                # roomIndex = where should the room's index start, when assigning remaining teams.
                roomIndex = i + 1

            # If there are not enough rooms
            elif self.debatingRoomCount:
                rm = Room.objects.create(
                    location='Automated Room',
                    owner=self.session.owner)
                gvTeams[i].room = rm
                opTeams[i].room = rm

                gvTeams[i].save()
                opTeams[i].save()
                self.debatingRoomCount-=1


        teamsNoRoom = self.session.teams.filter(room__isnull=True)
        if teamsNoRoom and self.debatingRoomCount:
            teamsNoRoomList = list(teamsNoRoom)
            skip = False

            for i in range(0, len(teamsNoRoomList)):
                if skip:
                    skip = False
                elif (i < len(teamsNoRoomList)-1) and self.debatingRoomCount:
                    if roomIndex < len(roomList):
                        teamsNoRoomList[i].room = roomList[roomIndex]
                        teamsNoRoomList[i+1].room = roomList[roomIndex]
                        teamsNoRoomList[i].position = 'GV'
                        teamsNoRoomList[i+1].position = 'OP'
                        teamsNoRoomList[i].save()
                        teamsNoRoomList[i+1].save()
                        self.debatingRoomCount-=1
                        roomIndex += 1
                        skip = True
                    else:
                        rm = Room.objects.create(
                            location='Automated Room',
                            owner=self.session.owner)
                        teamsNoRoomList[i].room = rm
                        teamsNoRoomList[i+1].room = rm
                        teamsNoRoomList[i].position = 'GV'
                        teamsNoRoomList[i+1].position = 'OP'
                        teamsNoRoomList[i].save()
                        teamsNoRoomList[i+1].save()
                        self.debatingRoomCount-=1
                        skip = True


        for t in teamsNoRoom:
            if not t.room:
                t.delete()



    def assignBPTeamRooms(self):
        # Assign Teams with assigned rooms. This assumes we already have
        # enough judges.
        processedTeams = []
        usedRoomIDList = []
        for t in self.session.teams.filter(room__isnull=False):
            if t not in processedTeams:
                positionChoices = ['OG', 'OO', 'CG', 'CO']
                random.shuffle(positionChoices)
                tSameRoom = self.session.teams.filter(room=t.room)
                usedRoomIDList.append(t.room.id)

                # Here we are ALWAYS assigning random position to teams in BP.
                for t2 in tSameRoom:
                        t2.position = positionChoices.pop()
                        t2.save()
                        processedTeams.append(t2)

                if len(tSameRoom) < 4:
                    needTeamCount = 4 - len(tSameRoom)

                    addedTeams = self.session.teams.filter(room__isnull=True).order_by(
                        'team_members__debate_judge_spectate')[:needTeamCount]

                    for t3 in addedTeams:
                        t3.room = t.room
                        t3.position = positionChoices.pop()
                        t3.save()
                        processedTeams.append(t3)


        # Assign Teams without assigned rooms. Take care of judge count.
        # First, get the appropriate rooms.
        if self.roomGroupList:
            roomQuery = Room.objects.filter(group__in=self.roomGroupList, owner=self.session.owner
                ).exclude(id__in=usedRoomIDList).distinct()
        else:
            roomQuery = Room.objects.filter(owner=self.session.owner
                ).exclude(id__in=usedRoomIDList).distinct()

        self.debatingRoomCount -= len(usedRoomIDList)
        # print('debatingRoomCount: ' + str(self.debatingRoomCount))

        teamsNoRoom = self.session.teams.filter(room__isnull=True)
        teamsNoRoomList = list(teamsNoRoom)
        # print('teamsnoroom length: ' + str(len(teamsNoRoomList)))
        roomList = list(roomQuery)

        for i in range(0, self.debatingRoomCount):
            positionChoices = ['OG', 'OO', 'CG', 'CO']
            random.shuffle(positionChoices)

            if len(roomList) > 0:
                for j in range(0, 4):
                    t = teamsNoRoomList.pop(0)
                    t.room = roomList[0]
                    t.position = positionChoices.pop()
                    t.save()

                roomList.pop(0)
            else:
                rm = Room.objects.create(
                    location='Automated Room',
                    owner=self.session.owner)
                for j in range(0, 4):
                    t = teamsNoRoomList.pop(0)
                    t.room = rm
                    t.position = positionChoices.pop()
                    t.save()

        for t in teamsNoRoomList:
            if not t.room:
                t.delete()



    def assignBPTeamRooms2(self):
        teamRoomIds = map(lambda team: team.room.id, self.teams)
        rooms = Room.objects.filter(owner=self.session.owner)
        rooms = filter(lambda room: room.id not in teamRoomIds, rooms)

        roomDict = {}
        for team in self.teams:
            if not team.room in roomDict:
                roomDict[team.room] = [team]
            else:
                roomDict[team.room].append(team)

        while len(roomDict) < self.noOfRooms:
            if len(rooms) > 0:
                room = rooms.pop()
            else:
                room = Room.objects.create(
                    location='Automated Room',
                    owner=self.session.owner)

            roomDict[room] = []

        for room, teams in roomDict.iteritems():
            positions = ["OG", "OO", "CG", "CO"]
            random.shuffle(positions)

            for team in teams:
                team.position = positions.pop()
                # We should already have the room here...
                team.room = room
                team.save()

            while len(positions) > 0:
                team = self.createdTeams.pop()
                team.room = room
                team.position = positions.pop()
                team.save()

    def assignJudges(self):
        # Assign 1 pro judge per room first
        usedRoom = Room.objects.filter(teams__in=self.session.teams.all()).distinct()

        if not usedRoom: return

        proJudges = list(Debater.objects.filter(
            session=self.session,
            nov_pro='PRO',
            team__isnull=True
            ).exclude(debate_judge_spectate='SPEC').distinct())

        # Can be refactored to a method, with below loop.
        for i in range(0, len(proJudges)):
            team = Team.objects.create(
                session=self.session,
                room=usedRoom[i % len(usedRoom)],
                position='JUDGE',
                debate_judge_spectate='JUDGE')
            if not team:
                        raise Error("yo")
            proJudges[i].team = team
            proJudges[i].save()

        # Assign the rest of the non-debating debaters to judge.
        restJudges = list(Debater.objects.filter(
            session=self.session,
            team__isnull=True
            ).exclude(debate_judge_spectate='SPEC').distinct())

        # Room index starts from where pro judges stopped.
        for i in range(0, len(restJudges)):
            team = Team.objects.create(
                session=self.session,
                room=usedRoom[(len(proJudges) + i) % len(usedRoom)],
                position='JUDGE',
                debate_judge_spectate='JUDGE')
            if not team:
                        raise Error("yo")
            restJudges[i].team = team
            restJudges[i].save()

    def declashifyAP(self):
        def checkAPInvariant(relevantDebaters, relevantDebatersCount):
            if (relevantDebatersCount < (6*self.requiredProJudges) or
                    self.session.debaters.exclude(debate_judge_spectate='SPEC').count() < (7*self.requiredProJudges)):
                return Response('Not enough debaters for the assigned rooms.', status=404)

            # We are now making the assumption that only Pro debaters can judge
            elif self.session.debaters.exclude(team__isnull=False
                    ).filter(nov_pro='PRO').count() < self.requiredProJudges:
                return Response('Need more pro judges.', status=404)
            elif relevantDebatersCount < 6 or self.session.debaters.exclude(debate_judge_spectate='SPEC').count() < 7:
                return Response('Not enough debaters to form a room.', status=404)

        relevantDebaters = self.session.debaters.exclude(
            debate_judge_spectate='JUDGE'
            ).exclude(debate_judge_spectate='SPEC')
        relevantDebatersCount = relevantDebaters.count()

        returnResponse = checkAPInvariant(relevantDebaters, relevantDebatersCount)
        if returnResponse: return returnResponse

        self.checkAndSwitchJudge(relevantDebaters, 6)

        self.pairUp(relevantDebaters)
        self.assign2TeamRooms()
        self.assignJudges()

        serializer = SessionSerializer(self.session)
        return Response(serializer.data)


    def declashifyBP(self):
        def checkBPInvariant(relevantDebatersCount):
            if (relevantDebatersCount < (8*self.requiredProJudges)
                    or self.session.debaters.exclude(debate_judge_spectate='SPEC').count() < (9*self.requiredProJudges)):
                return Response('Not enough debaters for the assigned rooms.', status=404)
            elif self.session.debaters.exclude(team__isnull=False
                    ).filter(nov_pro='PRO').count() < self.requiredProJudges:
                return Response('Need more pro judges.', status=404)
            elif relevantDebatersCount < 8 or self.session.debaters.exclude(debate_judge_spectate='SPEC').count() < 9:
                return Response('Not enough debaters to form a room.', status=404)




        relevantDebaters = self.session.debaters.exclude(
            debate_judge_spectate='JUDGE'
            ).exclude(debate_judge_spectate='SPEC')
        relevantDebatersCount = relevantDebaters.count()

        returnResponse = checkBPInvariant(relevantDebatersCount)
        if returnResponse: return returnResponse

        # self.checkAndSwitchJudge(relevantDebaters, 8)
        # self.pairUp(relevantDebaters)
        # self.assignBPTeamRooms()

        self.checkAndSwitchJudge2()
        self.pairUp2()
        self.assignBPTeamRooms2()

        self.assignJudges()

        serializer = SessionSerializer(self.session)
        return Response(serializer.data)

    def declashifyCP(self):
        def checkCPInvariant(relevantDebaters, relevantDebatersCount):
            if (relevantDebatersCount < (4*self.requiredProJudges) or
                    self.session.debaters.exclude(debate_judge_spectate='SPEC').count() < (5*self.requiredProJudges)):
                return Response('Not enough debaters for the assigned rooms.', status=404)

            # We are now making the assumption that only Pro debaters can judge
            elif self.session.debaters.exclude(team__isnull=False
                    ).filter(nov_pro='PRO').count() < self.requiredProJudges:
                return Response('Need more pro judges.', status=404)
            elif relevantDebatersCount < 4 or self.session.debaters.exclude(debate_judge_spectate='SPEC').count() < 5:
                return Response('Not enough debaters to form a room.', status=404)

        relevantDebaters = self.session.debaters.exclude(
            debate_judge_spectate='JUDGE'
            ).exclude(debate_judge_spectate='SPEC')
        relevantDebatersCount = relevantDebaters.count()

        returnResponse = checkCPInvariant(relevantDebaters, relevantDebatersCount)
        if returnResponse: return returnResponse

        self.checkAndSwitchJudge(relevantDebaters, 4)

        # Now start to put debaters into teams, start by pairing up teammates
        self.pairUp(relevantDebaters)
        self.assign2TeamRooms()
        self.assignJudges()

        serializer = SessionSerializer(self.session)
        return Response(serializer.data)
