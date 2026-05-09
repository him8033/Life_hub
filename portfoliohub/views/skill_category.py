from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from life_hub.renderers import UserRenderer
from portfoliohub.models.skill_category import SkillCategory
from portfoliohub.serializers.skill_category import SkillCategorySerializer


# ============================================
# PUBLIC LIST (FOR DROPDOWN)
# ============================================

class SkillCategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        categories = SkillCategory.objects.filter(
            is_active=True
        ).order_by("position")

        serializer = SkillCategorySerializer(categories, many=True)

        return Response({
            "message": "Skill categories fetched successfully",
            "data": serializer.data
        })


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
        return SkillCategory.objects.get(
            skillcategory_id=category_id
        )

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
