from rest_framework import serializers
from .models import TravelSpot


class TravelSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelSpot
        fields = "__all__"
        read_only_fields = (
            "created_by", "updated_by",
            "created_at", "updated_at", "deleted_at"
        )

    def create(self, validated_data):
        # Automatically set the logged-in user as created_by & updated_by
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Automatically set updated_by to logged-in user
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)
