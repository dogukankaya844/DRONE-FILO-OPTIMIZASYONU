# 📚 Drone Filo Optimizasyonu - Kullanım Rehberi

## 🚀 Hızlı Başlangıç

### 1️⃣ Kurulum
```bash
# Projeyi klonlayın veya indirin
cd drone_delivery_optimization

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2️⃣ İlk Test
```bash
# En basit çalıştırma
python main.py

# Önerilen ilk test (görselleştirme ile)
python main.py --algorithm multitrip --visualize
```

## 🎮 Komut Satırı Parametreleri

### Ana Parametreler
```bash
python main.py [PARAMETRELER]
```

| Parametre | Seçenekler | Varsayılan | Açıklama |
|-----------|------------|------------|----------|
| `--algorithm` | `astar`, `csp`, `ga`, `multitrip`, `all` | `all` | Çalıştırılacak algoritma |
| `--data` | Dosya yolu | `data/sample_data.txt` | Kullanılacak veri seti |
| `--visualize` | Flag | Kapalı | Görselleştirme oluştur |
| `--generations` | Sayı | `100` | GA için nesil sayısı |
| `--output` | Klasör | `results` | Çıktı dizini |

### Algoritma Seçenekleri

#### 🎯 A* Algoritması
```bash
python main.py --algorithm astar
```
- **Özellik**: Hızlı, deterministik
- **Sonuç**: ~%55 teslimat oranı
- **Süre**: <0.01 saniye

#### 🧩 CSP (Constraint Satisfaction)
```bash
python main.py --algorithm csp
```
- **Özellik**: Kısıt odaklı çözüm
- **Sonuç**: ~%20-30 teslimat oranı
- **Süre**: ~0.1 saniye

#### 🧬 Genetic Algorithm
```bash
python main.py --algorithm ga --generations 200
```
- **Özellik**: Evrimsel optimizasyon
- **Sonuç**: ~%40-50 teslimat oranı
- **Süre**: ~0.5 saniye

#### 🔄 Multi-Trip Planner (ÖNERİLEN)
```bash
python main.py --algorithm multitrip --visualize
```
- **Özellik**: Çoklu tur + şarj sistemi
- **Sonuç**: ~%100 teslimat oranı
- **Süre**: <0.01 saniye

## 📊 Test Senaryoları

### Scenario 1 - Küçük Problem
```bash
python main.py --data data/sample_data.txt --visualize
```
- **5 drone, 20 teslimat, 3 no-fly zone**
- **Hızlı test ve algoritma karşılaştırması için ideal**

### Scenario 2 - Büyük Problem
```bash
python main.py --data data/scenario2_data.txt --algorithm multitrip
```
- **10 drone, 50 teslimat, 5 no-fly zone**
- **Skalabilite testi ve gerçekçi senaryo**

### Tam Karşılaştırma
```bash
python main.py --algorithm all --visualize --data data/sample_data.txt
```
- **Tüm 4 algoritma birlikte çalışır**
- **Kapsamlı performans analizi**

## 🎨 Görselleştirme

### Görselleştirme Açma
```bash
python main.py --algorithm multitrip --visualize
```

### Oluşan Dosyalar
- `multitrip_routes.png` - Drone rotaları haritası
- `astar_routes.png` - A* rotaları
- `ga_routes.png` - GA rotaları  
- `performance_comparison.png` - Algoritma karşılaştırması
- `ga_fitness_evolution.png` - GA fitness grafiği

### Görselleştirme Özellikleri
- 🟦 **Mavi noktalar**: Drone başlangıç pozisyonları
- 📦 **Renkli noktalar**: Teslimat noktaları (renk = öncelik)
- 🚫 **Kırmızı alanlar**: No-fly zone'lar
- ➡️ **Renkli çizgiler**: Drone rotaları
- 📊 **Yan grafikler**: Performans metrikleri

## 📝 Çıktı Dosyaları

### Rapor Dosyaları
```
results/
├── comprehensive_report.txt         # Kapsamlı analiz
├── optimization_report.txt          # Genel rapor
└── *.png                           # Görselleştirmeler
```

### Comprehensive Report İçeriği
1. **Problem Tanımı**: Drone/teslimat detayları
2. **Algoritma Sonuçları**: Performans karşılaştırması
3. **Drone Performansı**: Her drone'un bireysel analizi
4. **Teslimat Analizi**: Öncelik bazında başarı oranları
5. **Zaman Karmaşıklığı**: Big O analizi
6. **Öneriler**: İyileştirme tavsiyeleri

## 🔧 Sorun Giderme

### Yaygın Hatalar

#### 1. ModuleNotFoundError
```bash
# Çözüm:
pip install -r requirements.txt
```

#### 2. Görselleştirme Açılmıyor
```bash
# macOS için:
brew install python-tk

