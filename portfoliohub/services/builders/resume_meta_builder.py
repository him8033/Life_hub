# portfoliohub/services/builders/resume_meta_builder.py


class ResumeMetaBuilder:

    @staticmethod
    def build(resume):

        return {
            "resume_id":
                resume.resume_id,

            "title":
                resume.title,

            "slug":
                resume.slug,

            "font_family":
                resume.font_family,

            "primary_color":
                resume.primary_color,

            "layout":
                resume.layout,

            "is_public":
                resume.is_public,

            "is_pdf_generated":
                resume.is_pdf_generated,
        }
