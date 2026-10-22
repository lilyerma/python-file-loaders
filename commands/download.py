DEFAULT_NOAA_DIR = "downloads"
DEFAULT_URIS = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
]

def run(args):
    from downloader_pkg.factory import DownloaderFactory
    print(f"Инициализация загрузчика типа: '{args.method}'...")
    try:
        urls_to_download = args.urls if args.urls else DEFAULT_URIS
        downloader = DownloaderFactory.create_downloader(
            loader_type=args.method,
            urls=urls_to_download,
            output_dir=DEFAULT_NOAA_DIR,
            max_workers=args.workers
        )
        results = downloader.download_all()
        for url, status in results.items():
            print(f"[{status}] {url}")
    except Exception as e:
        print(f"❌ Ошибка во время скачивания: {e}")