import os
import zipfile
import pandas as pd

def register_command(subparsers):
    p_inspect = subparsers.add_parser("inspect-schema", help="Проверить и сравнить колонки во всех ZIP-архивах")
    p_inspect.add_argument("--dir", "-d", type=str, default="pyspark_task/data", help="Путь к папке с архивами")
    p_inspect.set_defaults(func=run)

def is_real_csv(name: str) -> bool:
    """Отсеивает служебные файлы macOS и не-CSV."""
    base = os.path.basename(name)
    return (
        name.lower().endswith(".csv")
        and not name.startswith("__MACOSX/")
        and not base.startswith("._")
    )


def read_header(z: zipfile.ZipFile, inner_file: str, nrows: int = 5) -> pd.DataFrame:
    """Читает заголовок CSV, пробуя несколько кодировок (файл открывается заново на каждую попытку)."""
    for encoding in ("utf-8", "latin1"):
        try:
            with z.open(inner_file) as f:
                return pd.read_csv(f, nrows=nrows, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось определить кодировку: {inner_file}")


def run(args):
    """Команда для проверки и сравнения колонок во всех ZIP-архивах."""
    data_dir = args.dir
    print(f"🔍 Сканирование архивов и колонок в директории: {data_dir}\n")

    if not os.path.exists(data_dir):
        print(f"❌ Директория '{data_dir}' не найдена.")
        return

    column_report = {}

    for file_name in sorted(os.listdir(data_dir)):
        if not file_name.endswith(".zip"):
            continue

        zip_path = os.path.join(data_dir, file_name)
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                for inner_file in z.namelist():
                    if not is_real_csv(inner_file):
                        continue

                    try:
                        df_head = read_header(z, inner_file)
                    except Exception as e:
                        print(f"❌ Ошибка чтения {file_name} -> {inner_file}: {e}\n")
                        continue

                    columns = list(df_head.columns)
                    key = f"{file_name} -> {inner_file}"
                    column_report[key] = columns
                    print(f"📄 {key}")
                    print(f"   Колонок ({len(columns)}): {columns}\n")
        except zipfile.BadZipFile:
            print(f"❌ Файл {file_name} не является корректным ZIP-архивом.")
        except Exception as e:
            print(f"❌ Ошибка при чтении архива {file_name}: {e}")

    if not column_report:
        print("⚠️ CSV-файлы не найдены.")
        return

    print("-" * 50)
    first_key, first_cols = next(iter(column_report.items()))
    all_identical = all(cols == first_cols for cols in column_report.values())

    if all_identical:
        print("✅ Успех: Во всех CSV-файлах структура колонок ПОЛНОСТЬЮ совпадает!")
        return

    print("⚠️ Внимание: Обнаружены различия в наборе или порядке колонок между файлами.\n")

    # Показываем, чем именно отличаются файлы от первого
    first_set = set(first_cols)
    for key, cols in column_report.items():
        if key == first_key:
            continue
        cur_set = set(cols)
        only_first = sorted(first_set - cur_set)
        only_cur = sorted(cur_set - first_set)
        print(f"🔸 {key} vs {first_key}")
        if only_first:
            print(f"   Есть только в эталоне: {only_first}")
        if only_cur:
            print(f"   Есть только здесь:     {only_cur}")
        if not only_first and not only_cur:
            print("   Набор колонок тот же, отличается только порядок.")
        print()