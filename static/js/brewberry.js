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

    .controller('Controls', function ($scope) {

        $scope.startHeater = function () {
            console.log('start heating');
        };
        $scope.stopHeater = function () {
            console.log('stop heating');
        };
    });


// vim:sw=4:et:ai
