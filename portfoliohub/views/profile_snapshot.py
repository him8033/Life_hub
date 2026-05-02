from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from life_hub.renderers import UserRenderer
from portfoliohub.models.profile_snapshot import ProfileSnapshot
from portfoliohub.serializers.profile_snapshot import ProfileSnapshotSerializer
from portfoliohub.pagination import SnapShotOffsetPagination

# ============================================
# SNAPSHOT LIST + CREATE
# ============================================


class ProfileSnapshotAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        queryset = ProfileSnapshot.objects.filter(
            user=request.user
        )

        # -------------------------
        # Filters
        # -------------------------
        visibility = request.query_params.get("visibility")
        # is_template = request.query_params.get("is_template")
        # is_public = request.query_params.get("is_public")
        search = request.query_params.get("search")

        if visibility:
            queryset = queryset.filter(visibility=visibility)

        # if is_template:
        #     queryset = queryset.filter(
        #         is_template=is_template.lower() == "true"
        #     )

        # if is_public:
        #     queryset = queryset.filter(
        #         is_public=is_public.lower() == "true"
        #     )

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(target_role__icontains=search) |
                Q(description__icontains=search)
            )

        # Avoid duplicates
        queryset = queryset.distinct()

        # -------------------------
        # Sorting
        # -------------------------
        allowed_orderings = [
            "title",
            "-title",
            "created_at",
            "-created_at",
            # "updated_at",
            # "-updated_at",
            "version",
            "-version",
        ]

        ordering = request.query_params.get(
            "ordering",
            "-created_at"
        )

        if ordering not in allowed_orderings:
            ordering = "-created_at"

        queryset = queryset.order_by(ordering)

        # -------------------------
        # Cursor Pagination
        # -------------------------
        paginator = SnapShotOffsetPagination()

        # IMPORTANT: override paginator ordering
        paginator.ordering = ordering

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self
        )

        serializer = ProfileSnapshotSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = ProfileSnapshotSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Snapshot created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# ============================================
# SNAPSHOT DETAIL (GET / UPDATE / DELETE)
# ============================================

class ProfileSnapshotDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_object(self, user, snapshot_id):
        return get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=user
        )

    def get(self, request, snapshot_id):
        snapshot = self.get_object(request.user, snapshot_id)

        serializer = ProfileSnapshotSerializer(snapshot)

        return Response({
            "message": "Snapshot fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, snapshot_id):
        snapshot = self.get_object(request.user, snapshot_id)

        serializer = ProfileSnapshotSerializer(
            snapshot,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Snapshot updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, snapshot_id):
        snapshot = self.get_object(request.user, snapshot_id)
        snapshot.delete()

        return Response({
            "message": "Snapshot deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)


# ============================================
# SNAPSHOT DUPLICATE (CORE FEATURE)
# ============================================

class ProfileSnapshotDuplicateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, snapshot_id):
        snapshot = get_object_or_404(
            ProfileSnapshot,
            profile_snapshot_id=snapshot_id,
            user=request.user
        )

        new_snapshot = ProfileSnapshot.objects.create(
            user=request.user,
            title=f"{snapshot.title} Copy",
            target_role=snapshot.target_role,
            description=snapshot.description,
            source_profile=snapshot,
            version=snapshot.version + 1
        )

        return Response({
            "message": "Snapshot duplicated successfully",
            "data": ProfileSnapshotSerializer(new_snapshot).data
        }, status=status.HTTP_201_CREATED)
