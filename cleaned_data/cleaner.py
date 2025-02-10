'''module automate preprocessing'''

import copy
import pandas as pd
import numpy as np
from utils.utils import format_datetime

class Preprocessing:
    '''automate preprocessing class'''
    def __init__(self, raw_data: list[dict[str, list[str]]]) -> None:
        self.__raw_data = copy.deepcopy(raw_data)
        self.__results_df = self.__create_results_df()
        self.__fixtures_df = self.__create_fixtures_df()

        self.__results_df = self.__format_data(self.__results_df)
        self.__fixtures_df = self.__format_data(self.__fixtures_df)

        self.__standings_df = self.__create_standings_df(
            self.__results_df, self.__fixtures_df
        )

        self.__results_df, self.__fixtures_df, self.__standings_df = self.__concate_df()

    def __create_results_df(self) -> dict[str, pd.DataFrame]:
        results_data = self.__raw_data[: int(len(self.__raw_data) / 2)]
        results_df = {}

        for result_data in results_data:
            result_data.pop("Postponed")

            league_name = result_data["League"]
            result_data.pop("League")

            results_df[league_name] = pd.DataFrame(result_data)

        return results_df

    def __create_fixtures_df(self) -> dict[str, pd.DataFrame]:
        fixtures_data = self.__raw_data[int(len(self.__raw_data) / 2) :]
        fixtures_df = {}

        for fixture_data in fixtures_data:

            fixture_data.pop("Home Scores")
            fixture_data.pop("Away Scores")

            league_name = fixture_data["League"]
            fixture_data.pop("League")

            fixtures_df[league_name] = pd.DataFrame(fixture_data)

        return fixtures_df

    def __create_standings_df(
        self, results_df: dict[str, pd.DataFrame], fixtures_df: dict[str, pd.DataFrame]
    ) -> dict[str, pd.DataFrame]:
        df = {}

        for key in results_df.keys():
            df[key] = pd.DataFrame(
                columns=["TEAM", "MP", "W", "D", "L", "GF", "GA", "GD", "PTS"]
            )

            if results_df[key].empty:
                df[key].loc[:, "MP":] = 0
            else:
                df[key] = self.__all_teams(df[key], results_df[key], fixtures_df[key])
                df[key] = self.__calculate_win_draw_lose(df[key], results_df[key])
                df[key] = self.__calculate_match_played(df[key])
                df[key] = self.__calculate_gf_ga_gd(df[key], results_df[key])
                df[key] = self.__calculate_pts(df[key])
                df[key].sort_values(
                    by=["PTS", "GD", "GF"], ignore_index=True, inplace=True, ascending=False
                )

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
            result_df["Home Scores"] > result_df["Away Scores"],
            result_df["Home Scores"] < result_df["Away Scores"],
        ]
        choices = [result_df["Home"], result_df["Away"]]
        win_counts = np.select(conditions, choices, default=None)
        win_counts = (
            pd.Series(win_counts).value_counts().reindex(df["TEAM"], fill_value=0)
        )

        df["W"] = win_counts.values

        # lose
        conditions = [
            result_df["Home Scores"] < result_df["Away Scores"],
            result_df["Home Scores"] > result_df["Away Scores"],
        ]

        lose_counts = np.select(conditions, choices, default=None)
        lose_counts = (
            pd.Series(lose_counts).value_counts().reindex(df["TEAM"], fill_value=0)
        )

        df["L"] = lose_counts.values

        # draw
        draw_mask = result_df["Home Scores"] == result_df["Away Scores"]
        draw_clubs = result_df.loc[draw_mask, ["Home", "Away"]]
        draw_counts = pd.concat(
            [draw_clubs["Home"], draw_clubs["Away"]], ignore_index=True
        )
        draw_counts = draw_counts.value_counts().reindex(df["TEAM"], fill_value=0)

        df["D"] = draw_counts.values
        return df

    def __calculate_pts(self, df: pd.DataFrame) -> pd.DataFrame:
        df["PTS"] = (df["W"] * 3) + df["D"]
        return df

    def __calculate_gf_ga_gd(
        self, df: pd.DataFrame, results_df: pd.DataFrame
    ) -> pd.DataFrame:
        results_df = results_df.loc[:, "Home":]
        melted = results_df.melt(
            value_vars=["Home", "Away"],
            var_name="Role",
            value_name="Team",
            ignore_index=True,
        )

        melted["GF"] = results_df.melt(value_vars=["Home Scores", "Away Scores"])[
            "value"
        ]
        melted["GA"] = results_df.melt(value_vars=["Away Scores", "Home Scores"])[
            "value"
        ]
        melted["GD"] = melted["GF"] - melted["GA"]

        result = (
            melted.groupby("Team")[["GF", "GA", "GD"]]
            .sum()
            .reindex(df["TEAM"], fill_value=0)
        )
        df["GF"] = result["GF"].values
        df["GA"] = result["GA"].values
        df["GD"] = result["GD"].values

        return df

    def __all_teams(
        self, df: pd.DataFrame, results_df: pd.DataFrame, fixtures_df: pd.DataFrame
    ) -> pd.DataFrame:
        all_teams = pd.concat(
            [results_df.loc[:, "Home"], fixtures_df.loc[:, "Home"]], ignore_index=True
        ).unique()

        df.loc[:, "TEAM"] = all_teams
        return df

    def __format_schedules(self, df: pd.DataFrame, is_results: bool) -> pd.DataFrame:
        df["Schedules"] = format_datetime(df["Schedules"], is_results)
        return df

    def __convert_score_types(self, df: pd.DataFrame) -> pd.DataFrame:
        if "Home Scores" in df.columns:
            df["Home Scores"] = df["Home Scores"].apply(int)
            df["Away Scores"] = df["Away Scores"].apply(int)
        return df

    def __format_data(self, dfs: dict[pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for df in dfs.values():
            is_results = "Postponed" not in df.columns
            df = self.__format_schedules(df, is_results)
            df = self.__convert_score_types(df)

        return dfs

    @property
    def results(self) -> dict[str, pd.DataFrame]:
        '''to return result df'''
        return self.__results_df

    @property
    def fixtures(self) -> dict[str, pd.DataFrame]:
        '''return fixtures df'''
        return self.__fixtures_df

    @property
    def standings(self) -> dict[str, pd.DataFrame]:
        '''return standings df'''
        return self.__standings_df
