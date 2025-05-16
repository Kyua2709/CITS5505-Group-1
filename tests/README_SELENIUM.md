# Selenium Tests for SentiSocial

This directory contains Selenium tests for the SentiSocial web application. These tests automate browser interactions to verify that the application's UI and functionality work correctly.

## Test Coverage

The Selenium tests cover the following functionality:

1. **Home Page Test** (`test_home_page_loads`): Verifies that the home page loads correctly, including checking the title, main heading, navigation links, and login/register buttons.

2. **User Registration Test** (`test_user_registration`): Tests the user registration functionality by filling out and submitting the registration form with a randomly generated email.

3. **User Login Test** (`test_user_login`): Tests the user login functionality by logging in with the credentials created during the registration test.

4. **File Upload Test** (`test_file_upload`): Tests the manual data entry functionality by navigating to the upload page, filling out the form, and submitting it.

5. **Analysis Page Test** (`test_analysis_page`): Tests the analysis page functionality by navigating to the page and verifying that the upload select dropdown is present and functional.

## Prerequisites

Before running the tests, make sure you have the following installed:

- Python 3.6 or higher
- Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

## Required Python Packages

The following Python packages are required to run the tests:

- pytest
- selenium
- webdriver-manager

These dependencies are already included in the project's `requirements.txt` file.

## Running the Tests

You can run the Selenium tests using the provided `run_selenium_tests.py` script in the project root directory:

```bash
python run_selenium_tests.py
```

This script will:

1. Start the Flask application in testing mode
2. Run the Selenium tests
3. Shut down the Flask application when the tests are complete

Alternatively, you can run the tests directly using pytest:

```bash
# Make sure the Flask application is running first
python -m pytest tests/test_selenium.py -v
```

## Test Configuration

The tests are configured to run in headless mode by default, which means the browser will not be visible during test execution. This is suitable for CI/CD environments. If you want to see the browser during test execution, you can modify the `driver` fixture in `test_selenium.py` to remove the `--headless` option.

## Troubleshooting

If you encounter issues running the tests, check the following:

1. Make sure the Flask application is running on `http://localhost:5001` when running the tests directly with pytest.
2. Ensure that Chrome and ChromeDriver are properly installed and compatible with each other.
3. Check that all required Python packages are installed.
4. If tests are failing due to timing issues, you may need to increase the wait times in the WebDriverWait calls.

## Adding New Tests

To add new Selenium tests:

1. Add new test functions to `test_selenium.py` or `test_user_flow.py`
2. Follow the existing pattern of using WebDriverWait for elements that may take time to load
3. Use clear assertions to verify expected behavior
4. Keep tests independent of each other when possible
