import logging

logger = logging.getLogger("CLI.Benchmark")

def run(args):
    """Запуск бенчмарка."""
    from benchmark import run_benchmark
    logger.info("Запуск бенчмарка производительности...")
    run_benchmark()