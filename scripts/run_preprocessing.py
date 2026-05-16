from src.preprocessor import RamanSpectrumPreprocessor


def main():
    preprocessor = RamanSpectrumPreprocessor("scripts/configs/preprocessing.yaml")
    preprocessor.process_folder("data/raw", "data/processed")


if __name__ == "__main__":
    main()