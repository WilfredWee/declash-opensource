'use strict';

/* Filters */
var declashFilters = angular.module('declashFilters', []);

declashFilters.filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }]);
