Feature: Brew system logging

  Scenario: Log temperature, heater and time
    Given a running system
    When a line is logged
    Then it contains information about time, temperature and heater

  Scenario: One line is logged if the system state is unchanged
    Given a running system
    When a line is logged
    And a second line with the same state
    Then no new line is logged

  Scenario Outline: A line is logged if the temperature difference is big enough
    Given a running system
    When a line is logged
    And a second line with a temparature T plus <delta_t> degrees
    Then <logged> new line is logged

  Examples:
    | delta_t | logged |
    |  0.5    | one    |
    |  0.05   | one    |
    |  0.0499 | no     |
    |  0.00   | no     |
    | -0.0499 | no     |
    | -0.05   | one    |
    | -0.5    | one    |


  Scenario: A line is logged at least once a minute
    Given a running system
    When a line is logged
    And a minute expires
    Then one new line is logged
