# portfoliohub/services/builder_utils.py

class BuilderUtils:

    @staticmethod
    def format_date(value):

        if not value:
            return None

        return value.isoformat()

    @staticmethod
    def get_file_url(file_field):

        if not file_field:
            return None

        return file_field.url
