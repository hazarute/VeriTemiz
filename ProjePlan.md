VeriTemiz – Proje Planı (MVP)
Versiyon: 1.0
Tarih: 03.08.2025

1. Proje Özeti ve Amaç
Elevator Pitch:
VeriTemiz, kullanıcıların CSV veya Excel formatındaki veri setlerini web arayüzü üzerinden yükleyip, modüler temizleme adımlarını uygulayarak analize hazır, kaliteli veri setleri elde etmelerini sağlar.
Projenin Amacı ve Çözdüğü Sorun:
Veri temizleme, veri analizi sürecinin en zaman alan ve teknik bilgi gerektiren adımlarından biridir. VeriTemiz, kodlama bilgisi olmayan veya karmaşık araçlarla uğraşmak istemeyen kullanıcılar için eksik değerleri doldurma, format hatalarını düzeltme ve tutarsız verileri giderme işlemlerini kolaylaştırır. Böylece veri kalitesi artar ve analiz süreçleri hızlanır.
Hedef Kitle:
- Veri Analistleri ve Bilimciler
- Akademisyenler ve Öğrenciler
- Küçük ve Orta Ölçekli İşletmeler (KOBİ)

2. MVP Kapsamındaki Temel Özellikler
- Dosya Yükleme
Kullanıcı, bilgisayarından .csv formatında dosya yükleyebilir.
- Veri Önizleme
Yüklenen veri setinin ilk 10 satırı tablo formatında görüntülenir.
- Temel Temizleme Fonksiyonları
- Eksik değer içeren satırları silme
- Yinelenen satırları kaldırma
- İşleme ve İndirme
Seçilen temizleme adımları uygulanır ve temizlenmiş veri .csv olarak indirilebilir.

3. Teknik Gereksinimler ve Araçlar
- Programlama Dili: Python 3.9+
Ana Kütüphaneler / Framework’ler
- Backend (API): FastAPI
- Veri İşleme: Pandas, NumPy
- Frontend:
- HTML5, CSS3 (Tailwind CSS)
- JavaScript (Fetch API)
- Veritabanı: MVP aşamasında kullanılmayacak; dosyalar geçici sunucu hafızasında işlenecek.
Diğer Araçlar
- venv: Sanal ortam
- Uvicorn: ASGI sunucusu

4. Klasör ve Dosya Mimarisi

/VeriTemiz/
│
├── app/                  # Ana uygulama klasörü
│   ├── __init__.py
│   │
│   ├── main.py           # FastAPI uygulamasının giriş noktası ve API rotaları
│   │
│   └── modules/          # İş mantığı modülleri
│       ├── __init__.py
│       ├── data_io.py    # Veri okuma ve yazma fonksiyonları
│       └── cleaning.py   # Veri temizleme operasyonları
│
├── frontend/             # Web arayüzü kaynakları
│   ├── index.html        # Ana sayfa
│   └── static/
│       ├── css/style.css # Stil dosyaları
│       └── js/main.js    # JavaScript kodları
│
├── .gitignore            # Git tarafından izlenmeyecek dosyalar
├── requirements.txt      # Proje bağımlılıkları (pandas, fastapi, uvicorn)
└── README.md             # Proje tanımı ve kurulum talimatları

5. Modüler Planlama
Adım 1: Veri Giriş/Çıkış
Dosya: app/modules/data_io.py
- Sorumluluk: Dosyalardan DataFrame okumak ve CSV byte çıktısı üretmek.
- Fonksiyonlar:
- read_from_upload(file): UploadFile → DataFrame
- write_to_csv_bytes(df): DataFrame → CSV byte dizisi
Adım 2: Veri Temizleme
Dosya: app/modules/cleaning.py
- Sorumluluk: DataFrame üzerinde temel temizleme işlemleri.
- Fonksiyonlar:
- remove_missing_rows(df): NaN içeren satırları siler
- remove_duplicate_rows(df): Yinelenen satırları kaldırır
Adım 3: API ve Arayüz Yönetimi
Dosya: app/main.py
- Sorumluluk:
- HTTP isteklerini karşılama
- Modülleri çağırma
- Frontend’e veri gönderme
- API Rotaları:
- GET / → index.html sunar
- POST /api/upload → CSV yükle, önizleme (ilk 10 satır) ve dosya ID döner
- POST /api/process → Dosya ID + temizlik adımları, işleme komutu
- GET /api/download/{file_id} → Temizlenmiş CSV indir
Adım 4: Frontend Etkileşimi
Dosya: frontend/static/js/main.js
- Sorumluluk: Kullanıcı eylemlerini yakalamak, API ile iletişim kurmak, sayfayı güncellemek.
- İş Akışı:
- DOMContentLoaded: Element referansları, event listener’lar
- uploadButton click: Dosya seçimi, /api/upload isteği, renderPreviewTable()
- processButton click: Seçili işlemler, /api/process isteği, indirme yönlendirmesi
- renderPreviewTable(data): JSON verisi → dinamik HTML tablo
Adım 5: Web Arayüzü Yapısı
Dosya: frontend/index.html
- Bölümler:
- Başlık
- Dosya Yükleme
- Veri Önizleme
- Temizleme Seçenekleri
- İşleme ve İndirme
- Durum Mesajları
