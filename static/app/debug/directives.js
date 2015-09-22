'use strict';

/* Directives */

var declashDirectives = angular.module('declashDirectives', []);

declashDirectives.directive('appVersion', ['version', function(version) {
	return function(scope, elm, attrs) {
      elm.text(version);
    };
  }]);
