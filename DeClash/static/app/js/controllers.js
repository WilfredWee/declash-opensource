"use strict";var declashControllers=angular.module("declashControllers",[]);declashControllers.controller("AppController",["$scope","$rootScope","$location","GlobalService",function(e,t,n,r){var i=function(e){console.log(e)};t.globals=r;e.initialize=function(e){if(e=="False"){t.globals.is_authenticated=false}else{t.globals.is_authenticated=true}}}]);declashControllers.controller("SessionListCtrl",["$scope","$interval","Restangular","$modal",function(e,t,n,r){var i=function(){n.all("sessions").getList().then(function(t){e.sessions=t;if(!e.$$phase){e.$apply()}})};i();e.openForm=function(e){var t=r.open({templateUrl:"sessionreg2.html",controller:"DebaterRegCtrl",resolve:{sessionObj:function(){return e}}});t.result.then(function(){i()})}}]);declashControllers.controller("DebaterRegCtrl",["$scope","$modalInstance","Restangular","sessionObj",function(e,t,n,r){e.session=r;e.errorMessage="";e.debatername="";e.teammate={};e.teammate2={};e.viableTeammates=[];e.novpro="NOV";e.djs="DEBATE";e.positionpref="OP";e.customrequest="";for(var i=0;i<r.debaters.length;i++){if(r.debaters[i].teammates.length<1&&r.debaters[i].team==null){e.viableTeammates.push(r.debaters[i])}}e.Submit=function(){var r=function(){if(e.teammate.id){if(e.teammate2.id){return[e.teammate.id,e.teammate2.id]}return[e.teammate.id]}return[]};var i={name:this.debatername,teammates:r(),team:null,nov_pro:this.novpro,debate_judge_spectate:this.djs,session:e.session.id,position:this.positionpref,custom_requests:this.customrequest};n.all("debaters/").post(i).then(function(){t.close()},function(t){e.errorMessage=t.data})};e.Cancel=function(){t.dismiss("cancel")};e.addTeammate=function(t,n){if(n==0){e.teammate=t}else{e.teammate2=t}};e.teammateFilter=function(t){return t!=e.teammate}}]);declashControllers.controller("ManagementCtrl",["$scope","$route","Restangular","$modal",function(e,t,n,r){e.isCollapsed=false;var i=function(t){if(t.data instanceof Array){for(var n=0,r=t.data.length;n<r;n++){e.alerts.push(t.data[n])}}else{e.alerts.push(t.data)}};var s=function(){n.all("rooms").getList().then(function(t){e.rooms=t;if(!e.$$phase){e.$apply()}})};var o=function(){n.all("sessions").getList().then(function(t){e.alerts=[];e.session=t[0];e.tableDebaters=u(t[0]);e.tableTeams=a(t[0],t[0].debaters)},function(e){i(e)})};var u=function(e){var t=[];var n=JSON.parse(JSON.stringify(e.debaters));for(var r=0;r<n.length;r++){var i=n[r].teammates.length;if(i<1){t.push(n[r])}else{var s=_.remove(n,function(e){for(var t=0;t<i;t++){if(e.id===n[r].teammates[t]){return true}}return false});n[r].teammates=s;t.push(n[r])}}return t};var a=function(t,n){var r=t.teams;var i=n;for(var s=0,o=r.length;s<o;s++){for(var u=0,a=r[s].team_members.length;u<a;u++){r[s].team_members[u]=_.find(i,function(e){return e.id==r[s].team_members[u]})}r[s].room=_.find(e.rooms,function(e){return e.id==r[s].room})}return r};s();o();e.createSession=function(){var t=r.open({templateUrl:"sessioncreate.html",controller:"SessionCreateCtrl"});t.result.then(function(t){e.session=t})};e.toggleReg=function(t){var r=n.copy(e.session);r.patch({openForReg:t}).then(function(t){e.session.openForReg=t.openForReg},function(e){i(e)})};e.deClashify=function(){console.log("boom");n.one("sessions",e.session.id).get({declashify:true}).then(function(e){o();s()},function(e){i(e);console.log(e)})};e.togglePublish=function(t){var r=n.copy(e.session);r.patch({published:t}).then(function(t){e.session.published=t.published},function(e){i(e);console.log("response data"+e.data)})};e.teamNullDebaters=function(e){return e.team==null};e.addRoom=function(t){if(t.location.length<1){return}if(!t.group){t.group=0}n.all("rooms/").post(t).then(function(t){e.rooms.push(t)},function(e){i(e);console.log(e.data)})};e.deleteRoom=function(t){n.one("rooms",t.id).remove().then(function(){e.rooms=_.reject(e.rooms,function(e){return e==t});o()},function(e){i(e);console.log(reponse.data)})};e.createTeam=function(){var t=r.open({templateUrl:"teamcreate.html",controller:"TeamCreateCtrl",resolve:{session:function(){o();return e.session},rooms:function(){return e.rooms}}});t.result.then(function(e){o()})};e.deleteDebater=function(e){n.one("debaters",e.id).remove().then(function(e){o()},function(e){i(e)})};e.patchDebater=function(e,t,r){var s={};s[t]=r;n.one("debaters",e.id).patch(s).then(function(e){o()},function(e){i(e);console.log(e)})};e.deleteTeam=function(e){n.one("teams",e.id).remove().then(function(e){o()})};e.finalize=function(){var t=r.open({templateUrl:"finalize.html",controller:"FinalizeCtrl",resolve:{sessionID:function(){o();return e.session.id}}});t.result.then(function(){o()})};e.createDiffStyleForMessage=function(e){if(e&&e.custom_requests){return{color:"red"}}else{return{color:"black"}}}}]);declashControllers.controller("SessionCreateCtrl",["$scope","$modalInstance","Restangular",function(e,t,n){e.master={};e.submit=function(r){e.master=angular.copy(r);e.master.openForReg=true;n.all("sessions/").post(e.master).then(function(e){n.one("sessions",e.id).get().then(function(e){t.close(e)})},function(e){})};e.cancel=function(){t.dismiss("cancel")}}]);declashControllers.controller("TeamCreateCtrl",["$scope","$modalInstance","Restangular","session","rooms",function(e,t,n,r,i){e.errorMessage="";e.session=r;e.rooms=i;e.teamDebaters=[];e.team={};e.team.position="GV";e.team.room=null;e.nullTeamFilter=function(t){var n=t.team==null&&!_.contains(e.teamDebaters,t);var r=t.debate_judge_spectate!="JUDGE"&&t.debate_judge_spectate!="SPEC";return n&&r};e.notInUsedRoom=function(e){var t=_.reduce(r.teams,function(t,n){if(n.room.id==e.id){t++}return t},0);if(r.format=="BP"){return t<4?true:false}else{return t<2?true:false}};e.addDebater=function(t,n){e.teamDebaters[n]=t};e.submit=function(r){e.master={};e.master.session=e.session.id;e.master.team_members=_.map(e.teamDebaters,function(e){return e.id});e.master.room=r.room.id;e.master.position=r.position;n.all("teams/").post(e.master).then(function(e){t.close(e)},function(t){e.errorMessage=t.data;console.log(e.master)})};e.cancel=function(){t.dismiss("cancel")}}]);declashControllers.controller("TeamsCtrl",["$scope","$routeParams","Restangular",function(e,t,n,r){n.all("teams").getList({sessionID:t.sessionID}).then(function(t){e.teams=t})}]);declashControllers.controller("FinalizeCtrl",["$scope","$modalInstance","Restangular","sessionID",function(e,t,n,r){e.confirm=function(){n.one("sessions",r).patch({finalized:true}).then(function(){t.close()})};e.cancel=function(){t.dismiss("cancel")}}])