'use strict';

/* Services */

var declashServices = angular.module('declashServices', []);

declashServices.factory('GlobalService', [
	function () {
	    var vars = {
	        is_authenticated: false
	    }
		return vars;
}]);

// declashServices.factory('SessionService', ['Restangular',
// 	function(Restangular) {
// 		return Restangular.all('sessions').getList().$object;
// }]);
