import pytest
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Generate random email
def random_email():
    username = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    return f"{username}@example.com"

# Test user data
test_data = {
    "email": random_email(),
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
}

# Set up WebDriver
@pytest.fixture(scope="module")
def driver():
    """Set up Chrome WebDriver for testing"""
    print("Setting up Chrome WebDriver...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    driver.maximize_window()
    driver.implicitly_wait(10)

    yield driver

    print("Closing Chrome WebDriver...")
    driver.quit()

# Test 1: Home page load
def test_home_page(driver):
    """Test if the home page loads correctly"""
    print("\nTest 1: Verify home page load...")

    driver.get("http://localhost:5001")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hero-section"))
        )
        print("✓ Home page loaded successfully")
    except TimeoutException:
        pytest.fail("❌ Home page load timed out")

    assert "SentiSocial" in driver.title, "❌ Incorrect page title"
    print("✓ Page title is correct")

    nav_links = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-link")
    assert len(nav_links) >= 3, "❌ Not enough navigation links"
    print(f"✓ Found {len(nav_links)} navigation links")

    try:
        login_button = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#loginModal']")
        assert "Login" in login_button.text, "❌ Login button text incorrect"
        print("✓ Login button found")

        register_button = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#registerModal']")
        assert "Sign Up" in register_button.text, "❌ Sign Up button text incorrect"
        print("✓ Sign Up button found")
    except NoSuchElementException:
        pytest.fail("❌ Login or Sign Up button not found")

# Test 2: User registration
def test_user_registration(driver):
    """Test user registration functionality"""
    print("\nTest 2: Test user registration...")

    driver.get("http://localhost:5001")

    try:
        register_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#registerModal']"))
        )
        register_button.click()
        print("✓ Clicked Sign Up button")
    except TimeoutException:
        pytest.fail("❌ Sign Up button not clickable")

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "registerModal"))
        )
        print("✓ Register modal is visible")
    except TimeoutException:
        pytest.fail("❌ Register modal not shown")

    try:
        driver.find_element(By.ID, "firstName").send_keys(test_data["first_name"])
        driver.find_element(By.ID, "lastName").send_keys(test_data["last_name"])
        driver.find_element(By.ID, "registerEmail").send_keys(test_data["email"])
        driver.find_element(By.ID, "registerPassword").send_keys(test_data["password"])
        driver.find_element(By.ID, "confirmPassword").send_keys(test_data["password"])
        print("✓ Filled in registration form")
    except NoSuchElementException as e:
        pytest.fail(f"❌ Registration form field not found: {e}")

    try:
        driver.execute_script("""
            var form = document.getElementById('registerForm');
            var button = form.querySelector('button[type="submit"]');
            button.click();
        """)
        print("✓ Submitted registration form")
    except Exception as e:
        pytest.fail(f"❌ Failed to submit registration form: {e}")

    time.sleep(2)
    print("✓ Registration assumed successful")

# Test 3: User login
def test_user_login(driver):
    """Test user login functionality"""
    print("\nTest 3: Test user login...")

    driver.get("http://localhost:5001")

    try:
        dropdown = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "userDropdown"))
        )
        dropdown.click()

        logout_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-menu a"))
        )
        logout_link.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-bs-target='#loginModal']"))
        )
        print("✓ Logged out previous session")
    except TimeoutException:
        print("✓ No logged-in session detected")

    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#loginModal']"))
        )
        login_button.click()
        print("✓ Clicked Login button")
    except TimeoutException:
        pytest.fail("❌ Login button not clickable")

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "loginModal"))
        )
        print("✓ Login modal is visible")
    except TimeoutException:
        pytest.fail("❌ Login modal not shown")

    try:
        driver.find_element(By.ID, "loginEmail").send_keys(test_data["email"])
        driver.find_element(By.ID, "loginPassword").send_keys(test_data["password"])
        print("✓ Filled in login form")
    except NoSuchElementException as e:
        pytest.fail(f"❌ Login form field not found: {e}")

    try:
        submit_button = driver.find_element(By.CSS_SELECTOR, "#loginForm button[type='submit']")
        submit_button.click()
        print("✓ Submitted login form")
    except NoSuchElementException:
        pytest.fail("❌ Login form submit button not found")

    time.sleep(2)

    try:
        user_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userDropdown"))
        )
        assert test_data["first_name"] in user_dropdown.text, "❌ User name not shown in dropdown"
        print("✓ Login successful")
    except TimeoutException:
        pytest.fail("❌ Login failed, user dropdown not found")
