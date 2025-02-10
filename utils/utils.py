'''utils module'''

from datetime import datetime
from itertools import chain
import pandas as pd

def format_datetime(series: pd.Series, is_results: bool) -> pd.Series:
    '''to formatting date time'''
    schedules = [schedule.split(' ') for schedule in series]

    current_date = datetime.now()
    current_year = current_date.year

    for schedule in schedules:
        schedule[0] = schedule[0].removesuffix('.')

        day, month = map(int, schedule[0].split('.'))
        hour, minute = map(int, schedule[1].split(':'))

        date = datetime(current_year, month, day)

        if is_results and date > current_date:
            year = current_year - 1
            date = datetime(year, month, day)
            schedule[0] = date
        else:
            schedule[0] = date

        schedule[0] = schedule[0].replace(hour=hour, minute=minute)
        schedule[0] = schedule[0].strftime('%d/%m/%Y %H:%M')

        schedule.pop()

    series = pd.Series(list(chain.from_iterable(schedules)))
    return series
