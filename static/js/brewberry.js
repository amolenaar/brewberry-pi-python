'use strict';

angular.module('brewberry', ['brewberry.directive', 'brewberry.service'])
    .controller('Logger', function ($scope, $http, feed) {
        var since = new Date (Date.now() - 3600*1000).toISOString();
        console.log('Fetching data since', since);
        $http.get('/logger/history', {
            params: { 'since': since }
        }).success(function(data, status) {
            //provide data to charts
            console.log(data);
            data.forEach(function (e) {
                e.time = Date.parse(e.time);
            });
            $scope.chartData = data;

            // Hook up feed:
            var id = feed(function (sample) {
                if (sample) {
                    sample.time = Date.parse(sample.time);
                    console.log('New sample', sample);
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
