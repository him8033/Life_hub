from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from locations.models import *
from locations.serializers import *
from life_hub.renderers import UserRenderer

# 1. Start here


class CountryAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = Country.objects.all().order_by('name')
        serializer = CountrySerializer(qs, many=True)
        return Response({
            "message": "Countries fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# 2. Filter by country_id


class StateAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        country_id = request.query_params.get('country_id')

        if not country_id:
            return Response(
                {"message": "country_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = State.objects.filter(country_id=country_id).order_by('name')
        serializer = StateSerializer(qs, many=True)
        return Response({
            "message": "States fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# 3. Filter by state_id


class DistrictAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        state_id = request.query_params.get('state_id')

        if not state_id:
            return Response(
                {"message": "state_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = District.objects.filter(state_id=state_id).order_by('name')
        serializer = DistrictSerializer(qs, many=True)
        return Response({
            "message": "Districts fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# 4. Filter by district_id


class SubDistrictAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        district_id = request.query_params.get('district_id')

        if not district_id:
            return Response(
                {"message": "district_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = SubDistrict.objects.filter(
            district_id=district_id).order_by('name')
        serializer = SubDistrictSerializer(qs, many=True)
        return Response({
            "message": "SubDistricts fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# 5. Filter by sub_district_id

class VillageAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]
    MAX_LIMIT = 1000

    def get(self, request):
        sub_district_id = request.query_params.get('sub_district_id')

        if not sub_district_id:
            return Response(
                {"message": "sub_district_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            limit = int(request.query_params.get('limit', 1000))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            return Response(
                {"message": "limit and offset must be integers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        limit = max(1, min(limit, self.MAX_LIMIT))
        offset = max(0, offset)

        qs = (
            Village.objects
            .filter(sub_district_id=sub_district_id)
            .order_by('name')
            .only('id', 'name', 'category', 'slug')
        )

        villages = qs[offset:offset + limit]
        has_more = qs[offset + limit: offset + limit + 1].exists()

        serializer = VillageSerializer(villages, many=True)

        return Response({
            "message": "Villages fetched successfully",
            "data": {
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
                "results": serializer.data
            }
        }, status=status.HTTP_200_OK)


# 6. Search by Pincode OR Filter by Village

class PincodeAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        search = request.query_params.get('search')
        village_id = request.query_params.get('village_id')

        if not search and not village_id:
            return Response(
                {"message": "search or village_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = (
            Pincode.objects
            .select_related(
                'village',
                'village__sub_district',
                'village__sub_district__district',
                'village__sub_district__district__state',
                'village__sub_district__district__state__country',
            )
        )

        if search:
            qs = qs.filter(pincode__icontains=search)

        if village_id:
            qs = qs.filter(village_id=village_id)

        qs = qs[:1000]  # HARD LIMIT

        serializer = PincodeSerializer(qs, many=True)
        return Response({
            "message": "Pincodes fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
