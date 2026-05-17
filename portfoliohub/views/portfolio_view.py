from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer

from portfoliohub.models.portfolio_project import (
    PortfolioProject
)

from portfoliohub.models.portfolio_view import (
    PortfolioView
)

from portfoliohub.serializers.portfolio_view import (
    PortfolioViewSerializer
)


# ============================================
# TRACK PORTFOLIO VIEW
# ============================================

class PortfolioViewTrackAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request, portfolio_id):

        portfolio = get_object_or_404(
            PortfolioProject,
            portfolio_id=portfolio_id,
            is_public=True
        )

        # SIMPLE IP DETECTION
        ip_address = request.META.get(
            "REMOTE_ADDR",
            ""
        )

        country = request.data.get("country", "")

        PortfolioView.objects.create(
            portfolio=portfolio,
            ip_address=ip_address,
            country=country
        )

        # INCREMENT COUNTER
        PORTFOLIO.SNAPSHOT.VIEW_count += 1
        portfolio.save()

        return Response({
            "message": "Portfolio view tracked successfully"
        })


# ============================================
# PORTFOLIO ANALYTICS
# ============================================

class PortfolioAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, portfolio_id):

        portfolio = get_object_or_404(
            PortfolioProject,
            portfolio_id=portfolio_id,
            user=request.user
        )

        views = PortfolioView.objects.filter(
            portfolio=portfolio
        ).order_by("-viewed_at")

        serializer = PortfolioViewSerializer(
            views,
            many=True
        )

        return Response({
            "message": "Portfolio analytics fetched successfully",
            "total_views": views.count(),
            "portfolio_view_count": PORTFOLIO.SNAPSHOT.VIEW_count,
            "data": serializer.data
        })
