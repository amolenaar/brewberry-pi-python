'use strict';

function feed(callback) {
    var client = null;
    return setInterval((function () {
        return function () {
            if (client == null || client.readyState === 4 || client.responseText.length > 4096) {
                var offset = 0;
                if (client) client.abort();
                client = new XMLHttpRequest();
                client.open("GET", "/logger/feed", true);
                client.onreadystatechange = function() {
                    if (this.readyState === 3 || this.readyState === 4) {
                        var text = this.responseText;
                        if (text.length <= offset) return;
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
            }
        }
    })(), 300);
};

// vim: sw=4:et:ai
