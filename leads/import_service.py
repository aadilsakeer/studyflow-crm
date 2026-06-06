import pandas as pd

from .models import Lead


class LeadImportService:

    @staticmethod
    def preview_excel(file_path):

        df = pd.read_excel(file_path)

        return df.head()

    @staticmethod
    def import_excel(file_path):

        df = pd.read_excel(file_path)

        created = 0
        duplicates = 0

        for _, row in df.iterrows():

            phone = str(row.get("phone", "")).strip()

            if Lead.objects.filter(phone=phone).exists():
                duplicates += 1
                continue

            Lead.objects.create(
                first_name=row.get("first_name", ""),
                last_name=row.get("last_name", ""),
                phone=phone,
                email=row.get("email", "")
            )

            created += 1

        return {
            "created": created,
            "duplicates": duplicates
        }