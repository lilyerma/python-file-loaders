import os
import zipfile
import pytest
from extractor import ZipExtractor


@pytest.fixture
def mock_zip_environment(tmp_path):
    """Создает во временной папке тестовый .zip архив для проверки распаковки."""
    source_dir = tmp_path / "source_zips"
    target_dir = tmp_path / "extracted_files"
    source_dir.mkdir()
    
    # Создаем тестовый .zip файл
    zip_filename = "test_data.zip"
    zip_path = source_dir / zip_filename
    
    # Внутри архива будет лежать текстовый файл со строкой данных
    inner_file_name = "sample.txt"
    inner_file_content = b"hello divvy data"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr(inner_file_name, inner_file_content)
        
    return str(source_dir), str(target_dir), zip_filename, inner_file_name


def test_zip_extractor_success(mock_zip_environment):
    """Тест успешной распаковки архива и удаления оригинала."""
    source_dir, target_dir, zip_filename, inner_file_name = mock_zip_environment
    
    extractor = ZipExtractor(source_dir=source_dir, target_dir=target_dir)
    report = extractor.extract_and_clean_all()
    
    # Проверяем отчет
    assert report[zip_filename] == "EXTRACTED"
    
    # Проверяем, что исходный zip-файл был удален
    original_zip_path = os.path.join(source_dir, zip_filename)
    assert not os.path.exists(original_zip_path)
    
    # Проверяем, что внутренний файл успешно извлекся в целевую папку
    extracted_file_path = os.path.join(target_dir, inner_file_name)
    assert os.path.exists(extracted_file_path)
    
    with open(extracted_file_path, "rb") as f:
        assert f.read() == b"hello divvy data"