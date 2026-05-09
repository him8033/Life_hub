from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404

from life_hub.renderers import UserRenderer

from portfoliohub.models.project_skill import ProjectSkill
from portfoliohub.models.profile_project import ProfileProject

from portfoliohub.serializers.project_skill import (
    ProjectSkillSerializer
)


# ============================================
# LIST + CREATE
# ============================================

class ProjectSkillAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, project_id):

        project = get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

        skills = ProjectSkill.objects.filter(
            project=project
        ).select_related(
            "skill",
            "skill__category"
        )

        serializer = ProjectSkillSerializer(
            skills,
            many=True
        )

        return Response({
            "message": "Project skills fetched successfully",
            "data": serializer.data
        })

    def post(self, request, project_id):

        data = request.data.copy()
        data["project_id"] = project_id

        serializer = ProjectSkillSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Skill added to project successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# DELETE
# ============================================

class ProjectSkillDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def delete(self, request, project_id, skill_id):

        project = get_object_or_404(
            ProfileProject,
            profileproject_id=project_id,
            profile_snapshot__user=request.user
        )

        skill = get_object_or_404(
            ProjectSkill,
            project=project,
            skill__masterskill_id=skill_id
        )

        skill.delete()

        return Response({
            "message": "Skill removed from project successfully"
        })
