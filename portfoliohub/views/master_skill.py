from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser
)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Case, When, Value, IntegerField

import cloudinary.uploader
from life_hub.renderers import UserRenderer
from portfoliohub.models.master_skill import MasterSkill
from portfoliohub.serializers.master_skill import MasterSkillSerializer
from portfoliohub.pagination import MasterSkillAdminPagination
from portfoliohub.pagination import PublicMasterSkillPagination


class PublicMasterSkillListAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = (
            MasterSkill.objects.filter(
                is_active=True
            )
            .select_related("category")
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
                    Q(slug__icontains=search)
                )
                .annotate(
                    search_rank=Case(
                        # Exact name
                        When(name__iexact=search, then=Value(1)),

                        # Starts with name
                        When(name__istartswith=search, then=Value(2)),

                        # Contains in name
                        When(name__icontains=search, then=Value(3)),

                        # Starts with slug
                        When(slug__istartswith=search, then=Value(4)),

                        # Contains in slug
                        When(slug__icontains=search, then=Value(5)),

                        default=Value(6),
                        output_field=IntegerField(),
                    )
                )
                .order_by(
                    "search_rank",
                    "name"
                )
            )

        else:

            # Initial suggestions
            queryset = queryset.order_by(
                "-priority",
                "name"
            )

        # =========================================
        # PAGINATION
        # =========================================

        paginator = PublicMasterSkillPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self
        )

        serializer = MasterSkillSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# ============================================
# LIST + CREATE
# ============================================

class MasterSkillAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = MasterSkill.objects.select_related("category").all()

        # =========================================
        # SEARCH
        # =========================================
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(category__name__icontains=search)
            )

        # =========================================
        # FILTERS
        # =========================================
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category__skillcategory_id=category_id)

        # =========================================
        # SORTING
        # =========================================
        allowed_orderings = [
            "name",
            "-name",
            "priority",
            "-priority",
            "created_at",
            "-created_at",
            "category__position",
            "-category__position",
        ]

        ordering = request.query_params.get("ordering", "priority")

        if ordering not in allowed_orderings:
            ordering = "priority"

        queryset = queryset.order_by(ordering)

        # =========================================
        # PAGINATION
        # =========================================
        paginator = MasterSkillAdminPagination()

        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = MasterSkillSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):

        # ADMIN ONLY
        if not request.user.is_admin:
            return Response({
                "message": "Only admin can create master skills"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = MasterSkillSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Master skill created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DETAIL + UPDATE + DELETE
# ============================================

class MasterSkillDetailAPIView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, skill_id):

        return get_object_or_404(
            MasterSkill,
            masterskill_id=skill_id
        )

    def get(self, request, skill_id):

        skill = self.get_object(skill_id)

        serializer = MasterSkillSerializer(skill)

        return Response({
            "message": "Master skill fetched successfully",
            "data": serializer.data
        })

    def put(self, request, skill_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can update master skills"
            }, status=status.HTTP_403_FORBIDDEN)

        skill = self.get_object(skill_id)

        serializer = MasterSkillSerializer(
            skill,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Master skill updated successfully",
            "data": serializer.data
        })

    def delete(self, request, skill_id):

        if not request.user.is_admin:
            return Response({
                "message": "Only admin can delete master skills"
            }, status=status.HTTP_403_FORBIDDEN)

        skill = self.get_object(skill_id)

        if skill.public_id:
            cloudinary.uploader.destroy(skill.public_id)

        skill.delete()

        return Response({
            "message": "Master skill deleted successfully"
        })
