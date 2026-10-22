def run(args):
    """Пайплайн NOAA."""
    from noaa_loader import NoaaPipeline

    try:
        client = NoaaPipeline(base_url=args.url, output_dir=args.output_dir)
        client.run_pipeline(target_timestamp=args.timestamp)
    except Exception as e:
        print(f"❌ Ошибка выполнения NOAA пайплайна: {e}")