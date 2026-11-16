Feature: Unified Quality Assurance Orchestrator
  As a Django developer or QA engineer
  I want to discover and inspect Pytest, Behave, and Locust suites from the admin panel
  So that I can track test execution history across all project apps

  Background:
    Given an authenticated QA superuser exists

  Scenario: View discovered test inventory by app and test case
    When the superuser opens the Quality Assurance dashboard
    Then the response status code should be 200
    And the inventory table should list discovered test cases

  Scenario: Delete an archived execution record from history
    Given an archived QA execution record exists
    When the superuser deletes the archived QA execution record
    Then the execution record should be removed from the database
