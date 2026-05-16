import json
from pathlib import Path

import yaml

from src.client import RamanbaseClient


class SpectrumDownloader:
    def __init__(
        self,
        yaml_path: str,
        output_dir: str = "data/raw",
    ):
        self.output_dir = Path(output_dir)

        with open(yaml_path, "r", encoding="utf-8") as f:
            self.spectra: list[dict] = yaml.safe_load(f)

    def download(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for item in self.spectra:
            spectrum_id = item["id"]
            spectrum_name = item["name"]

            metadata = RamanbaseClient.get_metadata(spectrum_id)
            spectrum = RamanbaseClient.download_spectrum(spectrum_id)

            safe_name = spectrum_name.replace("/", "-")

            data = {
                "metadata": metadata,
                "spectrum": spectrum,
            }

            output_file = self.output_dir / f"{safe_name}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Saved: {output_file}")