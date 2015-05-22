'use strict';


// Declare app level module which depends on filters, and services


var DeClash = angular.module('DeClash', [
  'ngRoute',
  'restangular',
  'ui.bootstrap',
  'ngCookies',
  'declashFilters',
  'declashServices',
  'declashDirectives',
  'declashControllers' 
]);

DeClash.run(['$http', '$cookies', 
  function ($http, $cookies) {
    $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
}]);

DeClash.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol("{[{");
    $interpolateProvider.endSymbol("}]}");
}]);

DeClash.config(['RestangularProvider', function(RestangularProvider) {
  RestangularProvider.setBaseUrl('/api');
  RestangularProvider.setRequestSuffix('/');
}]);

DeClash.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/', {
    templateUrl: '/static/app/partials/landing.html',
    controller: 'SessionListCtrl'
  });
  $routeProvider.when('/about', {
    templateUrl: '/static/app/partials/about.html'
  });
  $routeProvider.when('/sessions', {
    templateUrl: '/static/app/partials/sessions.html', 
    controller: 'SessionListCtrl'
  });
  $routeProvider.when('/management', {
    templateUrl: '/static/app/partials/management.html',
    controller: 'ManagementCtrl'
  });
  $routeProvider.when('/sessions/:sessionID', {
    templateUrl: '/static/app/partials/publishedsession.html',
    controller: 'TeamsCtrl'
  });
  $routeProvider.otherwise({redirectTo: '/'});

}]);

DeClash.run(['$rootScope', '$location', '$window',
  function($rootScope, $location, $window) {
    $rootScope.$on("$routeChangeStart", function(event, next, current) {
      if(!$rootScope.globals.is_authenticated) {
        if(next.templateUrl == "/static/app/partials/management.html") {
          $window.location.href = '/api-auth/login';
        }
      }         
    });
}]);