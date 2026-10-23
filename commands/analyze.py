def register_command(subparsers):
    p_anal = subparsers.add_parser("analyze", help="Анализ CSV-файлов")
    p_anal.add_argument("--input", "-i", type=str, default="csv_to_pg_loader/data", help="Путь к CSV")
    p_anal.set_defaults(func=run)
    
def run(args):
    """Анализ CSV-файлов."""
    from pandas_analyzer.analyzer import CsvAnalyzer

    print(f"📊 Запуск анализа данных по пути: {args.input}")
    analyzer = CsvAnalyzer(root_dir=args.input)
    analyzer.run_analysis()