from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from life_hub.renderers import UserRenderer
from portfoliohub.models.skill_category import SkillCategory
from portfoliohub.serializers.skill_category import SkillCategorySerializer
from portfoliohub.pagination import CategoryOffsetPagination


# ============================================
# PUBLIC LIST (ACTIVE ONLY)
# ============================================

class PublicSkillCategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):

        categories = SkillCategory.objects.filter(
            is_active=True
        ).order_by("position")

        serializer = SkillCategorySerializer(
            categories,
            many=True
        )

        return Response({
            "message": "Skill categories fetched successfully",
            "data": serializer.data
        })

# ============================================
# ADMIN LIST
# ============================================


class SkillCategoryListAPIView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]

    def get(self, request):

        queryset = SkillCategory.objects.all()

        # SEARCH
        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search)
            )

        # FILTER
        is_active = request.query_params.get("is_active")

        if is_active is not None:

            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        # Sorting
        allowed_orderings = [
            "position",
            "-position",
            "name",
            "-name",
        ]

        ordering = request.query_params.get(
            "ordering",
            "position"
        )

        if ordering not in allowed_orderings:
            ordering = "position"

        queryset = queryset.order_by(ordering)

        # -------------------------
        # Offset Pagination
        # -------------------------
        paginator = CategoryOffsetPagination()

        # IMPORTANT: override paginator ordering
        paginator.ordering = ordering

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self
        )

        serializer = SkillCategorySerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# ============================================
# ADMIN CREATE
# ============================================

class SkillCategoryCreateAPIView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = SkillCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Skill category created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# ADMIN UPDATE + DELETE
# ============================================

class SkillCategoryDetailAPIView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [UserRenderer]

    def get_object(self, category_id):
        return get_object_or_404(
            SkillCategory,
            skillcategory_id=category_id
        )

    def get(self, request, category_id):

        category = self.get_object(category_id)

        serializer = SkillCategorySerializer(category)

        return Response({
            "message": "Skill category fetched successfully",
            "data": serializer.data
        })

    def put(self, request, category_id):
        category = self.get_object(category_id)

        serializer = SkillCategorySerializer(
            category,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Skill category updated successfully",
            "data": serializer.data
        })

    def delete(self, request, category_id):
        category = self.get_object(category_id)
        category.delete()

        return Response({
            "message": "Skill category deleted successfully"
        })
