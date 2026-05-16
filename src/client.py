import os
from enum import Enum
import requests

from dotenv import load_dotenv

load_dotenv(override=True)


class Paths(Enum):
    SPECTRA_DETAIL = "spectra/{id}"
    SPECTRA_DOWNLOAD_RAW = "spectra/{id}/download/raw"
    SPECTRA_DOWNLOAD_PROCESSED = "spectra/{id}/download/processed"


class RamanbaseClient:
    BASE_URL = "https://api.ramanbase.org/api/v1/public"
    API_TOKEN = os.getenv("RAMAN_API_TOKEN")

    @classmethod
    def _request(cls, endpoint: Paths, id: int):
        if not cls.API_TOKEN:
            raise RuntimeError("RAMAN_API_TOKEN não foi encontrado no ambiente")

        url = f"{cls.BASE_URL}/{endpoint.value.format(id=id)}"

        response = requests.get(
            url=url,
            headers={
                "Authorization": f"Token {cls.API_TOKEN}",
                "Accept": "application/json",
            },
            timeout=30,
        )

        response.raise_for_status()
        return response

    @classmethod
    def get_metadata(cls, spectrum_id: int):
        response = cls._request(Paths.SPECTRA_DETAIL, id=spectrum_id)

        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()

        return response.content

    @classmethod
    def download_spectrum(cls, spectrum_id: int, processed: bool = True):
        endpoint = (
            Paths.SPECTRA_DOWNLOAD_PROCESSED
            if processed
            else Paths.SPECTRA_DOWNLOAD_RAW
        )

        response = cls._request(endpoint, id=spectrum_id)

        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.content


if __name__ == "__main__":
    spectrum = RamanbaseClient.download_spectrum(1884, processed=True)
    print(spectrum)

    metadata = RamanbaseClient.get_metadata(1884)
    print(metadata)