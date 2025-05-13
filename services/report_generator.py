from datetime import date, timedelta

from services.logging import logger


def get_weeks_range(count):
    today = date.today()
    previous_monday = today - timedelta(days=today.weekday()) - timedelta(days=7)
    weeks_range = []
    for i in range(count):
        week_start = previous_monday - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        weeks_range.append(f'{week_start.strftime("%d.%m.%Y")}-{week_end.strftime("%d.%m.%Y")}')

    return weeks_range