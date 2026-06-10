from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CareersPage(BasePage):
    _EXPLORE_OPEN_ROLES_BTN = (By.XPATH, "//a[.//span[normalize-space()='Explore open roles'] or normalize-space()='Explore open roles']")

    # ------------------------------------------------------------------ #
    # Verifications
    # ------------------------------------------------------------------ #
    def verify_loaded(self):
        url = self.get_current_url()
        self.log.info(f"STEP | Verifying careers page URL → '{url}'")
        assert "careers" in url.lower(), f"Careers sayfası açılmadı. URL: {url}"

    def verify_has_explore_button(self):
        self.log.info("STEP | Verifying 'Explore open roles' button is visible")
        try:
            element = self.find_visible(*self._EXPLORE_OPEN_ROLES_BTN)
            assert element.is_displayed(), "'Explore open roles' butonu görünmüyor"
        except AssertionError:
            raise
        except Exception as exc:
            raise AssertionError(f"'Explore open roles' butonu bulunamadı: {exc}")

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def click_explore_open_roles(self):
        self.log.info("STEP | Clicking 'Explore open roles' button")
        btn = self.find_clickable(*self._EXPLORE_OPEN_ROLES_BTN)
        self.scroll_to_element(btn)
        btn.click()
