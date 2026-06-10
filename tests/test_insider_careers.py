

from pages.home_page import HomePage
from pages.careers_page import CareersPage
from pages.open_positions_page import OpenPositionsPage
from utils.logger import get_logger
from conftest import LOCATION_FILTER, DEPARTMENT_FILTER, SW_DEV_DEPARTMENT


class TestInsiderCareers:
    """
    E2E test for Insider careers flow:
        1. Open Insider homepage and verify it loads correctly
        2. Navigate to Careers page via 'We're Hiring' footer link and verify it loads
        3. Verify 'Explore Open Roles' button is visible, click it; then click
           'Open Positions' under the Software Development block
        4. Apply Team='Quality Assurance' and Location='Istanbul, Turkiye' filters
           on the Lever board and verify listings appear
        5. Verify every listing shows 'Quality Assurance' department and 'Istanbul, Turkiye'
        6. Click Apply on the first job and verify redirect to the Lever application form
    """

    location_filter = LOCATION_FILTER
    department_filter = DEPARTMENT_FILTER
    sw_dev_department = SW_DEV_DEPARTMENT

    def test_insider_careers_e2e(self, driver):
        """Tests the full Insider careers flow from homepage to job application redirect."""
        logger = get_logger(self.__class__.__name__)

        logger.info("1. Open Insider homepage")
        home = HomePage(driver)
        home.load()
        home.verify_loaded()
        home.verify_url()
        logger.info("Homepage loaded and verified successfully!")

        logger.info("2. Navigate to Careers page via 'We're Hiring' footer link")
        home.click_we_are_hiring()
        careers = CareersPage(driver)
        careers.verify_loaded()
        logger.info("Careers page opened and verified successfully!")

        logger.info("3. Verify 'Explore Open Roles' button, click it, then click Software Development Open Positions")
        careers.verify_has_explore_button()
        logger.info("'Explore Open Roles' button is visible!")
        careers.click_explore_open_roles()
        positions = OpenPositionsPage(driver)
        positions.navigate_to_department(self.sw_dev_department)
        logger.info(f"Navigated to Lever board via '{self.sw_dev_department}' Open Positions link")

        logger.info("4. Apply Team and Location filters on the Lever board")
        positions.apply_lever_filters(team=self.department_filter, location=self.location_filter)
        positions.wait_for_jobs_to_load()
        logger.info(f"Filters applied: team='{self.department_filter}', location='{self.location_filter}'")

        logger.info("5. Verify job listings are present with correct department and location")
        positions.verify_jobs_listed(self.department_filter, self.location_filter)
        positions.verify_all_jobs_department(self.department_filter)
        positions.verify_all_jobs_location(self.location_filter)
        logger.info("All job listings verified for correct department and location!")

        logger.info("6. Click Apply on first job and verify redirect to lever.co")
        positions.verify_apply_redirects_to_lever()
        logger.info("Apply button redirected to lever.co successfully!")
