import logging

logger = logging.getLogger("CLI.Benchmark")

def register_command(subparsers):
    parser = subparsers.add_parser("benchmark", help="Запустить сравнение скорости всех загрузчиков")
    parser.set_defaults(func=run)

def run(args):
    """Запуск бенчмарка."""
    from benchmark import run_benchmark
    logger.info("Запуск бенчмарка производительности...")
    run_benchmark()