from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from rest_framework_csv.renderers import CSVRenderer

from apps.currency.serializers import GetDailyCurrencyExchangeRateSerializer
from utils.ecb_client import EuropeanCentralBankClient


class GetDailyCurrencyExchangeRateCreateAPIView(CreateAPIView):
    serializer_class = GetDailyCurrencyExchangeRateSerializer
    renderer_classes = (JSONRenderer, CSVRenderer)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        central_bank_client = EuropeanCentralBankClient(**serializer.data)
        result = central_bank_client.get_daily_exchange_rates()
        if not result:
            return Response({'error_message': 'Something went wrong. Please try again'}, status.HTTP_400_BAD_REQUEST)

        return Response(result, status.HTTP_200_OK)
