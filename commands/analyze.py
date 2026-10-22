def run(args):
    """Анализ CSV-файлов."""
    from csv_to_pg_loader.analyzer import CsvAnalyzer

    print(f"📊 Запуск анализа данных по пути: {args.input}")
    analyzer = CsvAnalyzer(root_dir=args.input)
    analyzer.run_analysis()