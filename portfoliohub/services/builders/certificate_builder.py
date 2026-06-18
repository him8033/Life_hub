# portfoliohub/services/builders/certificate_builder.py

from portfoliohub.services.builder_utils import (
    BuilderUtils
)


class CertificateBuilder:

    @staticmethod
    def build(snapshot):

        certificates = []

        for item in snapshot.certificates.all().order_by(
            "position"
        ):

            certificates.append({
                "profilecertificate_id":
                    item.profilecertificate_id,

                "title":
                    item.title,

                "issued_by":
                    item.issued_by,

                "issued_date":
                    BuilderUtils.format_date(
                        item.issued_date
                    ),

                "expiry_date":
                    BuilderUtils.format_date(
                        item.expiry_date
                    ),

                "credential_id":
                    item.credential_id,

                "certificate_url":
                    item.certificate_url,

                "description":
                    item.description,

                "position":
                    item.position,

                "image":
                    BuilderUtils.get_file_url(
                        item.image
                    ),
            })

        return certificates
