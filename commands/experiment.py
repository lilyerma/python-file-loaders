def register_command(subparsers):
    parser = subparsers.add_parser("experiment", help="Запустить эксперимент с CommonCrawl")
    parser.set_defaults(func=run)
    
def run(args):
    """Запуск S3-эксперимента."""
    from experiment_s3 import run_experiment

    print("🚀 Запуск S3-эксперимента из CLI...")
    try:
        run_experiment()
        print("✨ Эксперимент успешно завершен!")
    except Exception as e:
        print(f"❌ Ошибка во время выполнения эксперимента: {e}")