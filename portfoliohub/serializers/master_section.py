# portfoliohub/serializers/master_section.py

from rest_framework import serializers

from portfoliohub.models.master_section import (
    MasterSection
)


class MasterSectionSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = MasterSection

        fields = [
            "mastersection_id",
            "name",
            "key",
            "description",
            "is_active",
        ]
