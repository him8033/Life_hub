from rest_framework import serializers
from .models import Country, State, District, SubDistrict, Village, Pincode


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso_code', 'slug']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'type', 'slug']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'slug']


class SubDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDistrict
        fields = ['id', 'name', 'slug']


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['id', 'name', 'category', 'slug']


class PincodeSerializer(serializers.ModelSerializer):
    village_name = serializers.CharField(source='village.name', read_only=True)
    village_category = serializers.CharField(source='village.category', read_only=True)
    sub_district_name = serializers.CharField(
        source='village.sub_district.name', read_only=True
    )
    district_name = serializers.CharField(
        source='village.sub_district.district.name', read_only=True
    )
    state_name = serializers.CharField(
        source='village.sub_district.district.state.name', read_only=True
    )
    country_name = serializers.CharField(
        source='village.sub_district.district.state.country.name', read_only=True
    )

    class Meta:
        model = Pincode
        fields = [
            'id',
            'pincode',
            'village',
            'village_name',
            'village_category',
            'sub_district_name',
            'district_name',
            'state_name',
            'country_name',
        ]
