'use strict';

angular.module('brewberry', ['brewberry.directive', 'brewberry.service'])
    .controller('Logger', function ($scope, feed) {


        var id = feed(function (sample) {
            if (sample) {
                console.log('sample', sample, $scope);
                $scope.sample = sample;
                $scope.$apply();
            }
        });

    });

// vim:sw=4:et:ai
