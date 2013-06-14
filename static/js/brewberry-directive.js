'use strict';

angular.module('brewberry.directive', [])
    .directive('logChart', function() {
//        Highcharts.setOptions({
//            // This is for all plots, change Date axis to local timezone
//            global : {
//                useUTC : false
//            }
//        });
        return {
            scope: true,

            link: { 
                pre: function (scope, element, attrs) {
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

                    scope.chart = chart;
                }
            }
        }
    })
    .directive('series', function() {
        return {
            restrict: 'E',
            transclude:true,
            link: function (scope, element, attrs) {
                var HISTORY_DEPTH = 3600 * 1000; // 1 hours of history
                var hostory_depth = attrs.history || HISTORY_DEPTH

                var series = scope.chart.addSeries({
                    name: attrs.name,
                    color: attrs.color,
                    tooltip: {
                        valueSuffix: attrs.valuesuffix
                    },
                    data: []
                });

                function dropOldData(series, ts) {
                    while (series.data.length > 0 && series.data[0].x < ts - HISTORY_DEPTH) {
                        series.data[0].remove(false);
                    }
                    //scope.chart.redraw();
                }

                var x = attrs.x;
                var y = attrs.y;
                scope.$watch("chartData", function (chartData) {
                    if (chartData) {
                        var newData = [];
                        chartData.forEach(function (e) {
                            newData.push([e[x], e[y]]);
                        });
                        series.setData(newData, true);
                    }
                });
                scope.$watch(attrs.sample, function(sample) {
                    if (sample) {
                        dropOldData(series, sample[x]);
                        series.addPoint([sample[x], sample[y]], true, false);
                    }
                });
                console.log('Added series for ', attrs.name );
            }
        }
    })
    .directive('logGauge', function() {
        return {
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
                        tickLength: 1,
                        tickColor: '#666',
                        labels: {
                            step: 2,
                            rotation: 'auto',
                            style: {
                                fontSize: '6px'
                            }
                        },
                        title: {
                            enabled: false,
                            text: ''
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
                        data: [20],
                        tooltip: {
                            enabled: false
                        },
                        dataLabels: {
                            formatter: function () {
                                return this.y.toFixed(2); 
                            }
                        }
                    }]
                
                });
                scope.$watch(attrs.sample, function(sample) {
                    if (sample) {
                        var point = chart.series[0].points[0];
                        point.update(sample[attrs.value]);
                    }
                });
            }
        }
    });

// vim:sw=4:et:ai
