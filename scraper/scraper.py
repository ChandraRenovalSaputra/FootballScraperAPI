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

                    # EC.all_of(
                    #     EC.visibility_of_all_elements_located((By.CLASS_NAME, 'event__time')),
                    #     EC.visibility_of_all_elements_located(
                    #         (By.CLASS_NAME, 'event__homeParticipant')
                    #     )
                    # )

                    EC.visibility_of_all_elements_located((By.CLASS_NAME, 'event__time'))

                )

            except TimeoutException:
                # print('no more button to clicked')
                break

        return driver


    def __fetch_match_schedules(self: 'FootballScraper', driver: WebDriver) -> list[str]:
        '''get match schedules'''
        match_schedules_elements = driver.find_elements(By.CLASS_NAME, 'event__time')
        match_schedules = [schedule.text for schedule in match_schedules_elements]
        league_name = driver.find_element(By.CLASS_NAME, 'heading__name').text
        season = driver.find_element(By.CLASS_NAME, 'heading__info').text
        # print(f'match schedule: {len(match_schedules)}')
        return match_schedules, league_name, season

    def __fetch_home_away_clubs(self, driver: WebDriver) -> tuple[list[str], list[str]]:
        '''
        fetch match results
        '''
        home_participants = []
        away_participants = []

        div_home_participants = driver.find_elements(By.CLASS_NAME, 'event__homeParticipant')
        div_away_participants = driver.find_elements(By.CLASS_NAME, 'event__awayParticipant')

        for home_participant, away_participant in zip(div_home_participants, div_away_participants):

            img_tag_home = home_participant.find_element(By.TAG_NAME, 'img')
            img_tag_away = away_participant.find_element(By.TAG_NAME, 'img')

            home_participants.append(img_tag_home.get_attribute('alt'))
            away_participants.append(img_tag_away.get_attribute('alt'))

        # print(f'Home Participants : {len(home_participants)}')
        # print(f'Away Participants : {len(away_participants)}')
        return home_participants, away_participants

    def __fetch_match_scores(self, driver: WebDriver) -> tuple[list[int], list[int]]:
        home_scores_elements = driver.find_elements(By.CLASS_NAME, 'event__score--home')
        away_scores_elements = driver.find_elements(By.CLASS_NAME, 'event__score--away')

        home_scores = [score.text for score in home_scores_elements]
        away_scores = [score.text for score in away_scores_elements]

        # print(f'Home Scores: {len(home_scores)}')
        # print(f'Away Scores: {len(away_scores)}')

        return home_scores, away_scores

    def __scraping(self, url: str) -> dict[str, str | list[str]]:
        '''scrap the data'''
        driver = self.__render_pages(url)

        match_schedules, league_name, season = self.__fetch_match_schedules(driver)
        home_clubs, away_clubs = self.__fetch_home_away_clubs(driver)
        home_scores, away_scores = self.__fetch_match_scores(driver)

        scraped_data = {
            'League': league_name,
            'Season': season,
            'Schedules': match_schedules,
            'Home': home_clubs,
            'Away': away_clubs,
            'Home Scores': home_scores, 
            'Away Scores': away_scores 
        }

        driver.quit()
        return scraped_data

    def start(self):
        '''to start scraping'''
        with ThreadPoolExecutor(max_workers=3) as executor:
            raw_data = executor.map(self.__scraping, URLS)

        return raw_data
