from src.downloader import SpectrumDownloader


def main():
    downloader = SpectrumDownloader(
        yaml_path="scripts/configs/spectra_ids.yaml",
        output_dir="data/raw",
    )

    downloader.download()


if __name__ == "__main__":
    main()