import pytest
from utils.driver_factory import DriverFactory
from utils.logger import get_logger
from utils.database import log_test_result
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
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run the browser in headless mode (used on CI agents without a display)",
    )


@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def driver(browser, request):
    headless = request.config.getoption("--headless")
    log.info(f"FIXTURE | Starting '{browser}' driver (headless={headless}, session-scoped, single browser)")
    drv = DriverFactory.get_driver(browser, headless=headless)
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

    if report.when == "call":
        try:
            log_test_result(
                test_name=item.name,
                browser=item.config.getoption("--browser"),
                status="PASS" if report.passed else "FAIL",
                duration=report.duration,
            )
        except Exception as db_exc:
            log.error(f"DB LOGGING FAILED | {db_exc}")
