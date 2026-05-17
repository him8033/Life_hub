from rest_framework import serializers
from django.shortcuts import get_object_or_404

import cloudinary.uploader

from portfoliohub.models.master_skill import MasterSkill
from portfoliohub.models.skill_category import SkillCategory


class MasterSkillSerializer(serializers.ModelSerializer):

    category_id = serializers.CharField(write_only=True)

    image = serializers.ImageField(
        write_only=True,
        required=False
    )

    remove_image = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )

    category_value = serializers.CharField(
        source="category.skillcategory_id",
        read_only=True
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MasterSkill

        fields = [
            "masterskill_id",

            "category",
            "category_id",
            "category_value",
            "category_name",

            "name",
            "slug",

            "icon",

            "image",
            "image_url",
            "remove_image",

            "description",

            "public_id",

            "is_active",
            "priority",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "masterskill_id",
            "category",
            "category_name",
            "image_url",
            "public_id",
            "created_at",
            "updated_at",
        ]

    # ============================================
    # IMAGE URL
    # ============================================

    def get_image_url(self, obj):

        from cloudinary.utils import cloudinary_url

        if not obj.public_id:
            return None

        url, _ = cloudinary_url(
            obj.public_id,
            width=200,
            height=200,
            crop="fit",
            quality="auto",
            fetch_format="auto"
        )

        return url

    # ============================================
    # CREATE
    # ============================================

    def create(self, validated_data):

        category_id = validated_data.pop("category_id")

        image = validated_data.pop("image", None)

        validated_data.pop("remove_image", False)

        category = get_object_or_404(
            SkillCategory,
            skillcategory_id=category_id,
            is_active=True
        )

        skill = MasterSkill.objects.create(
            category=category,
            **validated_data
        )

        # IMAGE UPLOAD
        if image:

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/master-skills/{skill.slug}",
                resource_type="image",
            )

            skill.image = upload["public_id"]
            skill.public_id = upload["public_id"]

            skill.save()

        return skill

    # ============================================
    # UPDATE
    # ============================================

    def update(self, instance, validated_data):

        category_id = validated_data.pop(
            "category_id",
            None
        )

        image = validated_data.pop(
            "image",
            None
        )

        remove_image = validated_data.pop(
            "remove_image",
            False
        )

        # CATEGORY UPDATE
        if category_id:

            category = get_object_or_404(
                SkillCategory,
                skillcategory_id=category_id,
                is_active=True
            )

            instance.category = category

        # NORMAL FIELD UPDATE
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # REMOVE IMAGE
        if remove_image:

            if instance.public_id:
                cloudinary.uploader.destroy(
                    instance.public_id
                )

            instance.image = None
            instance.public_id = None

        # REPLACE IMAGE
        elif image:

            if instance.public_id:
                cloudinary.uploader.destroy(
                    instance.public_id
                )

            upload = cloudinary.uploader.upload(
                image,
                folder=f"lifehub/master-skills/{instance.slug}",
                resource_type="image",
            )

            instance.image = upload["public_id"]
            instance.public_id = upload["public_id"]

        instance.save()

        return instance
