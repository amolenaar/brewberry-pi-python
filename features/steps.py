from lettuce import step, world

from brewgearpi import fakeio, logger

DEFAULT_TEMP = 20.0

@step(u'Given a running system')
def a_running_system(step):
    fakeio.time = 0
    fakeio.temperature = DEFAULT_TEMP
    fakeio.heater = Off
    world.logger = logger.Logger(fakeio)

@step(u'When a line is logged')
def a_line_is_logged(step):
    world.log_line = world.logger()

@step(u'Then it contains information about time, temperature and heater')
def it_contains_information_about_temperature_temperature_heater_and_time(step):
    assert world.log_line.time == 0, 'Time is %s' % world.log_line.time
    assert world.log_line.temperature == DEFAULT_TEMP, 'Temperature is %s' % world.log_line.temperature
    assert world.log_line.heater == Off, 'Heater is %s' % world.log_line.heater

@step(u'And a second line with the same state')
def a_second_line_with_the_same_state(step):
    fakeio.time = 1
    world.logger()

@step(u'And a second line with a temparature T plus 0.05 degrees')
def a_second_line_with_a_temparature_t_plus_d_degrees(step):
    fakeio.tempearure = DEFAULT_TEMP + 0.05
    world.logger()

@step(u'Then only (\d) line is logged')
def only_one_line_is_logged(step, n_lines):
    assert len(world.logger.lines) == int(n_lines), world.logger.lines

