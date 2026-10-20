"""Модуль для измерения потребления оперативной памяти с помощью tracemalloc."""

import contextlib
import time
import tracemalloc


@contextlib.contextmanager
def memory_profiler(task_name: str = "Задача"):
  """Контекстный менеджер для замера памяти и времени выполнения блока кода.

  Пример использования:
      with memory_profiler("Чтение большого файла"):
          LineReader.read_stream(stream, mode="stdout")
  """
  # Запускаем трекер памяти и таймер
  tracemalloc.start()
  start_time = time.time()

  try:
    yield
  finally:
    # Получаем показатели: текущая память и пиковая (максимальная за время работы блока)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_time = time.time() - start_time

    # Переводим байты в мегабайты (МБ)
    current_mb = current / 1024 / 1024
    peak_mb = peak / 1024 / 1024

    print("--------------------------------------------------")
    print(f"🧠 [Memory Profiler] {task_name}:")
    print(f"   ⏱ Время выполнения: {elapsed_time:.4f} сек.")
    print(f"   📊 Текущая память на выходе: {current_mb:.2f} MB")
    print(f"   🔥 Пиковое потребление памяти (Peak): {peak_mb:.2f} MB")
    print("--------------------------------------------------")