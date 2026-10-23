import argparse
import importlib
import logging
import pkgutil
import commands  # Импортируем вашу папку как пакет

# Настройка глобального логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    parser = argparse.ArgumentParser(
        description="🚀 Универсальный CLI-менеджер с авторегистрацией команд.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды для выполнения")

    # --- Автоматическая регистрация команд из папки commands/ ---
    for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
        # Динамически импортируем каждый модуль из папки commands
        module = importlib.import_module(f"commands.{module_name}")
        
        # Если в модуле есть функция регистрации аргументов, вызываем её
        if hasattr(module, "register_command"):
            module.register_command(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Превращаем дефисы в подчеркивания для поиска модуля (на случай если имя команды через дефис)
        module_name = args.command.replace("-", "_")
        module = importlib.import_module(f"commands.{module_name}")
        
        # Выполняем стандартизированную функцию run(args)
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