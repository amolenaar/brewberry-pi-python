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

var HISTORY_DEPTH = 2 * 3600 * 1000; // 2 hours of history

$(function () {
    var chart = $('#chart').highcharts({
        chart: {
            zoomType: 'xy',
            type: 'spline',
            animation: Highcharts.svg, // don't animate in old IE
            marginRight: 10,
            events: {
                load: function() {
                    // set up the updating of the chart each second
                    var self = this;
                    var temperature_series;
                    var heater_series;
                    function dropOldData(series, ts) {
                        if (series.data.length < 1) return;
                        while (series.data[0].x < ts - HISTORY_DEPTH) {
                            series.data[0].remove(false);
                        }
                        self.redraw();
                    }
                    temperature_series = self.addSeries({
                        name: 'Temperature',
                        color: '#89A54E',
                        tooltip: {
                            valueSuffix: ' °C'
                        },
                        data: []
                    });
                    heater_series = self.addSeries({
                        name: 'Heater',
                        color: '#4572A7',
                        yAxis: 1,
                        data: []
                    });

                    Logger(function (sample) {
                        var time = Date.parse(sample.time);
                        temperature_series.addPoint([time, sample.temperature], true, false);
                        heater_series.addPoint([time, sample.heater ? 1 : 0], true, false);
                        dropOldData(temperature_series, time);
                        dropOldData(heater_series, time);
                    });
                }
            }
        },

        title: {
            text: 'Mash'
        },
        legend: {
            enabled: false
        },
        xAxis: [{
            type: 'datetime',
            title: {
                text: 'Time',
            },
        }],
        yAxis: [{
            labels: {
                style: {
                    color: '#89A54E'
                }
            },
            title: {
                text: 'Temperature',
                style: {
                    color: '#89A54E'
                }
            }
        }, {
            gridLineWidth: 0,
            title: {
                text: 'Heater',
                style: {
                    color: '#A74572'
                },
            },
            labels: {
                enabled: false,
                formatter: function() {
                    return this.value === 0 ? 'Off' : (this.value === 1 ? 'On' : '');
                },
                style: {
                    color: '#A74572'
                },
            },
            min: 0,
            max: 1,
            //tickInterval: 1,
            opposite: true
        }],
        tooltip: {
            shared: true
        },
        plotOptions: {
            series: {
                stacking: null,
                marker: {
                    enabled: false
                }
            }
        }
            /*
            , series: [{
                name: 'Temperature',
                color: '#89A54E',
                tooltip: {
                    valueSuffix: ' °C'
                },
               data: [[0, 1], [3,5]]
            }, {
                name: 'Heater',
                color: '#4572A7',
                yAxis: 1,
               data: []
            }]
            */
    });
});
// vim:sw=4:et:ai