# Ubuntu için:
sudo apt-get install python3-tk
```

#### 3. Sonsuz Döngü
```bash
# Eğer program donuyorsa Ctrl+C ile durdurun
# Daha kısa test için:
python main.py --algorithm multitrip --data data/sample_data.txt
```

#### 4. Düşük Performans
- **A* %55**: Normal, tek-tur algoritması
- **CSP %20**: Normal, kısıt odaklı
- **GA %40**: Normal, evrimsel
- **Multi-Trip %100**: Beklenen sonuç

### Debug Modu
```bash
# Detaylı çıktı için MultiTripPlanner'ı kullanın
python main.py --algorithm multitrip
```

Bu modda her drone'un paket seçim süreci görünür.

## 📈 Performans Beklentileri

### Scenario 1 (20 teslimat)
| Algoritma | Teslimat | Süre | Tur Sayısı |
|-----------|----------|------|------------|
| A* | 11/20 (%55) | <0.01s | 5 |
| CSP | 4-6/20 (%20-30) | ~0.1s | - |
| GA | 8-10/20 (%40-50) | ~0.5s | - |
| Multi-Trip | 20/20 (%100) | <0.01s | 12 |

### Scenario 2 (50 teslimat)
- **Multi-Trip**: 45-50/50 (%90-100)
- **Süre**: <1 dakika
- **Tur Sayısı**: 25-30

## 🎯 Kullanım Önerileri

### Yeni Başlayanlar İçin
1. İlk önce bu komutu deneyin:
   ```bash
   python main.py --algorithm multitrip --visualize
   ```

2. Sonuçları inceleyin:
   - Terminal çıktısındaki drone raporları
   - `results/` klasöründeki grafikler

3. Farklı algoritmaları karşılaştırın:
   ```bash
   python main.py --algorithm all --visualize
   ```

### İleri Düzey Kullanım
```bash
# Özel parametrelerle GA
python main.py --algorithm ga --generations 500

# Farklı çıktı dizini
python main.py --algorithm multitrip --output my_results

# Büyük veri seti stress testi
python main.py --algorithm multitrip --data data/scenario2_data.txt
```

## 📊 Sonuç Analizi

### Terminal Çıktısında Arama
- **Teslimat Oranı**: `%XX.X` formatında
- **Drone Performansı**: Her drone için tur detayları
- **Kapasite Kullanımı**: `%XX.X kapasite` 

### Başarı Kriterleri
- ✅ **%70+ teslimat**: Başarılı
- ⚠️ **%40-70 teslimat**: Orta
- ❌ **%40 altı teslimat**: Düşük

### Multi-Trip Beklenen Çıktı Örneği
```
🚁 DRONE 1:
   📦 5 teslimat / 3 tur
   📊 Tur özeti: 3 paket, 3.5/4.0kg (%87.5)

📊 GENEL İSTATİSTİKLER:
   - Tamamlanan teslimat: 20/20 (%100.0)
   - Toplam tur sayısı: 12
```

---

Bu rehber ile projeyi etkili bir şekilde kullanabilir ve sonuçları analiz edebilirsiniz! 🚁✨
