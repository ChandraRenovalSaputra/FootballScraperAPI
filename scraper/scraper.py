'''scraper'''
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from scraper.config import URLS

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


    def __get_match_schedules(self: 'FootballScraper', driver: WebDriver) -> list[str]:
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

    def __is_postponed(self, driver: WebDriver) -> list[bool]:
        postponed_statuses = []

        try:
            match_schedules_elements = driver.find_elements(By.CLASS_NAME, 'event__time')
        except NoSuchElementException:
            return postponed_statuses

        for element in match_schedules_elements:

            try:

                element.find_element(By.CLASS_NAME, 'lineThrough')
                postponed_statuses.append(True)

            except NoSuchElementException:
                postponed_statuses.append(False)

        return postponed_statuses

    def __get_home_clubs(self, driver: WebDriver) -> list[str]:
        '''
        fetch match results
        '''
        home_participants = []

        try:
            div_home_participants = driver.find_elements(By.CLASS_NAME, 'event__homeParticipant')

            for home_participant in div_home_participants:

                img_tag_home = home_participant.find_element(By.TAG_NAME, 'img')

                home_participants.append(img_tag_home.get_attribute('alt'))
        except NoSuchElementException:
            pass

        return home_participants

    def __get_away_clubs(self, driver: WebDriver) -> list[str]:
        away_participants = []
        try:
            div_away_participants = driver.find_elements(By.CLASS_NAME, 'event__awayParticipant')

            for away_participant in div_away_participants:
                img_tag_away = away_participant.find_element(By.TAG_NAME, 'img')
                away_participants.append(img_tag_away.get_attribute('alt'))
        except NoSuchElementException:
            pass

        return away_participants


    def __get_home_scores(self, driver: WebDriver) -> list[int]:
        try:
            home_scores_elements = driver.find_elements(By.CLASS_NAME, 'event__score--home')
            home_scores = [score.text for score in home_scores_elements]
            return home_scores
        except NoSuchElementException:
            return []

    def __get_away_scores(self, driver: WebDriver) -> list[str]:
        try:
            away_scores_elements = driver.find_elements(By.CLASS_NAME, 'event__score--away')

            away_scores = [score.text for score in away_scores_elements]

            return away_scores
        except NoSuchElementException:
            return []

    def __get_league_name(self, driver: WebDriver) -> list[str]:
        try:
            league_name = driver.find_element(By.CLASS_NAME, 'heading__name').text
            return league_name
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
        is_postponed = self.__is_postponed(driver)
        league_name = self.__get_league_name(driver)
        season = self.__get_seasson(driver, len(match_schedules))
        home_clubs = self.__get_home_clubs(driver)
        away_clubs = self.__get_away_clubs(driver)
        home_scores = self.__get_home_scores(driver)
        away_scores = self.__get_away_scores(driver)

        scraped_data = {
            'League': league_name,
            'Season': season,
            'Schedules': match_schedules,
            'Postponed': is_postponed,
            'Home': home_clubs,
            'Away': away_clubs,
            'Home Scores': home_scores, 
            'Away Scores': away_scores 
        }

        driver.quit()
        return scraped_data

    def start(self) -> list[dict[str, list[str]]]:
        '''to start scraping'''
        with ThreadPoolExecutor(max_workers=3) as executor:
            raw_data = list(executor.map(self.__scraping, URLS))

        return raw_data
