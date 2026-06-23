# portfoliohub/services/duplicate_modules/certificate_duplicate.py

from portfoliohub.models.profile_certificate import (
    ProfileCertificate
)
from life_hub.utils import generate_ulid_with_prefix


class CertificateDuplicate:

    @staticmethod
    def copy(source_snapshot, new_snapshot):

        certificates = source_snapshot.certificates.all()

        ProfileCertificate.objects.bulk_create([
            ProfileCertificate(
                profilecertificate_id=generate_ulid_with_prefix("crt"),
                profile_snapshot=new_snapshot,
                title=item.title,
                issued_by=item.issued_by,
                issued_date=item.issued_date,
                expiry_date=item.expiry_date,
                credential_id=item.credential_id,
                certificate_url=item.certificate_url,
                description=item.description,
                image=item.image,
                position=item.position,
            )
            for item in certificates
        ])
