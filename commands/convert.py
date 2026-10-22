def run(args):
    """Конвертация JSON в CSV."""
    from json_flattening.converter_json_csv import RaggedJsonToCsvConverter

    print(f"Запуск конвертации из '{args.input}' в целевую папку '{args.output}'...")
    converter = RaggedJsonToCsvConverter(root_dir=args.input, output_dir=args.output)
    converted_files = converter.process_all()
    print(f"Готово! Успешно конвертировано файлов: {len(converted_files)}")