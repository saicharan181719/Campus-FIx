from urllib.parse import quote

from django.conf import settings
from storages.backends.s3 import S3Storage


class SupabaseStorage(S3Storage):

    def url(self, name):
        return (
            f"{settings.SUPABASE_PUBLIC_URL}"
            f"/storage/v1/object/public/"
            f"{self.bucket_name}/"
            f"{quote(name, safe='/')}"
        )