import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def _resolve_driver_path(raw_path: str) -> str:
    """webdriver-manager 4.x sometimes returns the wrong file path.
    Look for the largest executable in the same directory (the actual binary)."""
    driver_dir = os.path.dirname(raw_path)
    named = os.path.join(driver_dir, os.path.basename(driver_dir).split("-")[0])
    # e.g. chromedriver-mac-arm64/chromedriver or geckodriver-...
    for candidate in [named, raw_path]:
        if os.path.isfile(candidate):
            os.chmod(candidate, 0o755)
            return candidate
    # fallback: biggest file in directory
    files = [os.path.join(driver_dir, f) for f in os.listdir(driver_dir)]
    return max(files, key=os.path.getsize)


class DriverFactory:
    @staticmethod
    def get_driver(browser: str, headless: bool = False) -> webdriver.Remote:
        browser = browser.lower()
        if browser == "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            if headless:
                # Headless Chrome on CI agents needs these to avoid sandbox/shm crashes
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
            driver_path = _resolve_driver_path(ChromeDriverManager().install())
            service = ChromeService(driver_path)
            return webdriver.Chrome(service=service, options=options)
        elif browser == "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            if headless:
                options.add_argument("-headless")
            driver_path = _resolve_driver_path(GeckoDriverManager().install())
            service = FirefoxService(driver_path)
            return webdriver.Firefox(service=service, options=options)
        else:
            raise ValueError(f"Unsupported browser: '{browser}'. Use 'chrome' or 'firefox'.")
