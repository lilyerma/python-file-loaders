DEFAULT_NOAA_DIR = "downloads"
DEFAULT_URIS = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
]

def register_command(subparsers):
    p_download = subparsers.add_parser("download", help="Скачать zip-архивы по URL-адресам")
    p_download.add_argument("-m", "--method", type=str, default="thread", choices=["thread", "async", "requests", "wget"])
    p_download.add_argument("-w", "--workers", type=int, default=3, help="Количество потоков")
    p_download.add_argument("urls", nargs="*", help="Список URL через пробел (опционально)")
    p_download.set_defaults(func=run)

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