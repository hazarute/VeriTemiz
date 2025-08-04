# VeriTemiz 1.0

![VeriTemiz Logo](https://via.placeholder.com/150x50?text=VeriTemiz)

VeriTemiz, kullanıcı dostu bir arayüz ile veri temizleme işlemlerini kolaylaştıran bir web uygulamasıdır. CSV veya Excel formatındaki veri setlerinizi yükleyip, çeşitli temizleme işlemlerini uygulayarak analize hazır hale getirebilirsiniz.

## Özellikler

- **Kolay Dosya Yükleme**: CSV ve Excel dosyalarını kolayca yükleyin
- **Veri Önizleme**: Yüklenen veriyi tablo formatında görüntüleyin
- **Temizleme İşlemleri**:
  - Eksik değerleri olan satırları kaldırma
  - Yinelenen satırları temizleme
  - Veri tiplerini otomatik algılama ve dönüştürme
  - Sütun isimlerini düzenleme
- **Hızlı İşlem**: Büyük veri setlerinde bile hızlı çalışma
- **Güvenli**: Verileriniz sadece sizin tarafınızdan görüntülenir ve işlenir

## Teknik Özellikler

- **Backend**: Python 3.9+ ve FastAPI
- **Veri İşleme**: Pandas, NumPy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Sunucu**: Uvicorn ASGI sunucusu
- **Geliştirme Araçları**: Black, Pytest, Python-dotenv

## Kurulum

1. Gerekli yazılımların yüklü olduğundan emin olun:
   - Python 3.9 veya üzeri
   - pip (Python paket yöneticisi)
   - Git (isteğe bağlı)

2. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/VeriTemiz1.0.git
   cd VeriTemiz1.0
   ```

3. Sanal ortam oluşturup etkinleştirin:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Başlarken

1. Uygulamayı başlatın:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Tarayıcınızı açın ve şu adrese gidin:
   ```
   http://127.0.0.1:8000
   ```

## Proje Yapısı

```
VeriTemiz1.0/
├── app/                    # Ana uygulama klasörü
│   ├── __init__.py
│   ├── main.py            # FastAPI uygulama giriş noktası
│   └── modules/           # İş mantığı modülleri
│       ├── __init__.py
│       ├── data_io.py     # Veri giriş/çıkış işlemleri
│       └── cleaning.py    # Veri temizleme fonksiyonları
├── frontend/              # Web arayüzü dosyaları
│   ├── index.html         # Ana sayfa
│   └── static/
│       ├── css/           # Stil dosyaları
│       └── js/            # JavaScript dosyaları
├── .gitignore
├── requirements.txt       # Python bağımlılıkları
└── README.md              # Bu dosya
```

## API Dokümantasyonu

Uygulama çalışırken, otomatik olarak oluşturulan API dokümantasyonuna şu adresten ulaşabilirsiniz:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Katkıda Bulunma

1. Bu projeyi fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b ozellik/yeni-ozellik`)
3. Değişikliklerinizi kaydedin (`git commit -am 'Yeni özellik eklendi'`)
4. Dalınıza gönderin (`git push origin ozellik/yeni-ozellik`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Proje sahibi: [HAZAR UTE] - hazarute@gmail.com

Proje Linki: [https://github.com/kullaniciadi/VeriTemiz1.0](https://github.com/kullaniciadi/VeriTemiz1.0)

## Teşekkürler

- [FastAPI](https://fastapi.tiangolo.com/) ekibine harika bir framework için
- [Pandas](https://pandas.pydata.org/) ekibine güçlü veri işleme araçları için
- Tüm açık kaynak katkıcılarına