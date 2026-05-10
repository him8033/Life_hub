from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)
from rest_framework import status
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer
from portfoliohub.models.portfolio_theme import PortfolioTheme
from portfoliohub.serializers.portfolio_theme import (
    PortfolioThemeSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class PortfolioThemeAPIView(APIView):
    renderer_classes = [UserRenderer]

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAuthenticated()]

        return [AllowAny()]

    # LIST
    def get(self, request):

        themes = PortfolioTheme.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = PortfolioThemeSerializer(
            themes,
            many=True,
            context={"request": request}
        )

        return Response({
            "message": "Portfolio themes fetched successfully",
            "data": serializer.data
        })

    # CREATE (ADMIN)
    def post(self, request):

        serializer = PortfolioThemeSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Portfolio theme created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL
# ============================================

class PortfolioThemeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, theme_id):

        return get_object_or_404(
            PortfolioTheme,
            theme_id=theme_id
        )

    def get(self, request, theme_id):

        theme = self.get_object(theme_id)

        serializer = PortfolioThemeSerializer(
            theme,
            context={"request": request}
        )

        return Response({
            "message": "Portfolio theme fetched successfully",
            "data": serializer.data
        })

    def put(self, request, theme_id):

        theme = self.get_object(theme_id)

        serializer = PortfolioThemeSerializer(
            theme,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Portfolio theme updated successfully",
            "data": serializer.data
        })

    def delete(self, request, theme_id):

        theme = self.get_object(theme_id)
        theme.delete()

        return Response({
            "message": "Portfolio theme deleted successfully"
        })
