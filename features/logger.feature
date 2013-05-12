Feature: Brew system logging

  Scenario: Log temperature, heater and time
    Given a running system
    When a line is logged
    Then it contains information about time, temperature and heater

  Scenario: One line is logged if the system state is unchanged
    Given a running system
    When a line is logged
    And a second line with the same state
    Then only 1 line is logged

  Scenario: One line is logged if the temperature difference is < 0.05 degrees
    Given a running system
    When a line is logged
    And a second line with a temparature T plus 0.05 degrees
    Then only 1 line is logged

#  Examples:
#    | delta_t | n_lines |
#    | 0.0     | 
