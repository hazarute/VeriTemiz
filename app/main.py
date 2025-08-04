"""
VeriTemiz API Uygulaması

Bu modül, veri temizleme işlemleri için REST API sağlar.
Dosya yükleme, işleme ve indirme işlevlerini içerir.
"""
import os
import uuid
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd

# Yerel modüller
from app.modules.data_io import read_from_upload, write_to_csv_bytes, create_download_response
from app.modules.cleaning import clean_data, CleaningOperations

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Güvenlik
security = HTTPBearer()

# Uygulama örneğini oluştur
app = FastAPI(
    title="VeriTemiz API",
    description="Veri temizleme işlemleri için REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Sadece güvenilen kaynaklara izin ver
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=600  # Önbellek süresi (saniye)
)

# Statik dosyaları sun
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent.parent / "frontend" / "static")),
    name="static"
)

# Bellekte veri saklamak için sözlük (Üretimde veritabanı kullanılmalı)
file_store: Dict[str, Dict[str, Any]] = {}

# Geliştirme aşamasında kimlik doğrulamayı devre dışı bırakıyoruz
# Gerçek bir uygulamada bu fonksiyon etkinleştirilmeli
async def verify_token(credentials: HTTPAuthorizationCredentials = None) -> None:
    """Geliştirme aşamasında kimlik doğrulama devre dışı.
    
    Not: Üretim ortamında bu fonksiyon etkinleştirilmeli ve güvenli
    bir kimlik doğrulama mekanizması kullanılmalıdır.
    """
    pass

# Ana sayfa
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Ana sayfayı döndürür."""
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        logger.error(f"Ana sayfa yüklenirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ana sayfa yüklenirken bir hata oluştu."
        )

# Dosya yükleme endpoint'i
@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
) -> Dict[str, Any]:
    """Dosya yüklemek için kullanılan endpoint.
    
    Args:
        file: Yüklenecek dosya
        
    Returns:
        Dict: Dosya bilgileri ve önizleme verileri
    """
    try:
        logger.info(f"Dosya yükleniyor: {file.filename}")
        
        # Dosyayı oku ve DataFrame'e dönüştür
        df, file_info = await read_from_upload(file)
        
        # Benzersiz bir dosya ID'si oluştur
        file_id = str(uuid.uuid4())
        
        # İlk 10 satırı önizleme için ayır
        preview_data = df.head(10).to_dict(orient="records")
        
        # Dosyayı bellekte sakla
        file_store[file_id] = {
            "df": df,
            "filename": file.filename,
            "size": file_info["size"],
            "uploaded_at": pd.Timestamp.now().isoformat(),
            "preview_data": preview_data
        }
        
        logger.info(f"Dosya başarıyla yüklendi. ID: {file_id}")
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "size": file_info["size"],
            "rows": file_info["rows"],
            "columns": file_info["columns"],
            "preview_data": preview_data,
            "message": "Dosya başarıyla yüklendi."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dosya yükleme hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dosya yüklenirken bir hata oluştu: {str(e)}"
        )

# Veri temizleme endpoint'i
@app.post("/api/process")
async def process_data(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
) -> Dict[str, Any]:
    """Veri temizleme işlemlerini uygular.
    
    Request Body:
    {
        "file_id": "dosya-kimligi",
        "operations": {
            "remove_missing": true,
            "remove_duplicates": true,
            "columns": ["sutun1", "sutun2"]  # Opsiyonel
        }
    }
    """
    try:
        # İstek verilerini al
        data = await request.json()
        file_id = data.get("file_id")
        operations: CleaningOperations = data.get("operations", {})
        
        # Dosyayı bul
        if file_id not in file_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dosya bulunamadı. Lütfen tekrar yükleyin."
            )
            
        file_data = file_store[file_id]
        df = file_data["df"]
        
        # Temizleme işlemlerini uygula
        df_cleaned = clean_data(df, operations)
        
        # Temizlenmiş veriyi kaydet
        cleaned_file_id = str(uuid.uuid4())
        file_store[cleaned_file_id] = {
            "df": df_cleaned,
            "filename": f"cleaned_{file_data['filename']}",
            "size": len(write_to_csv_bytes(df_cleaned)),
            "cleaned_at": pd.Timestamp.now().isoformat(),
            "operations": operations
        }
        
        logger.info(f"Veri başarıyla temizlendi. Yeni dosya ID: {cleaned_file_id}")
        
        return {
            "status": "success",
            "file_id": cleaned_file_id,
            "filename": file_store[cleaned_file_id]["filename"],
            "size": file_store[cleaned_file_id]["size"],
            "rows": len(df_cleaned),
            "columns": len(df_cleaned.columns),
            "message": "Veri başarıyla temizlendi.",
            "download_url": f"/api/download/{cleaned_file_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Veri işleme hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Veri işlenirken bir hata oluştu: {str(e)}"
        )

# Dosya indirme endpoint'i
@app.get("/api/download/{file_id}")
async def download_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
) -> StreamingResponse:
    """Temizlenmiş dosyayı indirmek için kullanılan endpoint."""
    try:
        if file_id not in file_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dosya bulunamadı veya süresi dolmuş."
            )
            
        file_data = file_store[file_id]
        df = file_data["df"]
        filename = file_data["filename"]
        
        logger.info(f"Dosya indiriliyor: {filename}")
        
        return create_download_response(df, filename)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dosya indirme hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dosya indirilirken bir hata oluştu: {str(e)}"
        )

# Uygulama başlatıldığında çalışacak kod
@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında çalışır."""
    # Gerekli klasörleri oluştur
    os.makedirs("frontend/static", exist_ok=True)
    logger.info("Uygulama başlatıldı.")

# Hata yönetimi
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP hatalarını yönetir."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Genel hataları yönetir."""
    logger.error(f"Beklenmeyen hata: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "detail": "Beklenmeyen bir hata oluştu."}
    )

# Eğer doğrudan çalıştırılırsa
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
