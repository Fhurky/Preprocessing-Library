# Preprocessing-Library Documentation

## Sınıf: `Preprocessor`

Veri ön işleme işlemleri için hazırlanmış bir sınıftır.  
Desteklenen başlıca işlemler: CSV okuma/kaydetme, sütun kontrolü, eksik değer doldurma, aykırı değer yönetimi, ölçekleme, kategorik encode, sütun silme.

---

### 1️⃣ `__init__(csv_file_path=None)`
**Açıklama:** Sınıfı başlatır, opsiyonel olarak bir CSV dosyasını yükler.  
**Parametreler:**  
- `csv_file_path` (str, opsiyonel): Yüklenecek CSV dosyasının yolu.  

---

### 2️⃣ `load_csv(file_path)`
**Açıklama:** CSV dosyasını okuyarak `self.data` ve `self.header` değişkenlerini günceller.  
**Parametreler:**  
- `file_path` (str): Yüklenecek CSV dosyasının yolu.

---

### 3️⃣ `save_csv(file_name="processed_data.csv", path=None, index=False)`
**Açıklama:** Mevcut DataFrame’i CSV olarak kaydeder.  
**Parametreler:**  
- `file_name` (str): Kaydedilecek dosya adı.  
- `path` (str, opsiyonel): Dosya yolu, belirtilmezse current directory kullanılır.  
- `index` (bool): CSV’ye index yazılsın mı.

---

### 4️⃣ `preview(n=5)`
**Açıklama:** Veri setinin ilk `n` satırını görüntüler.  
**Parametreler:**  
- `n` (int, opsiyonel): Görüntülenecek satır sayısı, varsayılan 5.

---

### 5️⃣ `check_column(column_name)`
**Açıklama:** Bir sütunun temel istatistiklerini ve özelliklerini gösterir.  
**Parametreler:**  
- `column_name` (str): Kontrol edilecek sütun adı.  

**Gösterilen Bilgiler:**  
- Veri tipi (`dtype`)  
- Eksik veri sayısı ve oranı  
- Eşsiz değer sayısı  
- En çok tekrar eden 5 değer  
- Sayısal sütunlar için: ortalama, medyan, std, min, max, aykırı değer sayısı (Z-skor ile)  
- Metin sütunları için: ortalama, en kısa ve en uzun metin uzunluğu  

---

### 6️⃣ `check_csv(z_threshold=3)`
**Açıklama:** CSV hakkında genel bilgiler verir.  
**Parametreler:**  
- `z_threshold` (float, opsiyonel): Sayısal sütunlarda aykırı değer tespiti için Z-skor eşiği, default 3.  

**Gösterilen Bilgiler:**  
- Toplam satır ve sütun sayısı  
- Sütun isimleri ve veri tipleri  
- Eksik değer oranı ve benzersiz değer oranı  
- Sayısal sütunlarda aykırı değer sayısı (Z-skor yöntemi)

---

### 7️⃣ `standard_scale(column_name)`
**Açıklama:** Belirtilen sayısal sütunu standartlaştırır: `(x - mean) / std`.  
**Parametreler:**  
- `column_name` (str): Ölçeklenecek sütun adı.

---

### 8️⃣ `minmax_scale(column_name, feature_range=(0,1))`
**Açıklama:** Belirtilen sayısal sütunu Min-Max ölçekler.  
**Parametreler:**  
- `column_name` (str): Ölçeklenecek sütun adı.  
- `feature_range` (tuple, opsiyonel): Ölçek aralığı `(min, max)`, default `(0,1)`.

---

### 9️⃣ `fill_missing(column_name, method="mean", value=None)`
**Açıklama:** Belirtilen sütundaki eksik değerleri doldurur.  
**Parametreler:**  
- `column_name` (str): Eksik değerleri doldurulacak sütun.  
- `method` (str): `'mean'`, `'median'`, `'mode'`, `'constant'`.  
- `value` (opsiyonel): `'constant'` yöntemi için doldurulacak değer.

---

### 🔟 `drop_column(columns)`
**Açıklama:** Verilen sütun(lar)ı veri setinden düşürür.  
**Parametreler:**  
- `columns` (str veya list): Silinecek sütun veya sütunlar.

---

### 1️⃣1️⃣ `handle_outliers(column_name, method="drop", z_threshold=3, fill_value=None)`
**Açıklama:** Belirtilen sütundaki aykırı değerleri işler.  
**Parametreler:**  
- `column_name` (str): Aykırı değer kontrol edilecek sütun.  
- `method` (str): `'drop'`, `'cap'`, `'impute'`.  
- `z_threshold` (float): Z-skor eşiği, default 3.  
- `fill_value` (opsiyonel): `'impute'` yöntemi için doldurulacak değer.

---

### 1️⃣2️⃣ `encode_column(column_name, mode="label")`
**Açıklama:** Kategorik sütunu sayısala çevirir.  
**Parametreler:**  
- `column_name` (str): Encode edilecek sütun.  
- `mode` (str): `'label'` veya `'onehot'`.  
  - `label`: Kategori değerlerini 0..n-1 sayısal kodlara dönüştürür.  
  - `onehot`: 0-1 değerleri ile sütunları genişletir (**0-1 garantili**, `dtype=int`).  
