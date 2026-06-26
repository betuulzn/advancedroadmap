from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://insiderone.com/"

    _FOOTER_WE_ARE_HIRING = (By.XPATH, "//a[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),\"we're hiring\")]")

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def load(self):
        self.log.info("STEP | Opening Insider homepage")
        self.open(self.URL)
        self.accept_cookies_if_present()

    def verify_loaded(self):
        title = self.get_title()
        self.log.info(f"STEP | Verifying homepage title → '{title}'")
        assert "Insider" in title, f"Başlıkta 'Insider' bulunamadı: '{title}'"

    def verify_url(self):
        url = self.get_current_url()
        self.log.info(f"STEP | Verifying homepage URL → '{url}'")
        assert "insiderone.com" in url, f"Beklenmeyen URL: {url}"

    def click_we_are_hiring(self):
        self.log.info("STEP | Scrolling to footer 'We're hiring' link")
        link = self.find_clickable(*self._FOOTER_WE_ARE_HIRING)
        self.scroll_to_element(link)
        self.take_screenshot("we_are_hiring_visible")
        self.log.info("STEP | Clicking 'We're hiring' link")
        link.click()
