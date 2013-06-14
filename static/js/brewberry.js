'use strict';

angular.module('brewberry', ['brewberry.directive', 'brewberry.service'])
    .controller('Logger', function ($scope, $http, feed) {
        var since = new Date (Date.now() - 2*60*60*1000).toISOString();
        $http.get('/logger/history', {
            params: { 'since': since}
        }).success(function(data, status) {
            //provide data to charts
            console.log(data);
//            data.forEach(function (e) {
//                $scope.sample = e;
//                $scope.$apply();
//            });
            // Hook up feed:
            var id = feed(function (sample) {
                if (sample) {
                    $scope.sample = sample;
                    $scope.$apply();
                }
            });
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
