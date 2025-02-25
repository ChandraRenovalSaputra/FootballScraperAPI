'''module automate preprocessing'''

from datetime import datetime
import pandas as pd
import numpy as np
from config import URLS

class Preprocessing:
    """automate preprocessing class"""

    def __init__(self, raw_data: list[dict[str, list[str]]]) -> None:
        self.__bound = int(len(URLS) / 2)
        self.__raw_data = raw_data
        self.__results_df = self.__create_results_df()
        self.__fixtures_df = self.__create_fixtures_df()

        self.__results_df = self.__format_data(self.__results_df)
        self.__fixtures_df = self.__format_data(self.__fixtures_df)

        self.__standings_df = self.__create_standings_df(
            self.__results_df, self.__fixtures_df
        )

        self.__results_df, self.__fixtures_df, self.__standings_df = self.__concate_df()

    def __create_results_df(self) -> dict[str, pd.DataFrame]:
        results_df = {}

        for _ in range(self.__bound):
            result_data = next(self.__raw_data)
            result_data.pop("match_status")

            league_name = result_data["league"][0]
            result_data["league"] *= len(result_data["season"])

            results_df[league_name] = pd.DataFrame(result_data)

        return results_df

    def __create_fixtures_df(self) -> dict[str, pd.DataFrame]:
        fixtures_df = {}

        for _ in range(self.__bound):
            fixture_data = next(self.__raw_data)
            fixture_data.pop("home_scores")
            fixture_data.pop("away_scores")

            league_name = fixture_data["league"][0]
            fixture_data["league"] *= len(fixture_data["season"])

            fixtures_df[league_name] = pd.DataFrame(fixture_data)

        return fixtures_df

    def __create_standings_df(
        self, results_df: dict[str, pd.DataFrame], fixtures_df: dict[str, pd.DataFrame]
    ) -> dict[str, pd.DataFrame]:
        df = {}

        for key in results_df.keys():
            df[key] = pd.DataFrame(
                columns=["league", "team", "MP", "W", "D", "L", "GF", "GA", "GD", "PTS"]
            )

            df[key] = self.__add_all_teams_and_league(
                df[key], results_df[key], fixtures_df[key]
            )

            if results_df[key].empty:
                df[key].loc[:, "MP":] = 0
            else:
                df[key] = self.__calculate_win_draw_lose(df[key], results_df[key])
                df[key] = self.__calculate_match_played(df[key])
                df[key] = self.__calculate_gf_ga_gd(df[key], results_df[key])
                df[key] = self.__calculate_pts(df[key])

        return df

    def __concate_df(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        results = pd.DataFrame()
        fixtures = pd.DataFrame()
        standings = pd.DataFrame()

        for result, fixture, standing in zip(
            self.__results_df.values(),
            self.__fixtures_df.values(),
            self.__standings_df.values(),
        ):
            results = pd.concat([results, result], ignore_index=True)
            fixtures = pd.concat([fixtures, fixture], ignore_index=True)
            standings = pd.concat([standings, standing], ignore_index=True)

        return results, fixtures, standings

    def __calculate_match_played(self, df: pd.DataFrame) -> pd.DataFrame:
        df["MP"] = df["W"] + df["D"] + df["L"]
        return df

    def __calculate_win_draw_lose(
        self, df: pd.DataFrame, result_df: pd.DataFrame
    ) -> pd.DataFrame:
        conditions = [
            result_df["home_scores"] > result_df["away_scores"],
            result_df["home_scores"] < result_df["away_scores"],
        ]
        choices = [result_df["home"], result_df["away"]]
        win_counts = np.select(conditions, choices, default=None)
        win_counts = (
            pd.Series(win_counts).value_counts().reindex(df["team"], fill_value=0)
        )

        df["W"] = win_counts.values

        # lose
        conditions = [
            result_df["home_scores"] < result_df["away_scores"],
            result_df["home_scores"] > result_df["away_scores"],
        ]

        lose_counts = np.select(conditions, choices, default=None)
        lose_counts = (
            pd.Series(lose_counts).value_counts().reindex(df["team"], fill_value=0)
        )

        df["L"] = lose_counts.values

        # draw
        draw_mask = result_df["home_scores"] == result_df["away_scores"]
        draw_clubs = result_df.loc[draw_mask, ["home", "away"]]
        draw_counts = pd.concat(
            [draw_clubs["home"], draw_clubs["away"]], ignore_index=True
        )
        draw_counts = draw_counts.value_counts().reindex(df["team"], fill_value=0)

        df["D"] = draw_counts.values
        return df

    def __calculate_pts(self, df: pd.DataFrame) -> pd.DataFrame:
        df["PTS"] = (df["W"] * 3) + df["D"]
        return df

    def __calculate_gf_ga_gd(
        self, df: pd.DataFrame, results_df: pd.DataFrame
    ) -> pd.DataFrame:
        results_df = results_df.loc[:, "home":]
        melted = results_df.melt(
            value_vars=["home", "away"],
            var_name="Role",
            value_name="Team",
            ignore_index=True,
        )

        melted["GF"] = results_df.melt(value_vars=["home_scores", "away_scores"])[
            "value"
        ]
        melted["GA"] = results_df.melt(value_vars=["away_scores", "home_scores"])[
            "value"
        ]
        melted["GD"] = melted["GF"] - melted["GA"]

        result = (
            melted.groupby("Team")[["GF", "GA", "GD"]]
            .sum()
            .reindex(df["team"], fill_value=0)
        )
        df["GF"] = result["GF"].values
        df["GA"] = result["GA"].values
        df["GD"] = result["GD"].values

        return df

    def __add_all_teams_and_league(
        self, df: pd.DataFrame, results_df: pd.DataFrame, fixtures_df: pd.DataFrame
    ) -> pd.DataFrame:
        all_teams = pd.concat(
            [results_df.loc[:, "home"], fixtures_df.loc[:, "home"]], ignore_index=True
        ).unique()

        df.loc[:, "team"] = all_teams

        league = list(results_df["league"].unique())
        df["league"] = league * len(all_teams)
        return df

    def __format_schedules(self, df: pd.DataFrame, is_results: bool) -> pd.DataFrame:
        """to formatting Schedules"""
        schedules = [schedule.split(" ") for schedule in df["schedules"]]

        current_date = datetime.now()
        current_year = current_date.year

        for schedule in schedules:
            schedule[0] = schedule[0].removesuffix(".")

            day, month = map(int, schedule[0].split("."))

            date = datetime(current_year, month, day)

            if is_results and date > current_date:
                year = current_year - 1
                date = datetime(year, month, day)
                schedule[0] = date
            else:
                schedule[0] = date

            schedule[0] = schedule[0].strftime("%d/%m/%Y")

        date = [schedule[0] for schedule in schedules]
        time = [schedule[-1] for schedule in schedules]

        df.drop(columns=["schedules"], inplace=True)
        df["date"] = date
        df["time"] = time

        return df

    def __convert_score_types(self, df: pd.DataFrame) -> pd.DataFrame:
        if "home_scores" in df.columns:
            df["home_scores"] = df["home_scores"].apply(int)
            df["away_scores"] = df["away_scores"].apply(int)
        return df

    def __format_data(self, dfs: dict[pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for df in dfs.values():
            is_results = "match_status" not in df.columns
            df = self.__format_schedules(df, is_results)
            df = self.__convert_score_types(df)

        return dfs

    @property
    def results(self) -> pd.DataFrame:
        """to return result df"""
        return self.__results_df

    @property
    def fixtures(self) -> pd.DataFrame:
        """return fixtures df"""
        return self.__fixtures_df

    @property
    def standings(self) -> pd.DataFrame:
        """return standings df"""
        return self.__standings_df
