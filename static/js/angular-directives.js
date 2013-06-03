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
                        backgroundColor: 'transparent',
                        animation: Highcharts.svg // don't animate in old IE
                    },

                    title: {
                        text: ''
                    },
                    credits: {
                        enabled: false
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
                        },
                        opposite: true
                    }, {
                        gridLineWidth: 0,
                        title: {
                            text: '',
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
                        //opposite: true
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
    })
    .directive('logGauge', function() {
        return {
            restrict: 'E',
            template: '<div class="log-gauge"></div>',
            transclude:true,
            replace: true,

            link: function (scope, element, attrs) {

                var chart = new Highcharts.Chart({
                    
                    chart: {
                        type: 'gauge',
                        renderTo: element[0],
                        backgroundColor: 'transparent',
                        plotBackgroundColor: null,
                        plotBackgroundImage: null,
                        plotBorderWidth: 0,
                        plotShadow: false
                    },
                    
                    title: {
                        enabled: false,
                        //text: 'Thermometer'
                        text: ''
                    },
                    credits: {
                        enabled: false
                    },
                    pane: {
                        startAngle: -150,
                        endAngle: 150,
                        background: [{
                            backgroundColor: {
                                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                                stops: [
                                    [0, '#FFF'],
                                    [1, '#333']
                                ]
                            },
                            borderWidth: 0,
                            outerRadius: '109%'
                        }, {
                            backgroundColor: {
                                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                                stops: [
                                    [0, '#333'],
                                    [1, '#FFF']
                                ]
                            },
                            borderWidth: 1,
                            outerRadius: '107%'
                        }, {
                            // default background
                        }, {
                            backgroundColor: '#DDD',
                            borderWidth: 0,
                            outerRadius: '105%',
                            innerRadius: '103%'
                        }]
                    },
                       
                    // the value axis
                    yAxis: {
                        min: 20,
                        max: 100,
                        
                        minorTickInterval: 'auto',
                        minorTickWidth: 1,
                        minorTickLength: 10,
                        minorTickPosition: 'inside',
                        minorTickColor: '#666',
                        offset: 1,
                
                        tickPixelInterval: 30,
                        tickWidth: 2,
                        tickPosition: 'inside',
                        tickLength: 10,
                        tickColor: '#666',
                        labels: {
                            step: 2,
                            rotation: 'auto',
                            style: {
                                fontSize: 'smaller'
                            }
                        },
                        title: {
                            text: '°C'
                        },
                        plotBands: [{
                            from: 20,
                            to: 50,
                            color: '#0000BF' // blue
                        }, {
                            from: 50,
                            to: 80,
                            color: '#DDDF0D' // yellow
                        }, {
                            from: 80,
                            to: 100,
                            color: '#DF5353' // red
                        }]        
                    },
                
                    series: [{
                        name: 'Temperature',
                        data: [20],
                        tooltip: {
                            valueSuffix: '°C'
                        },
                        dataLabels: {
                            formatter: function () {
                                return this.y.toFixed(2); 
                            }
                        }
                    }]
                
                });
                scope.$watch("sample", function(sample) {
                    if (sample) {
                        console.log('gauge', sample);
                        var point = chart.series[0].points[0];
                        point.update(sample.temperature);
                    }
                });
            }
        }
    });

// vim:sw=4:et:ai
