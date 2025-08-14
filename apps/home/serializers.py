from rest_framework import serializers

class PurchaseNumberSerializer(serializers.Serializer):
    """
    Serializer for the request body when purchasing a phone number.
    """
    number = serializers.CharField(help_text="The phone number to purchase in E.164 format.")
    country = serializers.CharField(required=False, help_text="The two-letter ISO country code (e.g., 'GB'). Required for countries that need an address.")
