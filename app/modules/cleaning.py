"""
Veri temizleme işlemlerini içeren modül.

Bu modül, veri setlerine çeşitli temizleme işlemleri uygulamak için kullanılır.
"""
from typing import Dict, Any, TypedDict, Literal
from typing_extensions import NotRequired
import pandas as pd
import logging

# Loglama yapılandırması
logger = logging.getLogger(__name__)

class CleaningOperations(TypedDict):
    """Temizleme işlemleri için tip tanımı.
    
    Attributes:
        remove_missing: Eksik değer içeren satırları kaldır
        remove_duplicates: Yinelenen satırları kaldır
        columns: İşlem yapılacak sütunlar (opsiyonel, tüm sütunlar için None)
    """
    remove_missing: NotRequired[bool]
    remove_duplicates: NotRequired[bool]
    columns: NotRequired[list[str] | None]

def clean_data(df: pd.DataFrame, operations: CleaningOperations) -> pd.DataFrame:
    """
    Veri çerçevesine belirtilen temizleme işlemlerini uygular.
    
    Args:
        df: Temizlenecek veri çerçevesi
        operations: Uygulanacak temizleme işlemlerini içeren sözlük
        
    Returns:
        Temizlenmiş veri çerçevesi
        
    Raises:
        ValueError: Geçersiz işlem veya veri tipi durumunda
    """
    try:
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Geçersiz veri tipi. DataFrame bekleniyor.")
            
        if df.empty:
            logger.warning("Boş veri çerçevesi alındı, işlem yapılamadı.")
            return df
            
        df_cleaned = df.copy()
        
        # Eksik değerleri temizle
        if operations.get('remove_missing'):
            df_cleaned = remove_missing_rows(
                df_cleaned, 
                columns=operations.get('columns')
            )
            
        # Yinelenen satırları kaldır
        if operations.get('remove_duplicates'):
            df_cleaned = remove_duplicate_rows(
                df_cleaned, 
                columns=operations.get('columns')
            )
            
        return df_cleaned
        
    except Exception as e:
        logger.error(f"Veri temizleme hatası: {str(e)}", exc_info=True)
        raise

def remove_missing_rows(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """
    Eksik değer içeren satırları kaldırır.
    
    Args:
        df: İşlenecek veri çerçevesi
        columns: Kontrol edilecek sütunlar (None ise tüm sütunlar)
        
    Returns:
        Eksik değer içermeyen satırlardan oluşan veri çerçevesi
    """
    try:
        initial_rows = len(df)
        
        if columns:
            # Belirtilen sütunlarda eksik değer kontrolü
            df_cleaned = df.dropna(subset=columns)
        else:
            # Tüm sütunlarda eksik değer kontrolü
            df_cleaned = df.dropna()
            
        removed_rows = initial_rows - len(df_cleaned)
        if removed_rows > 0:
            logger.info(f"{removed_rows} adet eksik değer içeren satır kaldırıldı.")
            
        return df_cleaned
        
    except Exception as e:
        logger.error(f"Eksik değerleri kaldırma hatası: {str(e)}", exc_info=True)
        raise

def remove_duplicate_rows(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """
    Yinelenen satırları kaldırır.
    
    Args:
        df: İşlenecek veri çerçevesi
        columns: Yinelenme kontrolü yapılacak sütunlar (None ise tüm sütunlar)
        
    Returns:
        Yinelenmeyen satırlardan oluşan veri çerçevesi
    """
    try:
        initial_rows = len(df)
        
        # Belirtilen sütunlara göre veya tüm sütunlarda yinelenenleri kaldır
        df_cleaned = df.drop_duplicates(subset=columns, keep='first')
        
        removed_rows = initial_rows - len(df_cleaned)
        if removed_rows > 0:
            logger.info(f"{removed_rows} adet yinelenen satır kaldırıldı.")
            
        return df_cleaned
        
    except Exception as e:
        logger.error(f"Yinelenen satırları kaldırma hatası: {str(e)}", exc_info=True)
        raise
