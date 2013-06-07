from lettuce import step, world

from brewberry import fakeio, logger, sampler, controller

DEFAULT_TEMP = 20.0

@step(u'Given a running system')
def a_running_system(step):
    fakeio.time = 0
    fakeio.temperature = DEFAULT_TEMP
    fakeio.heater = Off
    world.log_lines = []
    world.sampler = sampler.Sampler(fakeio)
    world.logger = logger.Logger(world.sampler, world.log_lines.append)

@step(u'When a line is logged')
def a_line_is_logged(step):
    world.log_line = world.sampler()

@step(u'Then it contains information about time, temperature and heater')
def it_contains_information_about_temperature_temperature_heater_and_time(step):
    assert world.log_line.temperature == DEFAULT_TEMP, 'Temperature is %s' % world.log_line.temperature
    assert world.log_line.heater == Off, 'Heater is %s' % world.log_line.heater
    assert str(world.log_line.time) == '1970-01-01 00:00:00', 'Time is %s' % world.log_line.time

@step(u'And a second line with the same state')
def a_second_line_with_the_same_state(step):
    world.sampler()

@step(u'And a second line with a temparature T plus (-?\d+\.\d+) degrees')
def a_second_line_with_a_temparature_t_plus_d_degrees(step, delta_t):
    fakeio.temperature = DEFAULT_TEMP + float(delta_t)
    world.sampler()

@step(u'And a minute expires')
def when_a_minute_expires(step):
    fakeio.time = fakeio.time + 60
    world.sampler()

@step(u'Then (no|one) new line is logged')
def no_one_new_line_is_logged(step, s):
    if s == 'one':
        assert len(world.log_lines) == 2, world.log_lines
    else:
        assert len(world.log_lines) == 1, world.log_lines

@step(u'Given a mash temperature of (\d+) degrees')
def given_a_mash_temperature_of_66_degrees(step, degrees):
    world.controller = controller.Controller(fakeio)
    world.controller.mash_temperature = float(degrees)

@step(u'And the heating is turned (on|off)')
def and_the_heating_is_on_off(step, s):
    fakeio.set_heater(s == 'on')

@step(u'When the fluid is (\d+) degrees')
def when_the_fluid_is_xx_degrees(step, degrees):
    fakeio.temperature = float(degrees)
    world.controller()

@step(u'Then the heating should be turned on')
def then_the_heating_should_be_turned_on(step):
    assert fakeio.read_heater()

@step(u'Then the heating should be turned off')
def then_the_heating_should_be_turned_off(step):
    assert not fakeio.read_heater()

# vim: sw=4:et:ai
