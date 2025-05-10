
from typing import Dict, Any

from fastapi import APIRouter, File, UploadFile, Depends
import base64
import os
import rpc_client
from app.dependencies import jwt_validation

router = APIRouter(tags=['OCR Service'])

@router.post('/ocr')
def ocr(file: UploadFile = File(...), payload: dict = Depends(jwt_validation)) -> Dict[str, Any]:
    """Обрабатывает загруженный файл, отправляет его на OCR-обработку через RPC и возвращает результат.
    
    Args:
        file (UploadFile): Файл, загруженный через HTTP-запрос (например, изображение или PDF).
        payload (dict): Декодированные данные JWT-токена, содержащие информацию о пользователе.
                       Зависит от `jwt_validation` (обычно включает `name`, `email`, `id`).

    Returns:
        dict: Результат OCR-обработки, полученный от RPC-сервера.

    Raises:
        HTTPException: Если возникла ошибка при чтении файла, RPC-вызове или удалении временного файла.
    """
    # Сохраняем загруженный файл во временный файл на диске
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())

    # Инициализируем RPC-клиент для OCR
    ocr_rpc = rpc_client.OcrRpcClient()

    # Читаем файл в бинарном режиме и кодируем в base64
    with open(file.filename, "rb") as buffer:
        file_data = buffer.read()
        file_base64 = base64.b64encode(file_data).decode()  # base64 как строка (utf-8)

    # Формируем JSON-запрос для RPC-сервера
    request_json = {
        'user_name': payload['name'],    # Имя пользователя из JWT
        'user_email': payload['email'], # Email из JWT
        'user_id': payload['id'],       # ID пользователя из JWT
        'file': file_base64             # Файл в base64
    }

    # Отправляем запрос на OCR-обработку
    response = ocr_rpc.call(request_json)

    # Удаляем временный файл
    os.remove(file.filename)

    return response