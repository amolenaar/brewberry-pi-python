'use strict';

angular.module('brewberry', ['brewberry.directive', 'brewberry.service'])
    .controller('Logger', function ($scope, $http, feed) {
        function normalizeSample(sample) {
            sample.time = Date.parse(sample.time);
            sample.heater = sample.heater ? 1 : 0;
        }

        var since = new Date (Date.now() - 3600*1000).toISOString();
        console.log('Fetching data since', since);
        $http.get('/logger/history', {
            params: { 'since': since }
        }).success(function(data, status) {
            //provide data to charts
            console.log(data);
            data.forEach(normalizeSample);
            $scope.chartData = data;

            // Hook up feed:
            function callback(sample) {
                if (sample) {
                    normalizeSample(sample);
                    console.log('New sample', sample);
                    $scope.sample = sample;
                }
                $http.get('/logger/feed').success(callback)
            };
            callback();
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
