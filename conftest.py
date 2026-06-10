import pytest
from utils.driver_factory import DriverFactory
from utils.logger import get_logger
from pages.base_page import SCREENSHOT_DIR
import os

log = get_logger("conftest")

LOCATION_FILTER = "Istanbul"
DEPARTMENT_FILTER = "Quality Assurance"
SW_DEV_DEPARTMENT = "Software Development"


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome | firefox",
    )


@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def driver(browser):
    log.info(f"FIXTURE | Starting '{browser}' driver (session-scoped, single browser)")
    drv = DriverFactory.get_driver(browser)
    drv.implicitly_wait(0)
    yield drv
    log.info("FIXTURE | Quitting driver")
    drv.quit()



@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver") or getattr(item.funcargs.get("positions_page"), "driver", None)
        if drv:
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            from pages.base_page import BasePage
            path = BasePage(drv).take_screenshot(item.name)
            log.error(f"TEST FAILED → screenshot: {path}")
