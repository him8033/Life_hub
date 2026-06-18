# portfoliohub/services/builders/template_builder.py

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class TemplateBuilder:

    @staticmethod
    def build(template):

        return {
            "template_id":
                template.template_id,

            "name":
                template.name,

            "key":
                template.key,

            "description":
                template.description,

            "preview_image":
                BuilderUtils.get_file_url(
                    template.preview_image
                ),

            "is_ats_friendly":
                template.is_ats_friendly,

            "is_premium":
                template.is_premium,
        }
