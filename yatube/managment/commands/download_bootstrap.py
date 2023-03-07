from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Download Bootstrap CSS file"

    def handle(self, *args, **options):
        import os

        import requests

        CSS_FILE_NAME = "bootstrap.min.css"
        CSS_FILE_URL = (
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1"
            + "/dist/css/bootstrap.min.css"
        )
        CSS_FILE_DIR = "static/css"

        if not os.path.exists(CSS_FILE_DIR):
            os.makedirs(CSS_FILE_DIR)

        if not os.path.isfile(os.path.join(CSS_FILE_DIR, CSS_FILE_NAME)):
            response = requests.get(CSS_FILE_URL)
            response.raise_for_status()
            with open(os.path.join(CSS_FILE_DIR, CSS_FILE_NAME), "wb") as f:
                f.write(response.content)
        self.stdout.write(
            self.style.SUCCESS(
                "Успешная загрузка Bootstrap CSS file 5.3.0-alpha1"
            )
        )
