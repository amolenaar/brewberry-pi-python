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
        function setHeater(power) {
            $http.post('/heater', { 'power': true });
        }

        $scope.startHeater = function () {
            setHeater(true);
        };
        $scope.stopHeater = function () {
            setHeater(false);
        };
        $scope.showTemperatureDialog = false;

        $scope.cancelDialog = function () {
            $scope.showTemperatureDialog = false;
        }
        $scope.setTemperature = function (t) {
            $http.post('/temperature', { 'temperature': t });
            $scope.showTemperatureDialog = false;
        }
    });
// vim:sw=4:et:ai
