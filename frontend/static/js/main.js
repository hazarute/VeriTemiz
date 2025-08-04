/**
 * @file main.js
 * @description CSV dosyalarını yüklemek, temizlemek ve indirmek için istemci tarafı mantığını yönetir.
 * API uç noktalarıyla iletişim kurar, kullanıcı arayüzünü günceller ve veri önizlemesini işler.
 */
document.addEventListener('DOMContentLoaded', () => {

    //======================================================================
    // DOM Element Referansları
    //======================================================================
    const fileInput = document.getElementById('file-upload');
    const uploadBtn = document.getElementById('upload-btn');
    const processBtn = document.getElementById('process-btn');
    const previewSection = document.getElementById('preview-section');
    const cleaningOptions = document.getElementById('cleaning-options');
    const dataPreviewTable = document.getElementById('data-preview');
    const dataPreviewHead = dataPreviewTable.querySelector('thead tr');
    const dataPreviewBody = dataPreviewTable.querySelector('tbody');
    const statusMessage = document.getElementById('status-message');

    //======================================================================
    // Uygulama Durumu (State)
    //======================================================================
    let currentFileId = null;

    //======================================================================
    // Olay Dinleyicileri (Event Listeners)
    //======================================================================
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    processBtn.addEventListener('click', handleProcessData);

    //======================================================================
    // Ana Fonksiyonlar
    //======================================================================

    /**
     * Kullanıcının seçtiği dosyayı işler, doğrular ve sunucuya yükler.
     * @param {Event} event - Dosya girişinden gelen olay nesnesi.
     */
    async function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.csv')) {
            showStatus('Lütfen sadece CSV formatında bir dosya yükleyin.', 'error');
            return;
        }

        setLoadingState(true, file.name);
        showStatus('Dosya yükleniyor, lütfen bekleyin...', 'info');

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Doğrudan fetch kullanıyoruz çünkü apiFetch Content-Type'ı değiştiriyor
            const response = await fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer demo-key'  // Gerekli ise
                },
                body: formData  // FormData kullanıldığında Content-Type otomatik ayarlanır
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || result.message || 'Dosya yüklenirken bir hata oluştu');
            }

            if (result.status === 'success') {
                currentFileId = result.file_id;
                updateUIAfterUpload(file.name, result.rows, result.columns, result.preview_data);
                showStatus('Dosya başarıyla yüklendi!', 'success');
            } else {
                throw new Error(result.message || 'Sunucudan beklenmedik bir yanıt alındı.');
            }
        } catch (error) {
            console.error('Dosya yükleme hatası:', error);
            showStatus(`Hata: ${error.message}`, 'error');
            resetUploader();
        } finally {
            setLoadingState(false, file.name);
        }
    }

    /**
     * Seçilen temizleme işlemlerini sunucuya gönderir ve sonucu işler.
     */
    async function handleProcessData() {
        if (!currentFileId) {
            showStatus('İşlem yapmak için önce bir dosya yüklemelisiniz.', 'error');
            return;
        }

        const operations = {
            remove_missing: document.getElementById('remove-missing').checked,
            remove_duplicates: document.getElementById('remove-duplicates').checked,
            columns: null  // Şimdilik tüm sütunları işle
        };

        if (!operations.remove_missing && !operations.remove_duplicates) {
            showStatus('Lütfen en az bir temizleme işlemi seçin.', 'warning');
            return;
        }

        setProcessingState(true);
        showStatus('Veri temizleniyor, bu işlem biraz zaman alabilir...', 'info');

        try {
            // Doğrudan fetch kullanıyoruz ve gerekli header'ları ekliyoruz
            const requestBody = {
                file_id: currentFileId,
                operations: operations,
                // Kimlik doğrulama için gerekli alanlar
                scheme: 'bearer',
                credentials: 'demo-key'  // Geliştirme için sabit anahtar
            };

            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer demo-key'  // Header'da da gönderiyoruz
                },
                body: JSON.stringify(requestBody)
            });

            const result = await response.json();
            
            if (!response.ok) {
                // Backend'den gelen detaylı hata mesajlarını işle
                let errorMessage = 'Veri işlenirken bir hata oluştu';
                
                // Eğer hata detayı bir dizi ise (örn: FastAPI validasyon hataları)
                if (Array.isArray(result.detail)) {
                    errorMessage = result.detail.map(err => 
                        `${err.loc ? err.loc.join('.') + ' ' : ''}${err.msg}`
                    ).join('; ');
                } 
                // Eğer hata detayı bir string ise
                else if (typeof result.detail === 'string') {
                    errorMessage = result.detail;
                }
                // Eğer doğrudan bir mesaj varsa
                else if (result.message) {
                    errorMessage = result.message;
                }
                
                throw new Error(errorMessage);
            }

            if (result.status === 'success' && result.download_url) {
                showStatus(`İşlem başarılı! ${result.message || ''}`, 'success');
                // İndirme bağlantısını yeni sekmede aç
                window.open(result.download_url, '_blank');
            } else {
                throw new Error(result.message || 'Beklenmeyen yanıt alındı');
            }
        } catch (error) {
            console.error('Veri işleme hatası:', error);
            // Hata mesajını daha okunabilir hale getir
            const errorMessage = error.message || 'Bilinmeyen bir hata oluştu';
            showStatus(`Hata: ${errorMessage}`, 'error');
        } finally {
            setProcessingState(false);
        }
    }

    //======================================================================
    // Yardımcı ve Arayüz Fonksiyonları
    //======================================================================

    /**
     * API isteklerini yöneten merkezi fonksiyon
     * @param {string} url - İstek yapılacak URL
     * @param {Object} options - Fetch API seçenekleri
     * @returns {Promise<any>} - API yanıtı
     */
    async function apiFetch(url, options = {}) {
        // Varsayılan başlıkları ayarla
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer demo-key'
        };

        // Özel başlıkları birleştir
        const headers = {
            ...defaultHeaders,
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // JSON yanıtını çözümle
            let data;
            try {
                data = await response.json();
            } catch (e) {
                // JSON çözümleme hatası durumunda ham metni kullan
                const text = await response.text();
                throw new Error(`Geçersiz JSON yanıtı: ${text}`);
            }

            // Başarısız yanıtları işle
            if (!response.ok) {
                // FastAPI validasyon hatalarını işle
                if (Array.isArray(data.detail)) {
                    const errorMessages = data.detail.map(err => {
                        const loc = err.loc ? err.loc.join('.') : 'bilinmeyen_alan';
                        return `[${loc}] ${err.msg || 'Doğrulama hatası'}`;
                    });
                    throw new Error(errorMessages.join('; '));
                }
                // Diğer hata türlerini işle
                throw new Error(data.detail || data.message || 'Bilinmeyen bir hata oluştu');
            }

            return data;
        } catch (error) {
            console.error('API isteği başarısız oldu:', error);
            throw error; // Hata yönetimini çağrı yapan tarafa bırak
        }
    }

    /**
     * Sunucudan gelen önizleme verileriyle veri tablosunu günceller.
     * Bu fonksiyon, satırlar arasında farklı sütunlar olsa bile çalışacak şekilde tasarlanmıştır.
     * @param {Array<object>} data - Görüntülenecek veri dizisi. Her bir nesne bir satırı temsil eder.
     */
    function updateDataPreview(data) {
        if (!Array.isArray(data) || data.length === 0) {
            dataPreviewTable.classList.add('hidden');
            showStatus('Önizleme için geçerli veri bulunamadı.', 'warning');
            return;
        }

        // Tüm satırlardaki olası bütün sütun başlıklarını topla.
        const allHeaders = new Set();
        data.forEach(row => {
            if (row && typeof row === 'object') {
                Object.keys(row).forEach(key => allHeaders.add(key));
            }
        });
        const headers = Array.from(allHeaders);

        if (headers.length === 0) {
            showStatus('Veri içinde sütun başlıkları tespit edilemedi.', 'error');
            return;
        }

        // Tablo başlığını (thead) temizle ve yeniden oluştur
        dataPreviewHead.innerHTML = '';
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            th.className = 'px-4 py-2 border bg-gray-100 text-left text-sm font-medium text-gray-700 whitespace-nowrap';
            dataPreviewHead.appendChild(th);
        });

        // Tablo gövdesini (tbody) temizle ve yeniden oluştur
        dataPreviewBody.innerHTML = '';
        data.forEach((row, rowIndex) => {
            const tr = document.createElement('tr');
            tr.className = rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            
            headers.forEach(header => {
                const td = document.createElement('td');
                const cellValue = row ? (row[header] ?? '') : ''; // null veya undefined ise boş string kullan
                
                td.textContent = String(cellValue);
                td.className = 'px-4 py-2 border text-sm text-gray-800';

                // Uzun metinler için kırpma ve title ekleme
                if (td.textContent.length > 50) {
                    td.title = td.textContent;
                    td.textContent = td.textContent.substring(0, 50) + '...';
                }
                tr.appendChild(td);
            });
            dataPreviewBody.appendChild(tr);
        });

        dataPreviewTable.classList.remove('hidden');
    }
    
    /**
     * Kullanıcıya çeşitli türlerde (başarı, hata, uyarı, bilgi) durum mesajları gösterir.
     * @param {string} message - Gösterilecek mesaj.
     * @param {'success'|'error'|'warning'|'info'} type - Mesajın türü.
     */
    function showStatus(message, type = 'info') {
        if (!statusMessage) return;

        const styles = {
            error: 'bg-red-100 border-l-4 border-red-500 text-red-700',
            success: 'bg-green-100 border-l-4 border-green-500 text-green-700',
            warning: 'bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700',
            info: 'bg-blue-100 border-l-4 border-blue-500 text-blue-700'
        };
        
        statusMessage.textContent = message;
        statusMessage.className = `p-4 mb-4 ${styles[type] || styles.info}`;
    }

    /**
     * Dosya yüklemesi sonrası kullanıcı arayüzünü günceller.
     * @param {string} fileName - Yüklenen dosyanın adı.
     * @param {number} rows - Verideki satır sayısı.
     * @param {number} columns - Verideki sütun sayısı.
     * @param {Array<object>} previewData - Gösterilecek önizleme verisi.
     */
    function updateUIAfterUpload(fileName, rows, columns, previewData) {
        uploadBtn.textContent = 'Dosya Değiştir';
        showStatus(`${rows} satır ve ${columns} sütun içeren veri başarıyla yüklendi.`, 'success');
        previewSection.classList.remove('hidden');
        cleaningOptions.classList.remove('hidden');
        processBtn.disabled = false;
        updateDataPreview(previewData);
    }
    
    /**
     * Tüm arayüzü ve uygulama durumunu başlangıç haline sıfırlar.
     */
    function resetUploader() {
        fileInput.value = '';
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'CSV Dosyası Seç';
        processBtn.disabled = true;
        processBtn.textContent = 'Veriyi Temizle ve İndir';
        previewSection.classList.add('hidden');
        cleaningOptions.classList.add('hidden');
        currentFileId = null;
        dataPreviewHead.innerHTML = '';
        dataPreviewBody.innerHTML = '';
        if (statusMessage) {
            statusMessage.textContent = '';
            statusMessage.className = '';
        }
    }

    /**
     * Yükleme butonu durumunu ayarlar.
     * @param {boolean} isLoading - Yükleme durumunda mı?
     * @param {string} fileName - Yüklenen dosyanın adı.
     */
    function setLoadingState(isLoading, fileName = '') {
        uploadBtn.disabled = isLoading;
        uploadBtn.textContent = isLoading ? 'Yükleniyor...' : `Dosya Değiştir`;
    }

    /**
     * İşleme butonu durumunu ayarlar.
     * @param {boolean} isProcessing - İşlem durumunda mı?
     */
    function setProcessingState(isProcessing) {
        processBtn.disabled = isProcessing;
        if (isProcessing) {
            processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        } else {
            processBtn.textContent = 'Veriyi Temizle ve İndir';
        }
    }
});