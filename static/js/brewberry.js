'use strict';

angular.module('brewberry', ['brewberry.directive', 'brewberry.service'])
    .controller('Logger', function ($scope, $http, feed) {
        function normalizeSample(sample) {
            sample.time = Date.parse(sample.time);
            sample.heater = sample.heater ? 1 : 0;
            return sample;
        }

        var since = new Date (Date.now() - 3600*1000).toISOString();
        console.log('Fetching data since', since);
        $.get('/logger/history',
            { 'since': since },
            function(data, status) {
                //provide data to charts
                data = $.map(data, normalizeSample);
                $scope.chartData = $.makeArray(data);
                $scope.$digest();
                // Hook up feed:
                function callback(sample) {
                    if (sample) {
                        normalizeSample(sample);
                        console.log('New sample', sample);
                        $scope.sample = sample;
                        $scope.$digest();
                    }
                    $.get('/logger/feed', callback);
                };
                callback();
            }, 'json');
    })

    .controller('Controls', function ($scope, $http) {
        $scope.setHeater = function (power) {
            $.post('/controller', { 'set': power });
        }

        $scope.showTemperatureDialog = false;

        $scope.cancelDialog = function () {
            $scope.showTemperatureDialog = false;
        }
        $scope.setTemperature = function (t) {
            $.post('/temperature', { 'set': t });
            $scope.showTemperatureDialog = false;
        }
    });
// vim:sw=4:et:ai
