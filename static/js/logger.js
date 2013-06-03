//
// TODO: Convert into a Controller.
//
Logger = function (callback) {
    var client = null;
    setInterval((function () {
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
                        try {
                            var sample = JSON.parse(text.substring(offset));
                            console.log(sample);
                            callback(sample);
                        } catch (e) {
                            console.log('parse error', e, 'text is:', text);
                        }
                        offset = text.length;
                    }
                }
                client.send();
                console.log('new client', client);
            }
        }
    })(), 2000);
};

