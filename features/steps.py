from lettuce import step, world

from brewberry import fakeio, logger, sampler, controller
from gevent.queue import Queue

DEFAULT_TEMP = 20.0

@step(u'Given a running system')
def a_running_system(step):
    fakeio.time = 0
    fakeio.temperature = DEFAULT_TEMP
    fakeio.heater = Off
    world.log_lines = []
    world.controller = controller.Controller(fakeio)
    world.logger = logger.Logger(world.log_lines.append)

    def _sampler():
        sample_queue = Queue()
        sampler.Sampler(fakeio, world.controller, sample_queue.put)
        s = sample_queue.get()
        world.logger(s)
        return s

    world.sampler = _sampler

@step(u'When a line is logged')
def a_line_is_logged(step):
    world.sample = world.sampler()

@step(u'Then it contains information about time, temperature and heater')
def it_contains_information_about_temperature_temperature_heater_and_time(step):
    assert world.sample.temperature == DEFAULT_TEMP, 'Temperature is %s' % world.sample.temperature
    assert world.sample.heater == Off, 'Heater is %s' % world.sample.heater
    assert str(world.sample.time) == '1970-01-01 00:00:00', 'Time is %s' % world.sample.time

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

## Controller:

@step(u'Given a mash temperature of (\d+) degrees')
def given_a_mash_temperature_of_66_degrees(step, degrees):
    a_running_system(step)
    world.controller = controller.Controller(fakeio)
    world.controller.mash_temperature = float(degrees)
    world.controller.started = True

@step(u'And the heating is turned (on|off)')
def and_the_heating_is_on_off(step, s):
    fakeio.set_heater(s == 'on')

@step(u'When the fluid is (\d+) degrees')
def when_the_fluid_is_xx_degrees(step, degrees):
    fakeio.temperature = float(degrees)
    world.controller()
    fakeio.time += 30
    world.controller()

@step(u'Then the heating should be turned on')
def then_the_heating_should_be_turned_on(step):
    assert fakeio.read_heater()

@step(u'Then the heating should be turned off')
def then_the_heating_should_be_turned_off(step):
    assert not fakeio.read_heater(), fakeio.read_heater()

@step(u'Given controller and heater turned on')
def given_controller_and_heater_turned_on(step):
    a_running_system(step)
    world.controller.started = True
    fakeio.set_heater(On)
    world.controller.mash_temperature = 66

@step(u'When I turn off the controller')
def when_i_turn_off_the_controller(step):
    world.controller.started = False
    world.controller()
    
# Heat calculation:

@step(u'Given the heater has a performance of (\d+)%')
def given_the_heater_has_a_performance_of_xx(step, pct):
    world.controller.config.performance = int(pct) / 100.

@step(u'And the kettle is (\d+) Watts')
def and_the_kettle_is_xx_watts(step, P):
    world.controller.config.watts = int(P)

@step(u'And the vessel contains (\d+) litres of fluid')
def and_the_vessel_contains_xx_litres_of_fluid(step, ltr):
    world.controller.config.volume = int(ltr)

@step(u'When the temperature difference is (\d+) degrees')
def when_the_temperature_difference_is_xx_degrees(step, deg):
    world.dtemp = int(deg)

@step(u'Then the heater should be turned on for (\d+) seconds')
def then_the_heater_should_be_turned_on_for_xx_seconds(step, t):
    timer = world.controller.config.time(world.dtemp)
    assert int(timer) == int(t), timer

# vim: sw=4:et:ai
