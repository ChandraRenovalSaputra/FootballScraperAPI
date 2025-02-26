'''scraper'''
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from config import URLS

class FootballScraper:
    '''Football Scraper'''
    def __render_pages(self, url: str):
        '''render'''
        driver = WebDriver()
        driver.get(url)

        wait = WebDriverWait(
            driver,
            timeout=20,
            poll_frequency=5,
            ignored_exceptions=[NoSuchElementException]
        )

        try:
            reject_btn_privacy = wait.until(
                EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))
            )

            reject_btn_privacy.click()

        except TimeoutException:
            pass

        while True:
            try:
                show_more_button = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'event__more'))
                )

                show_more_button.click()

                wait.until(
                    EC.visibility_of_all_elements_located((By.CLASS_NAME, 'event__time'))
                )

            except TimeoutException:
                break

        return driver


    def __get_match_schedules(self: 'FootballScraper', driver: WebDriver) -> list[str] | list:
        '''get match schedules'''
        match_schedules = []

        try:
            match_schedules_elements = driver.find_elements(By.CLASS_NAME, 'event__time')
        except NoSuchElementException:
            return match_schedules

        for element in match_schedules_elements:
            try:

                postponed = element.find_element(By.CLASS_NAME, 'lineThrough')
                match_schedules.append(postponed.text)

            except NoSuchElementException:
                match_schedules.append(element.text)

        return match_schedules

    def __match_status(self, driver: WebDriver) -> list[bool] | list:
        match_status = []

        try:
            match_schedules_elements = driver.find_elements(By.CLASS_NAME, 'event__time')
        except NoSuchElementException:
            return match_status

        for element in match_schedules_elements:

            try:

                element.find_element(By.CLASS_NAME, 'lineThrough')
                match_status.append("postponed")

            except NoSuchElementException:
                match_status.append("not_postponed")

        return match_status

    def __get_home_clubs(self, driver: WebDriver) -> list[str] | list:
        '''
        fetch match results
        '''
        home_participants = []

        try:
            div_home_participants = driver.find_elements(By.CLASS_NAME, 'event__homeParticipant')

            for home_participant in div_home_participants:

                img_tag_home = home_participant.find_element(By.TAG_NAME, 'img')

                home_participants.append(img_tag_home.get_attribute('alt').lower())
        except NoSuchElementException:
            pass

        return home_participants

    def __get_away_clubs(self, driver: WebDriver) -> list[str]:
        away_participants = []
        try:
            div_away_participants = driver.find_elements(By.CLASS_NAME, 'event__awayParticipant')

            for away_participant in div_away_participants:
                img_tag_away = away_participant.find_element(By.TAG_NAME, 'img')
                away_participants.append(img_tag_away.get_attribute('alt').lower())
        except NoSuchElementException:
            pass

        return away_participants


    def __get_home_scores(self, driver: WebDriver) -> list[str] | list:
        try:
            home_scores_elements = driver.find_elements(By.CLASS_NAME, 'event__score--home')
            home_scores = [score.text for score in home_scores_elements]
            return home_scores
        except NoSuchElementException:
            return []

    def __get_away_scores(self, driver: WebDriver) -> list[str] | list:
        try:
            away_scores_elements = driver.find_elements(By.CLASS_NAME, 'event__score--away')

            away_scores = [score.text for score in away_scores_elements]

            return away_scores
        except NoSuchElementException:
            return []

    def __get_league_name(self, driver: WebDriver) -> list[str] | list:
        try:
            league_name = driver.find_element(By.CLASS_NAME, 'heading__name').text
            return [league_name.lower()]
        except NoSuchElementException:
            return []

    def __get_seasson(self, driver: WebDriver, len_of_data: int) -> list[str]:
        try:
            season = [driver.find_element(By.CLASS_NAME, 'heading__info').text]
            return season * len_of_data
        except NoSuchElementException:
            return []

    def __scraping(self, url: str) -> dict[str, list[str]]:
        '''scrap the data'''
        driver = self.__render_pages(url)

        match_schedules = self.__get_match_schedules(driver)
        is_postponed = self.__match_status(driver)
        league_name = self.__get_league_name(driver)
        season = self.__get_seasson(driver, len(match_schedules))
        home_clubs = self.__get_home_clubs(driver)
        away_clubs = self.__get_away_clubs(driver)
        home_scores = self.__get_home_scores(driver)
        away_scores = self.__get_away_scores(driver)

        scraped_data = {
            'league': league_name,
            'season': season,
            'schedules': match_schedules,
            'match_status': is_postponed,
            'home': home_clubs,
            'away': away_clubs,
            'home_scores': home_scores, 
            'away_scores': away_scores 
        }

        driver.quit()
        return scraped_data

    def start(self):
        '''to start scraping'''
        with ThreadPoolExecutor(max_workers=3) as executor:
            raw_data = executor.map(self.__scraping, URLS)

        return raw_data
