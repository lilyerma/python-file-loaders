from abc import ABC, abstractmethod
import io
from typing import Union


class BaseExtractor(ABC):
  """Абстрактный базовый класс для всех распаковщиков."""

  @abstractmethod
  def extract_from_file(self, source_path: str, target_dir: str) -> str:
    """Распаковывает файл с диска в целевую директорию."""
    pass

  @abstractmethod
  def extract_from_memory(self, source_buffer: io.BytesIO, target_dir: str, output_filename: str) -> str:
    """Распаковывает данные из оперативной памяти (BytesIO) на диск."""
    pass