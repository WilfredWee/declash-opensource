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
                    t3.append(processedTeams)


    # Assign Teams without assigned rooms. Take care of judge count.
    # First, get the appropriate rooms.
    if self.roomGroupList:
        roomQuery = Room.objects.filter(group__in=self.roomGroupList, owner=self.session.owner
            ).exclude(id__in=usedRoomIDList)
    else:
        roomQuery = Room.objects.filter(owner=self.session.owner
            ).exclude(id__in=usedRoomIDList)

    self.debatingRoomCount -= len(usedRoomIDList)

    teamsNoRoom = self.session.teams.filter(room__isnull=True).order_by(
        'team_members__debate_judge_spectate')
    teamsNoRoomList = list(teamsNoRoom)
    roomList = list(roomQuery)
    

    for i in range(0, self.debatingRoomCount):
        positionChoices = ['OG', 'OO', 'CG', 'CO']
        random.shuffle(positionChoices)

        if roomList:
            for j in range(0, 4):
                t = teamsNoRoomList.pop(0)
                t.room = roomList.pop(0)
                t.position = positionChoices.pop()
                t.save()
        else:
            rm = Room.objects.create(
                location='Automated Room',
                owner=self.sesson.owner)
            for j in range(0, 4):
                t = teamsNoRoomList.pop()
                t.room = rm
                t.position = positionChoices.pop()
                t.save()

    for t in teamsNoRoomList:
        if not t.room:
            t.delete()












