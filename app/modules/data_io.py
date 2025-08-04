"""
Veri giriş/çıkış işlemlerini yöneten modül.

Bu modül, dosya okuma ve yazma işlemlerini yönetir ve verileri pandas DataFrame
olarak işler.
"""
import io
import logging
from typing import Tuple, Dict, Any

import pandas as pd
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse

# Loglama yapılandırması
logger = logging.getLogger(__name__)

# Maksimum dosya boyutu (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

async def read_from_upload(file: UploadFile) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Yüklenen dosyayı okuyarak pandas DataFrame'e dönüştürür.
    
    Args:
        file: FastAPI UploadFile nesnesi
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (DataFrame, dosya bilgileri)
        
    Raises:
        HTTPException: Dosya okuma veya dönüştürme hatası durumunda
    """
    try:
        # Dosya boyutunu kontrol et
        file.file.seek(0, 2)  # Sonra konumla
        file_size = file.file.tell()
        file.file.seek(0)  # Başa dön
        
        if file_size > MAX_FILE_SIZE:
            error_msg = f"Dosya boyutu çok büyük. Maksimum izin verilen boyut: {MAX_FILE_SIZE/1024/1024}MB"
            logger.warning(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        # Dosya içeriğini oku
        content = await file.read()
        
        # CSV dosyasını DataFrame'e oku
        try:
            df = pd.read_csv(io.BytesIO(content))
        except pd.errors.EmptyDataError:
            error_msg = "Dosya boş veya geçersiz bir CSV dosyası."
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg) from None
            
        # Dosya bilgilerini topla
        file_info = {
            "filename": file.filename,
            "size": file_size,
            "content_type": file.content_type,
            "rows": len(df),
            "columns": len(df.columns),
            "columns_list": df.columns.tolist()
        }
        
        logger.info(
            f"Dosya başarıyla okundu: {file.filename}, "
            f"Boyut: {file_size} bayt, "
            f"Satır: {len(df)}, Sütun: {len(df.columns)}"
        )
        
        return df, file_info
        
    except pd.errors.ParserError as e:
        error_msg = f"CSV ayrıştırma hatası: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=400, detail=error_msg) from e
        
    except Exception as e:
        error_msg = f"Dosya okuma hatası: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg) from e

def write_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    DataFrame'i CSV formatında bayt dizisine dönüştürür.
    
    Args:
        df: Dönüştürülecek pandas DataFrame
        
    Returns:
        bytes: CSV içeriğinin bayt temsili
        
    Raises:
        HTTPException: Dönüştürme hatası durumunda
    """
    try:
        if df.empty:
            logger.warning("Boş DataFrame CSV'ye dönüştürülmeye çalışılıyor.")
            return b''
            
        # DataFrame'i CSV formatında bir StringIO nesnesine yaz
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        
        # StringIO'dan bayt dizisine dönüştür
        csv_bytes = output.getvalue().encode('utf-8')
        
        logger.info(f"CSV verisi oluşturuldu. Boyut: {len(csv_bytes)} bayt")
        return csv_bytes
        
    except Exception as e:
        error_msg = f"CSV dönüştürme hatası: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg) from e

def create_download_response(df: pd.DataFrame, filename: str = "cleaned_data.csv") -> StreamingResponse:
    """
    DataFrame'den indirilebilir bir yanıt oluşturur.
    
    Args:
        df: İndirilecek veri çerçevesi
        filename: İndirilecek dosyanın adı (varsayılan: "cleaned_data.csv")
        
    Returns:
        StreamingResponse: İndirilebilir yanıt
    """
    try:
        csv_bytes = write_to_csv_bytes(df)
        
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(csv_bytes))
            }
        )
        
    except Exception as e:
        logger.error(f"İndirme yanıtı oluşturma hatası: {str(e)}", exc_info=True)
        raise
