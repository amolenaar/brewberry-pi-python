'use strict';

angular.module('brewberry', ['brewberry.directive', 'brewberry.service'])
    .controller('Logger', function ($scope, feed) {
        var id = feed(function (sample) {
            if (sample) {
                $scope.sample = sample;
                $scope.$apply();
            }
        });

    })

    .controller('Controls', function ($scope, $http) {
        $scope.setHeater = function (power) {
            $http.post('/heater', { 'set': power });
        }

        $scope.showTemperatureDialog = false;

        $scope.cancelDialog = function () {
            $scope.showTemperatureDialog = false;
        }
        $scope.setTemperature = function (t) {
            $http.post('/temperature', { 'set': t });
            $scope.showTemperatureDialog = false;
        }
    });
// vim:sw=4:et:ai
