from utils.zip_analyzer import ZipAnalyzer


def register_command(subparsers):
    p_zip = subparsers.add_parser("analyze-zip", help="Распаковать ZIP и завести аналитику по CSV с генерацией DDL в консоль")
    p_zip.add_argument("--zip", "-z", required=True, help="Путь к ZIP-архиву для анализа")
    p_zip.add_argument("--temp-dir", default="./temp_extracted", help="Временная папка для распаковки")
    p_zip.set_defaults(func=run)
    
def run(args):
    print(f"📊 Запуск анализа данных по пути: {args.zip}")
    
    # Используем правильные имена параметров и нижние подчеркивания
    analyzer = ZipAnalyzer(
        target_path=args.zip, 
        temp_dir=args.temp_dir
    )
    analyzer.run()