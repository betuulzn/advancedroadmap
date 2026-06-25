import os
import time
from typing import List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils.logger import get_logger

SCREENSHOT_DIR = os.environ.get(
    "SCREENSHOT_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots"),
)


class BasePage:
    DEFAULT_TIMEOUT = 15

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)
        self.log = get_logger(self.__class__.__name__)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open(self, url: str):
        self.log.info(f"Navigating to: {url}")
        self.driver.get(url)

    # ------------------------------------------------------------------ #
    # Element finders
    # ------------------------------------------------------------------ #
    def find(self, by: By, locator: str) -> WebElement:
        self.log.debug(f"Waiting for presence  → ({by}, {locator})")
        return self.wait.until(EC.presence_of_element_located((by, locator)))

    def find_visible(self, by: By, locator: str) -> WebElement:
        self.log.debug(f"Waiting for visible   → ({by}, {locator})")
        return self.wait.until(EC.visibility_of_element_located((by, locator)))

    def find_clickable(self, by: By, locator: str) -> WebElement:
        self.log.debug(f"Waiting for clickable → ({by}, {locator})")
        return self.wait.until(EC.element_to_be_clickable((by, locator)))

    def find_all(self, by: By, locator: str) -> List[WebElement]:
        self.log.debug(f"Waiting for all       → ({by}, {locator})")
        self.wait.until(EC.presence_of_all_elements_located((by, locator)))
        return self.driver.find_elements(by, locator)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def click(self, by: By, locator: str):
        element = self.find_clickable(by, locator)
        self.log.info(f"Clicking element      → ({by}, {locator})")
        element.click()

    def get_text(self, by: By, locator: str) -> str:
        text = self.find_visible(by, locator).text
        self.log.debug(f"Text retrieved        → '{text}'")
        return text

    def get_title(self) -> str:
        title = self.driver.title
        self.log.debug(f"Page title: '{title}'")
        return title

    def get_current_url(self) -> str:
        url = self.driver.current_url
        self.log.debug(f"Current URL: {url}")
        return url

    def scroll_to_element(self, element: WebElement):
        self.log.debug("Scrolling element into view")
        self.driver.execute_script("arguments[0].scrollIntoView({behavior:'instant', block:'center'});", element)
        WebDriverWait(self.driver, 5).until(EC.visibility_of(element))

    def js_click(self, element: WebElement):
        self.log.debug("JS click on element")
        self.driver.execute_script("arguments[0].click();", element)

    def accept_cookies_if_present(self):
        self.log.info("Checking for cookie consent banner")
        try:
            cookie_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#wt-cli-accept-all-btn"))
            )
            cookie_btn.click()
            self.log.info("Cookie banner accepted")
        except (TimeoutException, NoSuchElementException):
            self.log.debug("No cookie banner found — skipping")

    def take_screenshot(self, name: str) -> str:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        self.log.warning(f"Screenshot saved: {path}")
        return path
