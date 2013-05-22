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
                    var last_reading;
                    function dropOldData(series, ts) {
                        if (series.data.length < 1) return;
                        while (series.data[0].x < ts - HISTORY_DEPTH) {
                            series.data[0].remove(false);
                        }
                        self.redraw();
                    }
                    var callback = function () {
                        $.get("/reading", function (data, textStatus, jqXHR) {
                            if (data !== last_reading) {
                                var d = Date.parse(data.time);
                                temperature_series.addPoint([d, data.temperature], true, false);
                                heater_series.addPoint([d, data.heater], true, false);
                                dropOldData(temperature_series, d);
                                dropOldData(heater_series, d);

                                last_reading = data;
                            }
                            setTimeout(callback, 2000);
                            console.log(data);
                        });
                    };
                    $.get('/readings/all', function (readings) {
                        var temperature_data = [], heater_data = [];
                        var oldest_date = readings ? Date.parse(readings[readings.length - 1].time) - HISTORY_DEPTH : undefined;
                        $.each(readings, function (i, data) {
                            console.log(i, data);
                            var d = Date.parse(data.time);
                            if (oldest_date && d > oldest_date) {
                                temperature_data.push([d, data.temperature]);
                                heater_data.push([d, data.heater]);
                            }
                        });
                        temperature_series = self.addSeries({
                            name: 'Temperature',
                            color: '#89A54E',
                            tooltip: {
                                valueSuffix: ' °C'
                            },
                            data: temperature_data
                        });
                        heater_series = self.addSeries({
                            name: 'Heater',
                            color: '#4572A7',
                            yAxis: 1,
                            data: heater_data
                        });
                        setTimeout(callback, 2000);
                    });
                }
                //*/
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
            type: 'area',
            title: {
                text: 'Heater',
                style: {
                    color: '#4572A7'
                },
            },
            labels: {
                formatter: function() {
                    return this.value === 0 ? 'Off' : (this.value === 1 ? 'On' : '');
                },
                style: {
                    color: '#4572A7'
                },
                tickInterval: 1
            },
            min: 0,
            max: 1,
            opposite: true
        }],
        tooltip: {
            shared: true
        },
        plotOptions: {
            series: {
                stacking: null
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
