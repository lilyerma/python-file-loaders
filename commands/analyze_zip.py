# commands/analyze_zip.py
import os
from pathlib import Path
from extractors.zip_extractor import ZipExtractor
from pandas_analyzer.analyzer import CsvAnalyzer

def register_command(subparsers):
    p_zip = subparsers.add_parser("analyze-zip", help="Распаковать ZIP и завести аналитику по CSV с генерацией DDL в консоль")
    p_zip.add_argument("--zip", "-z", required=True, help="Путь к ZIP-архиву для анализа")
    p_zip.add_argument("--temp-dir", default="./temp_extracted", help="Временная папка для распаковки")
    p_zip.set_defaults(func=run)
    
def run(args):
    """Распаковывает один или все ZIP-архивы в папке и анализирует CSV без сохранения DDL."""
    target_path = args.zip
    temp_dir = getattr(args, "temp_dir", "./temp_extracted")

    # Собираем список файлов для обработки: если передали папку, берем все .zip внутри неё
    if os.path.isdir(target_path):
        zip_files = [
            os.path.join(target_path, f) 
            for f in os.listdir(target_path) 
            if f.endswith(".zip")
        ]
        print(f"📁 Обнаружена папка. Найдено ZIP-архивов для анализа: {len(zip_files)}")
    else:
        zip_files = [target_path]

    if not zip_files:
        print(f"❌ В указанном пути не найдено ZIP-файлов: {target_path}")
        return

    extractor = ZipExtractor()

    # Проходим по каждому архиву
    for zip_path in zip_files:
        print(f"\n" + "="*50)
        print(f"📦 Обработка архива: {zip_path}")
        print("="*50)
        
        try:
            # Создаем уникальную подпапку для каждого архива, чтобы они не перезаписывали друг друга
            sub_target_dir = os.path.join(temp_dir, Path(zip_path).stem)
            
            # Распаковываем через ZipExtractor[cite: 11]
            extractor.extract_from_file(zip_path, sub_target_dir)

            print(f"\n📊 Запуск CSV-анализатора...")
            # Запускаем анализ распакованных данных (без сохранения DDL в файлы)
            analyzer = CsvAnalyzer(
                root_dir=Path(sub_target_dir),
                ddl_output_dir=None 
            )
            analyzer.run_analysis()

        except Exception as e:
            print(f"❌ Ошибка при анализе архива {zip_path}: {e}")