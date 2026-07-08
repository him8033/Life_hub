from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class PortfolioThemeBuilder:

    @staticmethod
    def build(theme):

        if not theme:
            return None

        return {
            "theme_id":
                theme.theme_id,

            "name":
                theme.name,

            "key":
                theme.key,

            "description":
                theme.description,

            "preview_image":
                BuilderUtils.get_file_url(
                    theme.preview_image
                ),

            "is_premium":
                theme.is_premium,
        }
