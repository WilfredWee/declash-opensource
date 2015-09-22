'use strict';

/* Controllers */

var declashControllers = angular.module('declashControllers', [])


declashControllers.controller('AppController', ['$scope', '$rootScope', '$location', 'GlobalService',
    function($scope, $rootScope, $location, GlobalService) {
        var failureCb = function (status) {
            console.log(status);
        };
        $rootScope.globals = GlobalService;

        $scope.initialize = function (is_authenticated) {
            if(is_authenticated == 'False') {
                $rootScope.globals.is_authenticated = false;
            }
            else {
                $rootScope.globals.is_authenticated = true;
            }
        };
    }
]);


declashControllers.controller('SessionListCtrl', ['$scope', '$interval','Restangular', '$modal',
    function($scope, $interval, Restangular, $modal) {

        var getSessions = function() {
            Restangular.all('sessions').getList().then(function (sessions) {
                $scope.sessions = sessions;
                if(!$scope.$$phase) {
                    $scope.$apply();
                }
            })
        }
        getSessions();

        // $interval(getSessions, 30000);

        $scope.openForm = function(session) {
            var modalInstance = $modal.open({
                templateUrl: "sessionreg2.html",
                controller: 'DebaterRegCtrl',
                resolve: {
                    sessionObj: function() {
                        return session;
                    }
                }
            });

            modalInstance.result.then(function() {
                getSessions();
            })
        };


}]);

declashControllers.controller('DebaterRegCtrl', ['$scope', '$modalInstance', 'Restangular','sessionObj',
    function($scope, $modalInstance, Restangular, sessionObj) {
        $scope.session = sessionObj;
        $scope.errorMessage = "";
        $scope.debatername = "";
        $scope.teammate = {};
        $scope.teammate2 = {};
        $scope.viableTeammates = [];
        $scope.novpro = 'NOV';
        $scope.djs = 'DEBATE';
        $scope.positionpref = 'OP';
        $scope.customrequest = "";

        for(var i=0; i<sessionObj.debaters.length; i++) {
            if (sessionObj.debaters[i].teammates.length < 1 && sessionObj.debaters[i].team == null) {
                $scope.viableTeammates.push(sessionObj.debaters[i]);
            }
        }


        // $scope.viableTeammates = viableTeammates();

        $scope.Submit = function() {
            var teammatesArray = function() {
                if($scope.teammate.id) {
                    if($scope.teammate2.id) {
                        return [$scope.teammate.id, $scope.teammate2.id]
                    }
                    return [$scope.teammate.id];
                }
                return [];
            }

            var master = {
                'name': this.debatername,
                'teammates': teammatesArray(),
                'team': null,
                'nov_pro': this.novpro,
                'debate_judge_spectate': this.djs,
                'session': $scope.session.id,
                'position': this.positionpref,
                'custom_requests': this.customrequest
            };

            Restangular.all('debaters/').post(master).then(function() {
                $modalInstance.close();
            }, function(response) {
                $scope.errorMessage = response.data;
                // console.log(response.data)
            });
        };

        $scope.Cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.addTeammate = function(debaterTeammate, index) {
            if(index == 0) {
                $scope.teammate = debaterTeammate;
            }
            else {
                $scope.teammate2 = debaterTeammate;
            }

        }

        $scope.teammateFilter = function(debater) {
            return debater != $scope.teammate;
        }

}]);



