# travelhub/serializers/spot_category_read.py

from rest_framework import serializers
from travelhub.models import SpotCategory


class SpotCategoryReadSerializer(serializers.ModelSerializer):
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
