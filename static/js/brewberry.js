'use strict';

function Logger(feed) {
    var self = this;

    function normalizeSample(sample) {
        sample.time = Date.parse(sample.time);
        sample.heater = sample.heater ? 1 : 0;
        return sample;
    }

    var since = new Date (Date.now() - 3600*1000).toISOString();
    console.log('Fetching data since', since);
    function callback(sample) {
        if (sample) {
            normalizeSample(sample);
            console.log('New sample', sample);
            self.trigger('sample', sample);
        }
    }

    $.get('/logger/history',
        { 'since': since },
        function(data, status) {
            // Provide data to charts
            data = $.map(data, normalizeSample);
            self.trigger('samples', data);

            feed(callback)
        }, 'json');

    $.observable(self);
}

function Controls() {
    var self = this;

    function setHeater(power) {
        $.ajax('/controller', {
                data: JSON.stringify({ 'set': power }),
                contentType: 'application/json',
                type: 'POST'
            });
    };

    this.turnOn = function () {
        setHeater('on');
    };

    this.turnOff = function () {
        setHeater('off');
    };

    this.setTemperature = function (t) {
        $.post('/temperature', JSON.stringify({ 'set': t }));
    };
}

$(function () {

    var logger = new Logger(feed),
        controls = new Controls();
    
    var chart = logChart($('#log-chart'));
    
    addSeries(chart, logger, {
        'name': 'Heater',
        'type': 'switch',
        'x': 'time',
        'y': 'heater',
        'color': '#DF5353' });
    addSeries(chart, logger, {
        'name': 'Mash temperature',
        'type': 'temperature',
        'x': 'time',
        'y': 'mash-temperature',
        'color': '#DDDF0D' });
    addSeries(chart, logger, {
        'name': 'Temperature',
        'type': 'temperature',
        'x': 'time',
        'y': 'temperature',
        'color': '#0000BF' });

    logger.on('sample', function (sample) {
        $('#turn-on').text(sample.controller);
    });

    $('#turn-on').click(function () {
        controls.turnOn();
        $(this).text('...');
    });
    $('#turn-off').click(function () {
        controls.turnOff();
        $('#turn-on').text('...');
    });
});
// vim:sw=4:et:ai