declashControllers.controller('ManagementCtrl', ['$scope', '$route','Restangular', '$modal',
    function($scope, $route, Restangular, $modal) {
        $scope.isCollapsed = false;

        var pushAlerts = function(response) {
            if (response.data instanceof Array){
                for(var i=0, len=response.data.length; i<len; i++) {
                    $scope.alerts.push(response.data[i]);
                }
            }
            else {
                $scope.alerts.push(response.data)
            }
        }

        var getRooms = function () {
            Restangular.all('rooms').getList().then(function(rooms) {
            $scope.rooms = rooms;
            if(!$scope.$$phase) {
                    $scope.$apply();
                }
            });
        };

        var getSession = function () {
            Restangular.all('sessions').getList().then(function(sessions) {
                //This is assuming logged in user can only view his/her own session AND
                //a user can only have one session unfinalized at a time.
                $scope.alerts = [];
                $scope.session = sessions[0];
                $scope.tableDebaters = getTableDebaters(sessions[0]);
                $scope.tableTeams = getTableTeams(sessions[0], sessions[0].debaters)


            }, function(response) {
                pushAlerts(response);
            });
        };

        var getTableDebaters = function(session) {
            var debaters = [];
            var sessionDebaters = JSON.parse(JSON.stringify(session.debaters));
            for(var i=0; i<sessionDebaters.length; i++) {
                var mateLength = sessionDebaters[i].teammates.length;
                if(mateLength < 1) {
                    debaters.push(sessionDebaters[i]);
                }
                else {
                    var pluckedMates = _.remove(sessionDebaters,
                        function(d) {
                            for(var j=0; j<mateLength; j++) {
                                if(d.id === sessionDebaters[i].teammates[j]) {
                                    return true;
                                }
                            }
                            return false;
                        });

                    sessionDebaters[i].teammates = pluckedMates;
                    debaters.push(sessionDebaters[i]);
                }
            }
            return debaters;
        };

        var getTableTeams = function(session, debaters) {
            var sessionTeams = session.teams;
            var sessionDebaters = debaters;
            for(var i=0, len=sessionTeams.length; i<len; i++) {
                for(var j=0, len2=sessionTeams[i].team_members.length; j<len2; j++) {
                    sessionTeams[i].team_members[j] = _.find(
                        sessionDebaters, function(d) {return d.id == sessionTeams[i].team_members[j]});
                }
                sessionTeams[i].room = _.find($scope.rooms, function(r) {return r.id == sessionTeams[i].room});
            }
            return sessionTeams;
        };

        getRooms();
        getSession();

        $scope.createSession = function() {
            var modalInstance = $modal.open({
                templateUrl: "sessioncreate.html",
                controller: 'SessionCreateCtrl',
            });

            modalInstance.result.then(function(session) {
                $scope.session = session;
            });
        };

        $scope.toggleReg = function(open) {
            var putSession = Restangular.copy($scope.session)
            // putSession.openForReg = open;
            putSession.patch({'openForReg': open}).then(function (session) {
                $scope.session.openForReg = session.openForReg;
            }, function(response) {
                pushAlerts(response);
            });
        };

        $scope.deClashify = function() {
            console.log('boom');
            Restangular.one('sessions', $scope.session.id).get({'declashify': true}).then(function(session) {
                getSession();
                getRooms();
            }, function(response) {
                pushAlerts(response);
                console.log(response);
            });
        };

        $scope.togglePublish = function(publish) {
            var putSession = Restangular.copy($scope.session)

            putSession.patch({'published': publish}).then(function(session) {
                $scope.session.published = session.published;
            }, function(response) {
                pushAlerts(response);
                console.log('response data' + response.data);
            });
        };

        $scope.teamNullDebaters = function(debater) {
            return debater.team == null;
        };

        $scope.addRoom = function(room) {
            if(room.location.length<1) {
                return;
            }

            if (!room.group) {
                room.group = 0;
            }

            Restangular.all('rooms/').post(room).then(function(room) {
                $scope.rooms.push(room);
            }, function(response) {
                pushAlerts(response);
                console.log(response.data);
            });
        };

        $scope.deleteRoom = function(room) {
            Restangular.one('rooms', room.id).remove().then(function() {
                $scope.rooms = _.reject($scope.rooms, function(rm) {return rm == room});
                getSession();
            }, function(response) {
                pushAlerts(response);
                console.log(reponse.data);
            });
        };

        $scope.createTeam = function() {
            var modalInstance = $modal.open({
                templateUrl: "teamcreate.html",
                controller: 'TeamCreateCtrl',
                resolve: {
                    session: function() {
                        getSession()
                        return $scope.session
                    },
                    rooms: function() {
                        return $scope.rooms
                    }
                }

            });
            modalInstance.result.then(function(team) {
                getSession();
            });
        };

        $scope.deleteDebater = function(debater) {
            Restangular.one('debaters', debater.id).remove().then(function(deletedDebater) {
                getSession();
            }, function(response) {
                pushAlerts(response);
            })
        }

        $scope.patchDebater = function(debater, elem, data) {
            var patchObj = {};
            patchObj[elem] = data;
            Restangular.one('debaters', debater.id).patch(patchObj).then(function(debater) {
                getSession();
            }, function(response) {
                pushAlerts(response);
                console.log(response);
            })
        }

        $scope.deleteTeam = function(team) {
            Restangular.one('teams', team.id).remove().then(function(deletedTeam) {
                getSession();
            });
        };

        $scope.finalize = function() {
            var modalInstance = $modal.open({
                templateUrl: "finalize.html",
                controller: 'FinalizeCtrl',
                resolve: {
                    sessionID: function() {
                        getSession()
                        return $scope.session.id
                    }
                }

            });
            modalInstance.result.then(function() {
                getSession();
            });

        }

        $scope.createDiffStyleForMessage = function(debater) {
            if(debater && debater.custom_requests) {
                return {color: "red"};
            }
            else {
                return {color: "black"};
            }
        }
  }]);

