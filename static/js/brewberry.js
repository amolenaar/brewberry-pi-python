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
        console.log('sample', sample);
        if (sample) {
            normalizeSample(sample);
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

    this.onSample = function (callback) {
        this.on('sample', callback);
    };
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
        $.ajax('/temperature', {
                data: JSON.stringify({ 'set': t }),
                contentType: 'application/json',
                type: 'POST'
            });
    };
}

// Presenter
$(function () {

    var logger = new Logger(feed),
        controls = new Controls();
    
    /* Chart */
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

    /* Controls */
    var turnOnButton = $('#turn-on'),
        turnOffButton = $('#turn-off'),
        temperatureDialogButton = $('#show-temperature-dialog'),
        temperatureDialog = $('#temperature-dialog'),
        temperatureDialogTemperatureInput = $('#temperature-dialog input[name=temperature]'),
        temperatureDialogSubmitButton = $('#temperature-dialog .submit'),
        temperatureDialogCancelButton = $('#temperature-dialog .cancel');

    logger.onSample(function (sample) {
        turnOnButton.text(sample.controller);
    });

    turnOnButton.click(function () {
        controls.turnOn();
        turnOnButton.text('...');
    });
    turnOffButton.click(function () {
        controls.turnOff();
        turnOnButton.text('...');
    });

    temperatureDialogButton.click(function () {
        temperatureDialog.show();
    });

    temperatureDialogCancelButton.click(function () {
        temperatureDialog.hide();
    });

    temperatureDialogSubmitButton.click(function () {
        var temperature = temperatureDialogTemperatureInput.val();
        if (temperature) {
            controls.setTemperature(parseInt(temperature));
        }
        temperatureDialog.hide();
    });
});
// vim:sw=4:et:ai
