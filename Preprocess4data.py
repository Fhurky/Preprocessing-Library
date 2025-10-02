import pandas as pd
import numpy as np

class Preprocessor:
    def __init__(self, csv_file_path=None):
        """
        İhtiyaç duyulan tüm parametreler burada tanımlanmalıdır.
        """
        self.data = None
        self.header = None

        if csv_file_path is not None:
            self.load_csv(csv_file_path)
    
    def load_csv(self, file_path):
        """
        CSV dosyasını okur ve self.data ile self.header'a kaydeder.
        Kodlama hatası durumunda alternatif kodlamaları dener.
        """
        encodings = ['utf-8', 'latin-1', 'windows-1254']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                self.data = df
                self.header = list(df.columns)
                return True
            except FileNotFoundError:
                # Dosya bulunamadıysa hemen False döndür, diğer kodlamaları deneme.
                return False
            except Exception:
                # Başka bir hata (örn: kodlama hatası) olursa, sıradaki kodlamayı dene.
                continue
        
        # Tüm kodlamalar başarısız olursa False döndür.
        return False
    
    def save_csv(self, file_name="processed_data.csv", path=None, index=False):
        """
        DataFrame'i CSV olarak kaydeder.
        
        file_name: Kaydedilecek dosya ismi (örn: 'my_data.csv')
        path: Dosya yolu, eğer None ise sadece file_name kullanılır
        index: CSV'ye index yazılsın mı?
        """
        if self.data is None:
            print("Veri yüklenmedi, kaydedilemez.")
            return
        
        if path:
            full_path = f"{path}/{file_name}"
        else:
            full_path = file_name
        
        self.data.to_csv(full_path, index=index)
        print(f"CSV kaydedildi: {full_path}")
   
        
    def preview(self, n=-1):
        """
        CSV dosyasının ilk n satırı gösterilir.
        """
        if n == 0:
            print(self.data)
            return 
        print(self.data.head(n))
        
    @staticmethod
    def guess_column_type(series: pd.Series, cat_threshold: float = 0.4, error_tolerance: float = 0.09):
        """
        Sütunun tipini tahmin eder: numeric, datetime, boolean, categorical, string.
        Bu versiyon, her bir benzersiz değerin frekansını hata toleransı ile karşılaştırır.
        
        Parametreler:
        series: Tahmin edilecek Pandas Serisi.
        cat_threshold: Kategorik olarak kabul edilecek maksimum benzersiz değer oranı.
        error_tolerance: Bir değerin anomali olarak kabul edilmesi için minimum frekans eşiği.
                        Bu eşiğin altındaki değerler veri hatası olarak kabul edilir.
        """
        series_cleaned = series.dropna().astype(str).str.strip().str.lower()
        if series_cleaned.empty:
            return "string"

        # 1. Boolean Kontrolü
        bool_candidates = {"true", "false", "0", "1", "yes", "no"}
        unique_vals = set(series_cleaned.unique())
        if unique_vals.issubset(bool_candidates) and len(unique_vals) <= 2:
            return "boolean"

        # 2. Datetime Kontrolü
        possible_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y',
                            '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S']
        for fmt in possible_formats:
            try:
                converted_series = pd.to_datetime(series, format=fmt, errors='raise')
                if not converted_series.isnull().any():
                    return "datetime"
            except (ValueError, TypeError):
                continue

        # 3. Numeric Kontrolü
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        else:
            try:
                if series.astype(float).notna().all():
                    return "numeric"
            except (ValueError, TypeError):
                pass
                
        # 4. Kategorik ve String Ayrımı (Yeni ve sadeleştirilmiş mantık)
        nunique_ratio = series.nunique(dropna=True) / len(series)
        if nunique_ratio <= cat_threshold:
            value_counts = series.value_counts(normalize=True, dropna=True)
            # Eğer herhangi bir değerin frekansı hata toleransından düşükse, string kabul et.
            if (value_counts < error_tolerance).any():
                return "string"
            else:
                return "categorical"

        # Tüm koşullar sağlanamazsa string olarak kabul et
        return "string"


    def check_column(self, column_name=None, cat_threshold_value=0.4, error_rate=0.09):
        """
        Bir sütunun temel istatistiklerini ve özelliklerini gösterir.
        Sütun tipi tahmini yapılarak analiz edilir.
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        if column_name not in self.header:
            print(f"'{column_name}' isimli bir sütun bulunamadı.")
            return
        
        col = self.data[column_name]
        total_count = len(col)
        
        print(f"\n📌 Sütun: {column_name}")
        
        # Tip tahmini
        col_type = self.guess_column_type(col, cat_threshold=cat_threshold_value, error_tolerance=error_rate)
        print(f"📄 Tahmini Tip: {col_type}")
        
        # Eksik veri analizi
        missing_count = col.isna().sum()
        missing_ratio = (missing_count / total_count) * 100
        print(f"❌ Eksik veri sayısı: {missing_count} ({missing_ratio:.2f}%)")
        
        # Eşsiz değer sayısı
        unique_count = col.nunique(dropna=True)
        unique_ratio = (unique_count / total_count) * 100
        print(f"🔢 Eşsiz değer sayısı: {unique_count} ({unique_ratio:.2f}%)")
        
        # En çok tekrar eden değerler
        print("\n🏆 En çok tekrar eden 5 değer:")
        print(col.value_counts(dropna=False).head(5))
        
        # Tip bazlı istatistikler
        if col_type == "numeric":
            print("\n📊 Sayısal İstatistikler:")
            mean_val = col.mean()
            std_val = col.std()
            print(f"Ortalama: {mean_val:.2f}")
            print(f"Medyan: {col.median():.2f}")
            print(f"Std Sapma: {std_val:.2f}")
            print(f"Min: {col.min()}")
            print(f"Max: {col.max()}")

            # Z-skor ile aykırı değer sayısı
            z_threshold = 3
            if std_val > 0:
                z_scores = (col - mean_val) / std_val
                outliers = (z_scores.abs() > z_threshold).sum()
            else:
                outliers = 0

            print(f"Aykırı değer sayısı (Z>{z_threshold}): {outliers}")
        
        elif col_type == "string":
            lengths = col.dropna().apply(len)
            print("\n📝 Metin İstatistikleri:")
            print(f"Ortalama metin uzunluğu: {lengths.mean():.2f}")
            print(f"En kısa metin uzunluğu: {lengths.min()}")
            print(f"En uzun metin uzunluğu: {lengths.max()}")
        
        elif col_type == "datetime":
            parsed = pd.to_datetime(col, errors="coerce")
            print("\n📅 Tarih İstatistikleri:")
            print(f"En eski tarih: {parsed.min()}")
            print(f"En yeni tarih: {parsed.max()}")
            print(f"Tarih aralığı (gün): {(parsed.max() - parsed.min()).days}")
            print(f"En sık görülen tarih: {parsed.mode().iloc[0]}")
        
        elif col_type == "boolean":
            # True/False sayısını hesapla (0/1 veya "true"/"false" olabilir)
            bool_series = col.dropna().apply(lambda x: str(x).lower() in {"true","1","yes"})
            true_count = bool_series.sum()
            false_count = len(bool_series) - true_count
            print("\n🔘 Boolean İstatistikleri:")
            print(f"True sayısı: {true_count} (%{true_count/len(col)*100:.1f})")
            print(f"False sayısı: {false_count} (%{false_count/len(col)*100:.1f})")
        
        elif col_type == "categorical":
            print("\n🏷️ Kategorik İstatistikler:")
            print(f"Benzersiz değer sayısı: {col.nunique()}")
            print(f"En sık görülen: {col.mode().iloc[0]}")
            print("Değer dağılımı:")
            print(col.value_counts(normalize=True).head(10).apply(lambda x: f"%{x*100:.1f}"))
        
        else:
            print("\n⚠️ Karışık Tipli Sütun:")
            print(col.apply(type).value_counts())


    def check_csv(self, z_threshold=3):
        """
        CSV hakkında genel bilgiler verir:
        - Toplam satır ve sütun sayısı
        - Sütun isimleri
        - Sütun veri tipleri
        - Eksik değer oranı
        - Benzersiz değer oranı
        - Sayısal sütunlarda aykırı değer sayısı (Z-skor yöntemi)
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        print("=== Genel Bilgiler ===")
        print(f"Toplam satır sayısı: {self.data.shape[0]}")
        print(f"Toplam sütun sayısı: {self.data.shape[1]}")
        print(f"Sütun isimleri: {list(self.data.columns)}")
        
        print("\n=== Sütun Detayları ===")
        for col_name in self.header:
            col = self.data[col_name]
            total = len(col)
            
            missing_count = col.isna().sum()
            missing_ratio = (missing_count / total) * 100
            
            unique_count = col.nunique(dropna=True)
            unique_ratio = (unique_count / total) * 100
            
            print(f"\n📌 Sütun: {col_name}")
            print(f"  Veri tipi: {col.dtype}")
            print(f"  Eksik değer: {missing_count} ({missing_ratio:.2f}%)")
            print(f"  Benzersiz değer: {unique_count} ({unique_ratio:.2f}%)")
            
            if pd.api.types.is_numeric_dtype(col):
                # Z-skor ile aykırı değer sayısı
                mean_val = col.mean()
                std_val = col.std()
                if std_val > 0:
                    z_scores = (col - mean_val) / std_val
                    outliers = ((z_scores.abs() > z_threshold).sum())
                else:
                    outliers = 0
                print(f"  Aykırı değer sayısı (Z>{z_threshold}): {outliers}")

    def standard_scale(self, column_name):
        """
        Belirtilen sayısal sütunu standartlaştırır: (x - mean) / std
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        if column_name not in self.header:
            print(f"'{column_name}' isimli bir sütun bulunamadı.")
            return
        
        col = self.data[column_name]
        if not pd.api.types.is_numeric_dtype(col):
            print(f"'{column_name}' sayısal bir sütun değil.")
            return
        
        mean_val = col.mean()
        std_val = col.std()
        
        if std_val == 0:
            print(f"'{column_name}' sütununda standart sapma 0, ölçekleme yapılamıyor.")
            return
        
        # Standartlaştırma
        self.data[column_name] = (col - mean_val) / std_val
        print(f"'{column_name}' sütunu standart ölçeklendi (mean=0, std=1 olacak şekilde).")

    def minmax_scale(self, column_name, feature_range=(0, 1)):
        """
        Belirtilen sayısal sütunu min-max ölçekler.
        feature_range: ölçek aralığı (min, max)
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        if column_name not in self.header:
            print(f"'{column_name}' isimli bir sütun bulunamadı.")
            return
        
        col = self.data[column_name]
        if not pd.api.types.is_numeric_dtype(col):
            print(f"'{column_name}' sayısal bir sütun değil.")
            return
        
        col_min = col.min()
        col_max = col.max()
        
        if col_max == col_min:
            print(f"'{column_name}' sütununda tüm değerler aynı, ölçekleme yapılamıyor.")
            return
        
        min_range, max_range = feature_range
        self.data[column_name] = ((col - col_min) / (col_max - col_min)) * (max_range - min_range) + min_range
        print(f"'{column_name}' sütunu min-max ölçeklendi ({min_range}-{max_range} aralığında).")

    def fill_missing(self, column_name, method="mean", value=None):
        """
        Belirtilen sütundaki eksik değerleri doldurur.
        
        method: 'mean', 'median', 'mode', 'constant'
        value: method='constant' ise doldurulacak değer
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        if column_name not in self.header:
            print(f"'{column_name}' isimli sütun bulunamadı.")
            return
        
        col = self.data[column_name]
        
        if col.isna().sum() == 0:
            print(f"'{column_name}' sütununda eksik değer bulunmuyor.")
            return
        
        if method == "mean":
            if pd.api.types.is_numeric_dtype(col):
                fill_val = col.mean()
            else:
                print(f"'{column_name}' sayısal değil, mean ile dolduramazsınız.")
                return
        elif method == "median":
            if pd.api.types.is_numeric_dtype(col):
                fill_val = col.median()
            else:
                print(f"'{column_name}' sayısal değil, median ile dolduramazsınız.")
                return
        elif method == "mode":
            fill_val = col.mode().iloc[0]
        elif method == "constant":
            if value is None:
                print("Lütfen constant metodunda doldurulacak bir değer belirtin.")
                return
            fill_val = value
        else:
            print(f"Geçersiz method: {method}. ('mean', 'median', 'mode', 'constant')")
            return
        
        self.data[column_name].fillna(fill_val, inplace=True)

    def drop_column(self, columns):
        """
        Verilen sütun(lar)ı veri setinden düşürür.
        
        columns: str (tek sütun) veya list (birden fazla sütun)
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return

        # Tek sütun string olarak verilmişse listeye çevir
        if isinstance(columns, str):
            columns = [columns]
        
        # Mevcut olmayan sütunları kontrol et
        existing_cols = [col for col in columns if col in self.data.columns]
        missing_cols = [col for col in columns if col not in self.data.columns]
        
        if missing_cols:
            print(f"Uyarı: Aşağıdaki sütunlar bulunamadı ve düşürülemedi: {missing_cols}")
        
        if existing_cols:
            self.data.drop(columns=existing_cols, inplace=True)
            print(f"Sütun(lar) düşürüldü: {existing_cols}")

    def handle_outliers(self, column_name, method="drop", z_threshold=3, fill_value=None):
        """
        Belirtilen sütundaki aykırı değerleri işler.
        
        method: 'drop', 'cap', 'impute'
        z_threshold: aykırı değer tespiti için Z-skor eşiği (default 3)
        fill_value: method='impute' ise doldurulacak değer (default medyan)
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        if column_name not in self.header:
            print(f"'{column_name}' sütunu bulunamadı.")
            return
        
        col = self.data[column_name]
        
        if not pd.api.types.is_numeric_dtype(col):
            print(f"'{column_name}' sayısal bir sütun değil.")
            return
        
        mean_val = col.mean()
        std_val = col.std()
        
        if std_val == 0:
            print(f"'{column_name}' sütununda standart sapma 0, aykırı değer yok.")
            return
        
        z_scores = (col - mean_val) / std_val
        outlier_idx = z_scores[ z_scores.abs() > z_threshold ].index
        
        if len(outlier_idx) == 0:
            print(f"'{column_name}' sütununda Z>{z_threshold} aykırı değer bulunamadı.")
            return
        
        if method == "drop":
            self.data.drop(index=outlier_idx, inplace=True)
            print(f"'{column_name}' sütunundaki {len(outlier_idx)} aykırı değer satırları drop edildi.")
        
        elif method == "cap":
            upper = mean_val + z_threshold * std_val
            lower = mean_val - z_threshold * std_val
            self.data.loc[col > upper, column_name] = upper
            self.data.loc[col < lower, column_name] = lower
            print(f"'{column_name}' sütunundaki {len(outlier_idx)} aykırı değer cap yöntemiyle sınırlandırıldı.")
        
        elif method == "impute":
            if fill_value is None:
                fill_value = col.median()
            self.data.loc[outlier_idx, column_name] = fill_value
            print(f"'{column_name}' sütunundaki {len(outlier_idx)} aykırı değer impute yöntemiyle dolduruldu (değer={fill_value}).")
        
        else:
            print(f"Geçersiz method: {method}. ('drop', 'cap', 'impute')")

    def encode_column(self, column_name, mode="label"):
        """
        Kategorik sütunu sayısala çevirir.
        
        mode: 'label' veya 'onehot'
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return
        
        if column_name not in self.header:
            print(f"'{column_name}' sütunu bulunamadı.")
            return
        
        col = self.data[column_name]
        
        if pd.api.types.is_numeric_dtype(col):
            print(f"'{column_name}' zaten sayısal.")
            return
        
        if mode == "label":
            self.data[column_name] = col.astype('category').cat.codes
            print(f"'{column_name}' sütununa label encoding uygulandı.")
        
        elif mode == "onehot":
            onehot_df = pd.get_dummies(col, prefix=column_name, dtype=int)  # 0-1 garantili
            self.data = pd.concat([self.data.drop(columns=[column_name]), onehot_df], axis=1)
            self.header = list(self.data.columns)
            print(f"'{column_name}' sütununa one-hot encoding uygulandı.")
        
        else:
            print(f"Geçersiz mode: '{mode}'. 'label' veya 'onehot' olmalı.")

    def split_data(self, target_column, train_size=0.7, val_size=0.15, random_state=None):
        """
        Veri setini Train, Validation (opsiyonel) ve Test olarak ayırır, X ve y olarak böler.

        Parametreler:
        - target_column: hedef sütun (y)
        - train_size: Train seti oranı
        - val_size: Validation seti oranı (0 ise validation set oluşturulmaz)
        - random_state: seed

        Döndürür:
        - train_X, train_y, val_X, val_y, test_X, test_y
        """
        if self.data is None:
            print("Veri yüklenmedi.")
            return None

        if target_column not in self.data.columns:
            print(f"Hedef sütun '{target_column}' bulunamadı.")
            return None

        if train_size + val_size > 1.0:
            print("train_size + val_size toplamı 1'den küçük veya eşit olmalı.")
            return None

        X = self.data.drop(columns=[target_column]).copy()
        y = self.data[target_column].copy()

        # Shuffle
        np.random.seed(random_state)
        shuffled_idx = np.random.permutation(len(X))
        X = X.iloc[shuffled_idx].reset_index(drop=True)
        y = y.iloc[shuffled_idx].reset_index(drop=True)

        n_total = len(X)
        n_train = int(n_total * train_size)
        n_val = int(n_total * val_size)

        # Slice ile ayır
        X_train = X.iloc[:n_train]
        y_train = y.iloc[:n_train]

        X_test = X.iloc[n_train+n_val:]
        y_test = y.iloc[n_train+n_val:]

        if n_val > 0:
            X_val = X.iloc[n_train:n_train+n_val]
            y_val = y.iloc[n_train:n_train+n_val]
            print(f"Train: {X_train.shape}, Validation: {X_val.shape}, Test: {X_test.shape}")
            return X_train, y_train, X_val, y_val, X_test, y_test
        else:
            print(f"Train: {X_train.shape}, Test: {X_test.shape} (Validation yok)")
            return X_train, y_train, X_test, y_test

