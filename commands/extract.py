import logging

logger = logging.getLogger("CLI.Extract")
DEFAULT_RAW_DIR = "divvy_zips"
DEFAULT_EXTRACTED_DIR = "divvy_extracted"

def register_command(subparsers):
    parser = subparsers.add_parser("extract", help="Распаковать скачанные архивы")
    parser.set_defaults(func=run)
    
def run(args):
    """Распаковка архивов."""
    from extractors.zip_extractor import ZipExtractor

    logger.info("Запуск распаковки из %s в %s", DEFAULT_RAW_DIR, DEFAULT_EXTRACTED_DIR)
    extractor = ZipExtractor(source_dir=DEFAULT_RAW_DIR, target_dir=DEFAULT_EXTRACTED_DIR)
    extractor.extract_and_clean_all()
    logger.info("Распаковка и очистка архивов завершена.")