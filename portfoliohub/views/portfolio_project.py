from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from life_hub.renderers import UserRenderer

from portfoliohub.models.portfolio_project import PortfolioProject
from portfoliohub.models.profile_snapshot import ProfileSnapshot

from portfoliohub.serializers.portfolio_project import (
    PortfolioProjectSerializer
)

import copy


# ============================================
# LIST + CREATE
# ============================================

class PortfolioProjectAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):

        portfolios = PortfolioProject.objects.filter(
            user=request.user
        ).select_related("profile_snapshot")

        serializer = PortfolioProjectSerializer(
            portfolios,
            many=True
        )

        return Response({
            "message": "Portfolio projects fetched successfully",
            "data": serializer.data
        })

    def post(self, request):

        serializer = PortfolioProjectSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Portfolio project created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class PortfolioProjectDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, request, portfolio_id):

        return get_object_or_404(
            PortfolioProject,
            portfolio_id=portfolio_id,
            user=request.user
        )

    def get(self, request, portfolio_id):

        portfolio = self.get_object(
            request,
            portfolio_id
        )

        serializer = PortfolioProjectSerializer(
            portfolio
        )

        return Response({
            "message": "Portfolio fetched successfully",
            "data": serializer.data
        })

    def put(self, request, portfolio_id):

        portfolio = self.get_object(
            request,
            portfolio_id
        )

        serializer = PortfolioProjectSerializer(
            portfolio,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Portfolio updated successfully",
            "data": serializer.data
        })

    def delete(self, request, portfolio_id):

        portfolio = self.get_object(
            request,
            portfolio_id
        )

        portfolio.delete()

        return Response({
            "message": "Portfolio deleted successfully"
        })


# ============================================
# DUPLICATE
# ============================================

class PortfolioProjectDuplicateAPIView(APIView):

    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, portfolio_id):

        portfolio = get_object_or_404(
            PortfolioProject,
            portfolio_id=portfolio_id,
            user=request.user
        )

        old_snapshot = portfolio.profile_snapshot

        # DUPLICATE SNAPSHOT
        new_snapshot = copy.copy(old_snapshot)

        new_snapshot.id = None
        new_snapshot.profile_snapshot_id = None

        new_snapshot.title = f"{old_snapshot.title} Copy"

        new_snapshot.source_profile = old_snapshot
        new_snapshot.version = old_snapshot.version + 1

        new_snapshot.save()

        # CREATE NEW PORTFOLIO
        new_portfolio = PortfolioProject.objects.create(
            user=request.user,
            profile_snapshot=new_snapshot,
            title=f"{portfolio.title} Copy",
            slug=f"{portfolio.slug}-copy",
            theme_key=portfolio.theme_key,
            custom_domain=None,
            seo_title=portfolio.seo_title,
            seo_description=portfolio.seo_description,
            hero_title=portfolio.hero_title,
            hero_subtitle=portfolio.hero_subtitle,
            is_public=False,
        )

        serializer = PortfolioProjectSerializer(
            new_portfolio
        )

        return Response({
            "message": "Portfolio duplicated successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# PUBLIC PORTFOLIO
# ============================================

class PublicPortfolioProjectAPIView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request, slug):

        portfolio = get_object_or_404(
            PortfolioProject,
            slug=slug,
            is_public=True
        )

        PORTFOLIO.SNAPSHOT.VIEW_count += 1
        portfolio.save()

        serializer = PortfolioProjectSerializer(
            portfolio
        )

        return Response({
            "message": "Public portfolio fetched successfully",
            "data": serializer.data
        })
