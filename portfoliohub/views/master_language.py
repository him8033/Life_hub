from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import (Q, Case, When, Value, IntegerField,)

from life_hub.renderers import UserRenderer

from portfoliohub.models.master_language import MasterLanguage
from portfoliohub.models.profile_language import ProfileLanguage
from portfoliohub.serializers.master_language import (
    MasterLanguageSerializer
)
from portfoliohub.pagination import MasterLanguageAdminPagination
from portfoliohub.pagination import PublicMasterLanguagePagination


# ============================================
# PUBLIC LIST
# ============================================

class PublicMasterLanguageListAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = MasterLanguage.objects.filter(
            is_active=True
        )

        # =========================================
        # SEARCH
        # =========================================

        search = request.query_params.get(
            "search",
            ""
        ).strip()

        if search:

            queryset = (
                queryset.filter(
                    Q(name__icontains=search) |
                    Q(code__icontains=search) |
                    Q(slug__icontains=search)
                )
                .annotate(
                    search_rank=Case(

                        # Exact name
                        When(name__iexact=search, then=Value(1)),

                        # Exact code
                        When(code__iexact=search, then=Value(2)),

                        # Starts with name
                        When(name__istartswith=search, then=Value(3)),

                        # Starts with code
                        When(code__istartswith=search, then=Value(4)),

                        # Starts with slug
                        When(slug__istartswith=search, then=Value(5)),

                        # Contains name
                        When(name__icontains=search, then=Value(6)),

                        # Contains code
                        When(code__icontains=search, then=Value(7)),

                        # Contains slug
                        When(slug__icontains=search, then=Value(8)),

                        default=Value(9),
                        output_field=IntegerField(),
                    )
                )
                .order_by(
                    "search_rank",
                    "position",
                    "name"
                )
            )

        else:

            queryset = queryset.order_by(
                "position",
                "name"
            )

        # =========================================
        # PAGINATION
        # =========================================

        paginator = PublicMasterLanguagePagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self
        )

        serializer = MasterLanguageSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# ============================================
# ADMIN LIST + CREATE
# ============================================

class MasterLanguageAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = MasterLanguage.objects.all()

        # =========================================
        # SEARCH
        # =========================================

        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(slug__icontains=search)
            )

        # =========================================
        # FILTER
        # =========================================

        is_active = request.query_params.get("is_active")

        if is_active is not None:

            if is_active.lower() == "true":
                queryset = queryset.filter(
                    is_active=True
                )

            elif is_active.lower() == "false":
                queryset = queryset.filter(
                    is_active=False
                )

        # =========================================
        # SORTING
        # =========================================

        allowed_orderings = [
            "name",
            "-name",
            "position",
            "-position",
            "created_at",
            "-created_at",
        ]

        ordering = request.query_params.get(
            "ordering",
            "position"
        )

        if ordering not in allowed_orderings:
            ordering = "position"

        queryset = queryset.order_by(ordering)

        # =========================================
        # PAGINATION
        # =========================================

        paginator = MasterLanguageAdminPagination()

        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = MasterLanguageSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can create languages"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = MasterLanguageSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Language created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class MasterLanguageDetailAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, language_id):

        return get_object_or_404(
            MasterLanguage,
            masterlanguage_id=language_id
        )

    def get(self, request, language_id):

        language = self.get_object(language_id)

        serializer = MasterLanguageSerializer(
            language
        )

        return Response({
            "message": "Language fetched successfully",
            "data": serializer.data
        })

    def put(self, request, language_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can update languages"
            }, status=status.HTTP_403_FORBIDDEN)

        language = self.get_object(language_id)

        # Prevent inactive if already used
        if (
            request.data.get("is_active") is False
            or str(request.data.get("is_active")).lower() == "false"
        ):
            if ProfileLanguage.objects.filter(
                language=language
            ).exists():
                return Response({
                    "message": "This language is already assigned to one or more profiles and cannot be deactivated."
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = MasterLanguageSerializer(
            language,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Language updated successfully",
            "data": serializer.data
        })

    def delete(self, request, language_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can delete languages"
            }, status=status.HTTP_403_FORBIDDEN)

        language = self.get_object(language_id)

        if ProfileLanguage.objects.filter(language=language).exists():
            return Response({
                "message": "This language is already assigned to one or more profiles and cannot be deleted."
            }, status=status.HTTP_400_BAD_REQUEST)

        language.delete()

        return Response({
            "message": "Language deleted successfully"
        })
