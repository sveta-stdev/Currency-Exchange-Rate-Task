import datetime

from rest_framework import serializers

from apps.currency.choices import CURRENCIES_CHOICES


class GetDailyCurrencyExchangeRateSerializer(serializers.Serializer):
    from_currency = serializers.ChoiceField(choices=CURRENCIES_CHOICES, required=True)
    to_currency = serializers.ChoiceField(choices=CURRENCIES_CHOICES, required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)

    def validate_from_date(self, value):
        if value > datetime.datetime.now().date():
            raise serializers.ValidationError("Incorrect from date")

        return value

    def validate_to_date(self, value):
        if value > datetime.datetime.now().date():
            raise serializers.ValidationError("Incorrect to date")

        return value

    def validate(self, attrs):
        if attrs.get('from_date') > attrs.get('to_date'):
            raise serializers.ValidationError("The from date cannot be after the to date.")

        if attrs.get('from_currency') == attrs.get('to_currency'):
            raise serializers.ValidationError("The from currency cannot be the same as to currency.")

        return attrs
