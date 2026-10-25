from json_flattening.converter_json_csv import RaggedJsonToCsvConverter

def register_command(subparsers):
    p_conv = subparsers.add_parser("convert", help="Конвертация JSON в CSV")
    p_conv.add_argument("--input", "-i", type=str, default="./data", help="Директория с JSON")
    p_conv.add_argument("--output", "-o", type=str, default="output_csv", help="Директория для CSV")
    p_conv.set_defaults(func=run)
    
def run(args):
    """Конвертация JSON в CSV."""

    converter = RaggedJsonToCsvConverter(root_dir=args.input, output_dir=args.output)
    converted_files = converter.process_all()
    print(f"Готово! Успешно конвертировано файлов: {len(converted_files)}")