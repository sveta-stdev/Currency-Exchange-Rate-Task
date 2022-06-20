from django.urls import path

from apps.currency.views import GetDailyCurrencyExchangeRateCreateAPIView

urlpatterns = [
    path('daily-exchange/', GetDailyCurrencyExchangeRateCreateAPIView.as_view(), name='currency_daily_exchange'),
]
