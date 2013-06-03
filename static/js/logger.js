'use strict';

function Logger ($scope, $rootScope) {

    // Move this out to a service
    var longPoller = function (callback) {
        var client = null;
        return setInterval((function () {
            var offset = 0;
            return function () {
                if (client == null || client.readyState === 4 || client.responseText.length > 4096) {
                    if (client) client.abort();
                    console.log('Set up new client', client);
                    client = new XMLHttpRequest();
                    client.open("GET", "logger", true);
                    client.onreadystatechange = function() {
                        console.log('state:', this.readyState);
                        if (this.readyState === 3) {
                            var text = this.responseText;
                            var sample;
                            try {
                                sample = JSON.parse(text.substring(offset));
                            } catch (e) {
                                console.log('parse error', e, 'text is:', text);
                            }
                            offset = text.length;
                            try {
                                callback(sample);
                            } catch (e) {
                                console.log('callback error', e, 'sample is:', sample);
                            }
                        }
                    }
                    client.send();
                    console.log('new client', client);
                }
            }
        })(), 2000);
    };


    var id = longPoller(function (sample) {
        if (sample) {
            console.log('sample', sample, $scope);
            $scope.sample = sample;
            $scope.$apply();
        }
    });

}

