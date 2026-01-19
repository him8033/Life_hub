from rest_framework import serializers
from travelhub.models import SpotCategory


class SpotCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotCategory
        fields = [
            "id",
            "spotcategory_id",
            "name",
            "slug",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "spotcategory_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at"
        ]

    def create(self, validated_data):
        # Automatically set the logged-in user as created_by & updated_by
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        validated_data["updated_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Automatically set updated_by to logged-in user
        request = self.context.get("request")
        instance.updated_by = request.user
        return super().update(instance, validated_data)
