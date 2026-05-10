from rest_framework import serializers

from portfoliohub.models.portfolio_view import PortfolioView


class PortfolioViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = PortfolioView

        fields = [
            "id",
            "ip_address",
            "country",
            "viewed_at",
        ]