declashControllers.controller('SessionCreateCtrl', ['$scope', '$modalInstance', 'Restangular',
    function($scope, $modalInstance, Restangular) {
        $scope.master = {};

        $scope.submit = function(session) {
            $scope.master = angular.copy(session);
            $scope.master.openForReg = true;

            // console.log($scope.master)

            Restangular.all('sessions/').post($scope.master).then(function(addedSession) {
                Restangular.one('sessions', addedSession.id).get().then(function(session) {
                    $modalInstance.close(session);
                });
            }, function(response) {
            });
        };
        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

}]);

declashControllers.controller('TeamCreateCtrl', ['$scope', '$modalInstance', 'Restangular', 'session', 'rooms',
    function($scope, $modalInstance, Restangular, session, rooms) {
        $scope.errorMessage = "";
        $scope.session = session;
        $scope.rooms = rooms;
        $scope.teamDebaters = [];

        $scope.team = {};
        $scope.team.position = 'GV';
        $scope.team.room = null;

        $scope.nullTeamFilter = function(debater) {
            var cond1 = debater.team == null && !(_.contains($scope.teamDebaters, debater));
            var cond2 = debater.debate_judge_spectate != 'JUDGE' && debater.debate_judge_spectate != 'SPEC';

            return cond1 && cond2;
        };

        $scope.notInUsedRoom = function(room) {
            // for(var i=0;i<session.teams.length;i++) {
            //     if(room.id == session.teams[i].room.id) {
            //         return false;
            //     }
            // }

            var teamCount = _.reduce(
                session.teams,
                function(sum, team) {
                    if(team.room.id == room.id) {
                        sum++;
                    }
                    return sum;
                },
                0
            );

            if(session.format == 'BP') {
                return ((teamCount < 4)? true : false);
            }
            else {
                return ((teamCount < 2)? true : false);
            }
        };

        $scope.addDebater = function(debater, index) {
            $scope.teamDebaters[index] = debater
        };

        $scope.submit = function(team) {
            $scope.master = {};
            $scope.master.session = $scope.session.id;
            $scope.master.team_members = _.map($scope.teamDebaters, function(d) {return d.id});
            $scope.master.room = team.room.id;
            $scope.master.position = team.position;

            Restangular.all('teams/').post($scope.master).then(function(addedTeam) {
                $modalInstance.close(addedTeam);
            }, function(response) {
                $scope.errorMessage = response.data;
                console.log($scope.master);
            });

        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };
}]);


declashControllers.controller('TeamsCtrl', ['$scope', '$routeParams','Restangular',
    function($scope, $routeParams, Restangular, $modal) {
        Restangular.all('teams').getList({'sessionID': $routeParams.sessionID}).then(function(teams) {

            $scope.teams = teams.filter(function(leTeam) {
                return leTeam.session == $routeParams.sessionID;
            });
        });

}]);

declashControllers.controller('FinalizeCtrl', ['$scope', '$modalInstance', 'Restangular', 'sessionID',
    function($scope, $modalInstance, Restangular, sessionID) {

        $scope.confirm = function() {
            Restangular.one('sessions', sessionID).patch({'finalized': true}).then(function () {
                $modalInstance.close();
            });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        }

}]);
