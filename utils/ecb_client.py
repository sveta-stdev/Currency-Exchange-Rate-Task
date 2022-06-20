import requests

from utils.basic_utils import DatetimeUtil


class EuropeanCentralBankClient:
    ECB_EXR_BASE_URL = "https://sdw-wsrest.ecb.europa.eu/service/data/EXR/"

    FREQUENCY_DAILY = 'D'
    EXCHANGE_TYPE_FOREIGN_CODE = 'SP00'
    SERIES_VARIATION_AVERAGE = 'A'

    def __init__(self, **kwargs):
        self.from_currency = kwargs.get('from_currency')
        self.to_currency = kwargs.get('to_currency')
        self.from_date = kwargs.get('from_date')
        self.to_date = kwargs.get('to_date')

    @property
    def _date_range(self):
        from_date = DatetimeUtil.str_to_date(self.from_date)
        to_date = DatetimeUtil.str_to_date(self.to_date)

        return DatetimeUtil.date_range_between_two_dates(from_date, to_date)

    @property
    def _daily_exchange_url_parameters(self):
        return {
            'startPeriod': self.from_date,
            'endPeriod': self.to_date,
        }

    @classmethod
    def _get_request(cls, url, params=None):
        try:
            response = requests.get(url, params=params, headers={'Accept': 'application/json'})
            return response
        except requests.JSONDecodeError:
            pass

    def _get_exchange_dates_from_api(self, response):
        return [data['name'] for data in response['structure']['dimensions']['observation'][0]['values']]

    def _get_exchange_rates_from_api(self, response):
        return response['dataSets'][0]['series']['0:0:0:0:0']['observations']

    def _get_daily_exchange_url(self, to_currency):
        """
        The from_currency should be EUR, otherwise the API doesn't found data
        """
        ecb_exp_url_params = '{frequency}.{to_currency}.{from_currency}.{exchange_type}.{series_variation}'.format(
            frequency=self.FREQUENCY_DAILY,
            to_currency=to_currency,
            from_currency='EUR',
            exchange_type=self.EXCHANGE_TYPE_FOREIGN_CODE,
            series_variation=self.SERIES_VARIATION_AVERAGE)

        return self.ECB_EXR_BASE_URL + ecb_exp_url_params

    def _get_exchange_rate_from_exr_rates(self, index, exr_rates, extra_exr_rates=None):
        if extra_exr_rates:
            return extra_exr_rates[str(index)][0] / exr_rates[str(index)][0]

        return exr_rates[str(index)][0] if self.from_currency == 'EUR' else 1 / exr_rates[str(index)][0]

    def _get_previous_day_exchange_rate(self, date_str):
        previous_day_date = DatetimeUtil.previous_day(date_str)
        previous_day_str = DatetimeUtil.datetime_to_str(previous_day_date)

        if self.from_currency == 'EUR' or self.to_currency == 'EUR':
            to_currency = self.to_currency if self.from_currency == 'EUR' else self.from_currency
            response = self._get_request(url=self._get_daily_exchange_url(to_currency=to_currency),
                                         params={'startPeriod': previous_day_str, 'endPeriod': previous_day_str})

            if response and response.content:
                response_data = response.json()
                exchange_rates_data = self._get_exchange_rates_from_api(response_data)

                return self._get_exchange_rate_from_exr_rates(0, exchange_rates_data)

        else:
            from_response = self._get_request(url=self._get_daily_exchange_url(to_currency=self.from_currency),
                                              params={'startPeriod': previous_day_str, 'endPeriod': previous_day_str})
            to_response = self._get_request(url=self._get_daily_exchange_url(to_currency=self.to_currency),
                                            params={'startPeriod': previous_day_str, 'endPeriod': previous_day_str})

            if from_response and to_response and from_response.content and to_response.content:
                from_response_data = from_response.json()
                to_response_data = to_response.json()

                from_exchange_rates_data = self._get_exchange_rates_from_api(from_response_data)
                to_exchange_rates_data = self._get_exchange_rates_from_api(to_response_data)

                return self._get_exchange_rate_from_exr_rates(0, from_exchange_rates_data, to_exchange_rates_data)

        return self._get_previous_day_exchange_rate(previous_day_str)

    def _get_exchange_rates_data_from_api(self, response, extra_response=None):
        """
        If one of the currencies isn't EUR, an extra API call is needed for conversion.
        In these cases, 'extra_' prefix variables are used.
        """
        data, exchange_date_ranges = [], []
        exchange_rates, extra_exchange_rates = {}, {}
        if response.content:
            response_data = response.json()
            exchange_date_ranges = self._get_exchange_dates_from_api(response_data)
            exchange_rates = self._get_exchange_rates_from_api(response_data)

        if extra_response and extra_response.content:
            extra_response_data = extra_response.json()
            extra_exchange_rates = self._get_exchange_rates_from_api(extra_response_data)

        date_ranges = self._date_range
        for date_range_index, date_range_str in enumerate(date_ranges):
            daily_exchange_rate = 0
            try:
                if date_range_str in exchange_date_ranges and exchange_rates:
                    index_in_range = exchange_date_ranges.index(date_range_str)
                    daily_exchange_rate = self._get_exchange_rate_from_exr_rates(index_in_range,
                                                                                 exchange_rates,
                                                                                 extra_exchange_rates)

                elif date_range_index != 0 and data:
                    # Gets previous day exchange rate from data
                    daily_exchange_rate = data[date_range_index-1]['daily_exchange_rate']

                else:
                    # Gets previous day exchange rate via API Call
                    daily_exchange_rate = self._get_previous_day_exchange_rate(date_range_str)

            except (IndexError, KeyError):
                pass

            data.append({
                'date': date_range_str,
                'daily_exchange_rate': daily_exchange_rate,
            })

        return data

    def get_daily_exchange_rates(self):
        data = []
        if self.from_currency == 'EUR' or self.to_currency == 'EUR':
            to_currency = self.to_currency if self.from_currency == 'EUR' else self.from_currency
            response = self._get_request(url=self._get_daily_exchange_url(to_currency=to_currency),
                                         params=self._daily_exchange_url_parameters)

            if response and response.status_code == 200:
                data = self._get_exchange_rates_data_from_api(response)
        else:
            from_response = self._get_request(url=self._get_daily_exchange_url(to_currency=self.from_currency),
                                              params=self._daily_exchange_url_parameters)
            to_response = self._get_request(url=self._get_daily_exchange_url(to_currency=self.to_currency),
                                            params=self._daily_exchange_url_parameters)

            if from_response and to_response and from_response.status_code == 200 and to_response.status_code == 200:
                data = self._get_exchange_rates_data_from_api(from_response, to_response)

        return data
