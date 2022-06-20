import datetime


class DatetimeUtil:
    @classmethod
    def str_to_date(cls, _date: str) -> datetime.date:
        return datetime.datetime.strptime(_date, "%Y-%m-%d").date()

    @classmethod
    def str_to_datetime(cls, _date: str) -> datetime:
        return datetime.datetime.strptime(_date, "%Y-%m-%d")

    @classmethod
    def datetime_to_str(cls, _date: datetime) -> str:
        return datetime.datetime.strftime(_date, '%Y-%m-%d')

    @classmethod
    def date_range_between_two_dates(cls, start_date: datetime.date, end_date: datetime.date) -> list:
        date_delta = end_date - start_date
        date_range = [str(start_date + datetime.timedelta(days=day)) for day in range(date_delta.days + 1)]
        return date_range

    @classmethod
    def previous_day(cls, _date: str) -> datetime:
        return cls.str_to_datetime(_date) - datetime.timedelta(days=1)
