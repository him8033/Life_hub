from django.shortcuts import get_object_or_404
from django.db.models import Q

import cloudinary.uploader

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.portfolio_theme import PortfolioTheme
from portfoliohub.serializers.portfolio_theme import (
    PortfolioThemeSerializer
)
from portfoliohub.pagination import (
    PortfolioThemeAdminPagination
)


# ============================================
# PUBLIC LIST
# ============================================

class PublicPortfolioThemeListAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = PortfolioTheme.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = PortfolioThemeSerializer(
            queryset,
            many=True
        )

        return Response({
            "message": "Portfolio themes fetched successfully",
            "data": serializer.data
        })


# ============================================
# ADMIN LIST + CREATE
# ============================================

class PortfolioThemeAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = PortfolioTheme.objects.all()

        # SEARCH

        search = request.query_params.get("search")

        if search:

            queryset = queryset.filter(
                Q(name__icontains=search)
            )

        # FILTER ACTIVE

        is_active = request.query_params.get(
            "is_active"
        )

        if is_active is not None:

            if is_active.lower() == "true":
                queryset = queryset.filter(
                    is_active=True
                )

            elif is_active.lower() == "false":
                queryset = queryset.filter(
                    is_active=False
                )

        # FILTER PREMIUM

        is_premium = request.query_params.get(
            "is_premium"
        )

        if is_premium is not None:

            if is_premium.lower() == "true":
                queryset = queryset.filter(
                    is_premium=True
                )

            elif is_premium.lower() == "false":
                queryset = queryset.filter(
                    is_premium=False
                )

        # ORDERING

        allowed_orderings = [
            "name",
            "-name",
            "created_at",
            "-created_at",
        ]

        ordering = request.query_params.get(
            "ordering",
            "name"
        )

        if ordering not in allowed_orderings:
            ordering = "name"

        queryset = queryset.order_by(ordering)

        # PAGINATION

        paginator = PortfolioThemeAdminPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self
        )

        serializer = PortfolioThemeSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can create themes"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioThemeSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Portfolio theme created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class PortfolioThemeDetailAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, theme_id):

        return get_object_or_404(
            PortfolioTheme,
            theme_id=theme_id
        )

    def get(self, request, theme_id):

        theme = self.get_object(theme_id)

        serializer = PortfolioThemeSerializer(
            theme
        )

        return Response({
            "message": "Portfolio theme fetched successfully",
            "data": serializer.data
        })

    def put(self, request, theme_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can update themes"
            }, status=status.HTTP_403_FORBIDDEN)

        theme = self.get_object(theme_id)

        serializer = PortfolioThemeSerializer(
            theme,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Portfolio theme updated successfully",
            "data": serializer.data
        })

    def delete(self, request, theme_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can delete themes"
            }, status=status.HTTP_403_FORBIDDEN)

        theme = self.get_object(theme_id)

        if theme.public_id:

            cloudinary.uploader.destroy(
                theme.public_id
            )

        theme.delete()

        return Response({
            "message": "Portfolio theme deleted successfully"
        })
