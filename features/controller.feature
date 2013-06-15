Feature: Temperature control
  The system should be able to maintain a constant temperature for mashing

  Scenario: start heating if temperature is to low
    Given a mash temperature of 66 degrees
    And the heating is turned off
    When the fluid is 64 degrees
    Then the heating should be turned on

  Scenario: stop heating if the temperature is achieved
    Given a mash temperature of 66 degrees
    And the heating is turned on
    When the fluid is 66 degrees
    Then the heating should be turned off

  Scenario: heater is turned off if controller is turned off
    Given controller and heater turned on
    When I turn off the controller
    Then the heating should be turned off
