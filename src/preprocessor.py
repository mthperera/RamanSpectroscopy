import json
import os

import numpy as np
import ramanspy as rp
from ramanspy.preprocessing.baseline import ASLS
import yaml


class RamanSpectrumPreprocessor:
    def __init__(self, yaml_path: str):

        with open(yaml_path, "r", encoding="utf-8") as f:
            self.config: list[dict] = yaml.safe_load(f)

        self.x_start = self.config["x_start"]
        self.x_end = self.config["x_end"]
        self.n_points = int(self.x_end - self.x_start + 1)
        self.baseline = ASLS(
            lam=self.config.get("lam", 1e6),
            p=self.config.get("p", 0.01),
        )

    def _extract_xy(self, data):
        s = data["spectrum"]
        x = np.asarray(s["x"], dtype=float)
        y = np.asarray(s["y"], dtype=float)

        if y.ndim == 2:
            y = y[0]

        order = np.argsort(x)
        return x[order], y[order]

    def _interpolate(self, x, y):
        x_new = np.linspace(self.x_start, self.x_end, self.n_points)
        y_new = np.interp(x_new, x, y)

        if x.size >= 2:
            m_left = (y[1] - y[0]) / (x[1] - x[0])
            m_right = (y[-1] - y[-2]) / (x[-1] - x[-2])

            left = x_new < x[0]
            right = x_new > x[-1]

            y_new[left] = y[0] + m_left * (x_new[left] - x[0])
            y_new[right] = y[-1] + m_right * (x_new[right] - x[-1])

        return x_new, y_new

    def _apply_baseline(self, x, y):
        spectrum = rp.Spectrum(y, x)
        corrected = self.baseline.apply(spectrum)
        return corrected.spectral_axis, corrected.spectral_data

    def _normalize(self, y):
        lo, hi = y.min(), y.max()
        return np.zeros_like(y) if np.isclose(lo, hi) else (y - lo) / (hi - lo)

    def clean_spectrum(self, data):
        x, y = self._extract_xy(data)
        x, y = self._interpolate(x, y)
        x, y = self._apply_baseline(x, y)
        y = self._normalize(y)

        data["spectrum"]["x"] = x.tolist()
        data["spectrum"]["y"] = [y.tolist()]

        if "metadata" in data:
            data["metadata"]["spectral_interval_min"] = float(self.x_start)
            data["metadata"]["spectral_interval_max"] = float(self.x_end)
            data["metadata"]["spectra_count"] = 1

        return data

    def process_file(self, input_file, output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cleaned = self.clean_spectrum(data)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)

    def process_folder(self, input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(input_folder):
            if filename.endswith(".json"):
                self.process_file(
                    os.path.join(input_folder, filename),
                    os.path.join(output_folder, filename),
                )
            print(f"Processed {filename}")