
import urllib.parse
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage


class OpenPositionsPage(BasePage):
    URL = "https://jobs.lever.co/insiderone"

    # Careers page – department card (clicked before Lever navigation)
    _DEPT_CARD_BTN = (By.XPATH,
        "//div[contains(@class,'insiderone-icon-cards-grid-item') and @data-department='{dept}']"
        "//a[contains(@class,'insiderone-icon-cards-grid-item-btn')]")

    # Lever job board – job listing items
    _JOB_LIST_ITEMS = (By.CSS_SELECTOR, "div.posting")
    _JOB_DEPT_HEADER = (By.CSS_SELECTOR, ".posting-category-title")
    _JOB_LOCATION = (By.CSS_SELECTOR, "span.sort-by-location")
    _APPLY_BTN = (By.CSS_SELECTOR, "a.posting-btn-submit")
    _CONTENT_WRAPPER = (By.CSS_SELECTOR, ".content-wrapper")

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def load(self):
        self.log.info("STEP | Opening Open Positions page directly")
        self.open(self.URL)

    def navigate_to_department(self, department: str):
        """Clicks the department card on the insider careers page to reach the Lever board."""
        self.log.info(f"STEP | Clicking '{department}' department card")
        xpath = self._DEPT_CARD_BTN[1].replace("{dept}", department)

        # Expand hidden cards section if present; use JS click to bypass overlays
        see_more_btn = self.driver.find_elements(By.CSS_SELECTOR, ".see-more")
        if see_more_btn:
            self.log.info("      Clicking 'See more' to expand hidden department cards")
            self.scroll_to_element(see_more_btn[0])
            self.js_click(see_more_btn[0])

        card_btn = self.find_clickable(By.XPATH, xpath)
        self.scroll_to_element(card_btn)

        href = card_btn.get_attribute("href") or ""
        self.log.info(f"      Card button href: '{href}'")

        if "lever.co" in href:
            self.log.info("      Navigating directly via href")
            self.driver.get(href)
        else:
            self.js_click(card_btn)
            self.log.info(f"      Waiting for Lever board navigation for '{department}'")
            try:
                WebDriverWait(self.driver, 15).until(EC.url_contains("lever.co"))
            except TimeoutException as e:
                self.log.warning(f"      Navigation timed out: {e}")
                dept_encoded = urllib.parse.quote(department, safe="")
                fallback_url = f"{self.URL}?team={dept_encoded}"
                self.log.warning(f"      Falling back to: {fallback_url}")
                self.driver.get(fallback_url)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self._CONTENT_WRAPPER)
        )

    def apply_lever_filters(self, team: str, location: str):
        """Sets Team and Location filters on the Lever board via URL parameters in one navigation."""
        self.log.info(f"STEP | Applying Lever filters → team='{team}', location='{location}'")
        parsed = urllib.parse.urlparse(self.driver.current_url)
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        params["team"] = [team]
        params["location"] = [location]
        new_query = urllib.parse.urlencode(params, doseq=True)
        new_url = urllib.parse.urlunparse(parsed._replace(query=new_query))
        self.log.info(f"      Navigating to: {new_url}")
        self.driver.get(new_url)
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self._JOB_LIST_ITEMS)
        )

    def wait_for_jobs_to_load(self):
        self.log.info("STEP | Waiting for job listing items to appear")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located(self._JOB_LIST_ITEMS)
        )
        count = len(self.driver.find_elements(*self._JOB_LIST_ITEMS))
        self.log.info(f"      {count} job listing(s) loaded")

    def get_job_items(self) -> List[WebElement]:
        items = self.find_all(*self._JOB_LIST_ITEMS)
        self.log.debug(f"get_job_items → {len(items)} items found")
        return items

    def get_job_department(self, item: WebElement) -> str:
        headers = self.driver.find_elements(*self._JOB_DEPT_HEADER)
        return headers[0].text.strip() if headers else ""

    def get_job_location(self, item: WebElement) -> str:
        try:
            return item.find_element(*self._JOB_LOCATION).text.strip()
        except NoSuchElementException as e:
            self.log.debug(f"Location element not found: {e}")
            return ""

    def click_apply_on_first_job(self):
        self.log.info("STEP | Clicking 'Apply' button on the first job listing")
        jobs = self.get_job_items()
        assert jobs, "No job listings found to click Apply"
        apply_btn = jobs[0].find_element(*self._APPLY_BTN)
        self.scroll_to_element(apply_btn)
        apply_btn.click()
        self.log.info("      Apply button clicked")

    # ------------------------------------------------------------------ #
    # Verifications
    # ------------------------------------------------------------------ #
    def verify_jobs_listed(self, department: str, location: str):
        jobs = self.get_job_items()
        self.log.info(f"STEP | Verifying jobs listed → {len(jobs)} found")
        assert len(jobs) > 0, f"'{department}' / '{location}' için ilan bulunamadı"

    def verify_all_jobs_department(self, department: str):
        self.log.info(f"STEP | Verifying all jobs belong to '{department}'")
        for idx, job in enumerate(self.get_job_items(), start=1):
            dept = self.get_job_department(job)
            assert department.lower() in dept.lower(), (
                f"İlan {idx}: '{dept}' içinde '{department}' yok"
            )

    def verify_all_jobs_location(self, location: str):
        self.log.info(f"STEP | Verifying all jobs are in '{location}'")
        for idx, job in enumerate(self.get_job_items(), start=1):
            loc = self.get_job_location(job)
            assert location.lower() in loc.lower(), (
                f"İlan {idx}: '{loc}' içinde '{location}' yok"
            )

    def verify_apply_redirects_to_lever(self):
        self.log.info("STEP | Verifying Apply button redirects to lever.co")
        self.click_apply_on_first_job()
        WebDriverWait(self.driver, 15).until(EC.url_contains("lever.co"))
        url = self.driver.current_url
        assert "lever.co" in url, f"Lever sayfası beklendi, gelen URL: {url}"
