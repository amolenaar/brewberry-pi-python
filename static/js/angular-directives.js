'use strict';

angular.module('brewberry', [])
    .directive('logChart', function() {
        return {
            restrict: 'E',
            template: '<div class="log-chart"></div>',
            transclude:true,
            replace: true,

            link: function (scope, element, attrs) {
                var HISTORY_DEPTH = 2 * 3600 * 1000; // 2 hours of history

                var chart = new Highcharts.Chart({
                    chart: {
                        renderTo: element[0],
                        zoomType: 'xy',
                        type: 'spline',
                        animation: Highcharts.svg // don't animate in old IE
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
                            text: 'Time'
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
                });

                var temperature_series = chart.addSeries({
                    name: 'Temperature',
                    color: '#89A54E',
                    tooltip: {
                        valueSuffix: ' °C'
                    },
                    data: []
                });
                var heater_series = chart.addSeries({
                    name: 'Heater',
                    color: '#4572A7',
                    yAxis: 1,
                    data: []
                });

                function dropOldData(series, ts) {
                    if (series.data.length < 1) return;
                    while (series.data[0].x < ts - HISTORY_DEPTH) {
                        series.data[0].remove(false);
                    }
                    chart.redraw();
                }

                scope.$watch("sample", function(sample) {
                    if (sample) {
                        var time = Date.parse(sample.time);
                        temperature_series.addPoint([time, sample.temperature], true, false);
                        heater_series.addPoint([time, sample.heater ? 1 : 0], true, false);
                        dropOldData(temperature_series, time);
                        dropOldData(heater_series, time);
                    }
                });
            }
        }
    });
// vim:sw=4:et:ai
