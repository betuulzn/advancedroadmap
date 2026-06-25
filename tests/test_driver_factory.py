"""Unit tests for DriverFactory.

These tests mock out Selenium/webdriver-manager (via the stdlib unittest.mock)
so no real browser or driver binary is launched — they only assert the factory's
wiring/dispatch logic:
  * chrome is built through webdriver-manager + an explicit ChromeService,
  * firefox is built through Selenium Manager (no explicit service, so geckodriver
    is NOT resolved via webdriver-manager's GitHub API),
  * an unsupported browser raises ValueError,
  * the --browser value is case-insensitive,
  * headless toggles the Chrome CI hardening flags.
"""

from unittest.mock import patch

import pytest

from utils.driver_factory import DriverFactory


@pytest.fixture
def selenium_mocks():
    """Patch the Selenium entry points used by DriverFactory.

    webdriver-manager's install() and our _resolve_driver_path() are stubbed too,
    so the chrome path never touches the network or the filesystem.
    """
    with patch("utils.driver_factory.webdriver.Chrome") as chrome, \
         patch("utils.driver_factory.webdriver.Firefox") as firefox, \
         patch("utils.driver_factory.ChromeDriverManager.install",
               return_value="/tmp/chromedriver"), \
         patch("utils.driver_factory._resolve_driver_path",
               return_value="/tmp/chromedriver"):
        yield chrome, firefox


def test_chrome_uses_explicit_service(selenium_mocks):
    chrome, firefox = selenium_mocks

    driver = DriverFactory.get_driver("chrome", headless=True)

    chrome.assert_called_once()
    firefox.assert_not_called()
    # Chrome must be wired with an explicit Service (webdriver-manager path).
    assert "service" in chrome.call_args.kwargs
    assert driver is chrome.return_value


def test_firefox_uses_selenium_manager_no_service(selenium_mocks):
    chrome, firefox = selenium_mocks

    driver = DriverFactory.get_driver("firefox", headless=True)

    firefox.assert_called_once()
    chrome.assert_not_called()
    # Firefox must NOT pass an explicit service: that is what lets Selenium Manager
    # resolve geckodriver instead of webdriver-manager's GitHub API call.
    assert "service" not in firefox.call_args.kwargs
    assert driver is firefox.return_value


def test_browser_is_case_insensitive(selenium_mocks):
    chrome, _ = selenium_mocks

    DriverFactory.get_driver("CHROME", headless=False)

    chrome.assert_called_once()


def test_unsupported_browser_raises(selenium_mocks):
    with pytest.raises(ValueError, match="Unsupported browser"):
        DriverFactory.get_driver("safari")


def test_chrome_headless_adds_ci_flags(selenium_mocks):
    chrome, _ = selenium_mocks

    DriverFactory.get_driver("chrome", headless=True)

    options = chrome.call_args.kwargs["options"]
    assert "--headless=new" in options.arguments
    assert "--no-sandbox" in options.arguments


def test_chrome_non_headless_omits_ci_flags(selenium_mocks):
    chrome, _ = selenium_mocks

    DriverFactory.get_driver("chrome", headless=False)

    options = chrome.call_args.kwargs["options"]
    assert "--headless=new" not in options.arguments
