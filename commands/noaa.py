from noaa_loader import NoaaPipeline

def register_command(subparsers):
    p_noaa = subparsers.add_parser("noaa", help="Обработка климатического файла с NOAA")
    p_noaa.add_argument("--url", default="https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvf/", help="Базовый URL")
    p_noaa.add_argument("--timestamp", required=True, help='Таймстамп, например: "2024-01-19 15:42"')
    p_noaa.add_argument("--output-dir", default="downloads", help="Директория для сохранения")
    p_noaa.set_defaults(func=run)
    
def run(args):
    """Пайплайн NOAA."""
    try:
        client = NoaaPipeline(base_url=args.url, output_dir=args.output_dir)
        client.run_pipeline(target_timestamp=args.timestamp)
    except Exception as e:
        print(f"❌ Ошибка выполнения NOAA пайплайна: {e}")