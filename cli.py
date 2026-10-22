import argparse
import importlib
import logging

# Настройка глобального логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    parser = argparse.ArgumentParser(
        description="🚀 CLI-менеджер для запуска шагов и упражнений по работе с файлами.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды для выполнения")

    # --- 1. Команда: download ---
    p_download = subparsers.add_parser("download", help="Скачать zip-архивы по URL-адресам")
    p_download.add_argument("-m", "--method", type=str, default="thread", choices=["thread", "async", "requests", "wget"])
    p_download.add_argument("-w", "--workers", type=int, default=3, help="Количество потоков")
    p_download.add_argument("urls", nargs="*", help="Список URL через пробел (опционально)")

    # --- 2. Команда: extract ---
    subparsers.add_parser("extract", help="Распаковать скачанные архивы")

    # --- 3. Команда: clean ---
    subparsers.add_parser("clean", help="Удалить все созданные папки и файлы")

    # --- 4. Команда: benchmark ---
    subparsers.add_parser("benchmark", help="Запустить сравнение скорости всех загрузчиков")

    # --- 5. Команда: noaa ---
    p_noaa = subparsers.add_parser("noaa", help="Обработка климатического файла с NOAA")
    p_noaa.add_argument("--url", default="https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvf/", help="Базовый URL")
    p_noaa.add_argument("--timestamp", required=True, help='Таймстамп, например: "2024-01-19 15:42"')
    p_noaa.add_argument("--output-dir", default="downloads", help="Директория для сохранения")

    # --- 6. Команда: experiment ---
    subparsers.add_parser("experiment", help="Запустить эксперимент с CommonCrawl")

    # --- 7. Команда: convert ---
    p_conv = subparsers.add_parser("convert", help="Конвертация JSON в CSV")
    p_conv.add_argument("--input", "-i", type=str, default="./data", help="Директория с JSON")
    p_conv.add_argument("--output", "-o", type=str, default="output_csv", help="Директория для CSV")

    # --- 8. Команда: analyze ---
    p_anal = subparsers.add_parser("analyze", help="Анализ CSV-файлов")
    p_anal.add_argument("--input", "-i", type=str, default="csv_to_pg_loader/data", help="Путь к CSV")

    # --- 9. Команда: run-sql ---
    p_sql = subparsers.add_parser("sql-run", help="Запустить SQL скрипты в PostgreSQL")
    p_sql.add_argument("--dir", "-d", type=str, default="csv_to_pg_loader/sql", help="Путь к директории с .sql")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Превращаем дефисы в подчеркивания (например, "sql-run" -> модуль "commands.sql_run")
        module_name = args.command.replace("-", "_")
        
        # Динамический импорт нужного модуля из папки commands
        module = importlib.import_module(f"commands.{module_name}")
        
        # Проверяем наличие стандартизированной функции run и выполняем её
        if hasattr(module, "run"):
            module.run(args)
        else:
            print(f"❌ В модуле 'commands.{module_name}' не найдена функция run(args)")

    except ImportError as e:
        print(f"❌ Не удалось загрузить модуль для команды '{args.command}': {e}")
    except Exception as e:
        print(f"❌ Ошибка выполнения команды '{args.command}': {e}")


if __name__ == "__main__":
    main()