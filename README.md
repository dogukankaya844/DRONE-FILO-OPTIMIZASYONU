# 🚁 Drone Filo Optimizasyonu

**Çok Kısıtlı Ortamlarda Dinamik Teslimat Planlaması**

Kocaeli Üniversitesi TBL331 - Yazılım Geliştirme Laboratuvarı II Projesi

## 📋 Proje Özeti

Bu proje, enerji limitleri ve uçuş yasağı bölgeleri gibi dinamik kısıtlar altında çalışan drone'lar için en uygun teslimat rotalarının belirlenmesini sağlayan bir sistem geliştirir. 

### 🎯 Ana Özellikler

- **4 Farklı Algoritma**: A*, CSP, Genetic Algorithm, Multi-Trip Planner
- **Multi-Trip Sistemi**: Drone'lar şarj olup tekrar teslimat yapabilir
- **Dinamik Kısıtlar**: No-fly zone'lar ve zaman pencereleri
- **Gerçek Zamanlı Optimizasyon**: 8 saatlik operasyonel simülasyon
- **Kapsamlı Görselleştirme**: Haritalar, grafikler ve performans analizi

### 📊 Performans Sonuçları

| Algoritma | Teslimat Oranı | Çalışma Süresi | Özel Özellik |
|-----------|----------------|----------------|--------------|
| A* | %55 | ~0.001s | Hızlı tek-tur |
| CSP | %20-30 | ~0.1s | Kısıt odaklı |
| GA | %40-50 | ~0.5s | Evrimsel optimizasyon |
| **Multi-Trip** | **%100** | ~0.001s | **Çoklu tur + şarj** |

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Temel Çalıştırma
```bash
# En iyi sonuç için (önerilen)
python main.py --algorithm multitrip --visualize

# Tüm algoritmaları karşılaştır
python main.py --algorithm all --visualize

# Büyük scenario testi (50 teslimat)
python main.py --algorithm multitrip --data data/scenario2_data.txt --visualize
```

### 3. Sonuçları İncele
- **Grafikler**: `results/` klasöründeki PNG dosyaları
- **Raporlar**: `results/comprehensive_report.txt`
- **Drone Performansı**: Terminal çıktısında detaylı analiz

## 📁 Proje Yapısı

```
drone_delivery_optimization/
├── 📄 README.md                    # Bu dosya
├── 📄 KULLANIM_REHBERI.md          # Detaylı kullanım kılavuzu
├── 📄 KOD_MIMARISI.md              # Kod yapısı ve algoritma açıklamaları
├── 📄 main.py                      # Ana program
├── 📄 requirements.txt             # Python bağımlılıkları
├── 📁 src/                         # Kaynak kodlar
│   ├── 🔧 multi_trip_planner.py    # Multi-trip sistemi (Ana yenilik)
│   ├── 🎯 astar.py                 # A* algoritması
│   ├── 🧩 csp_solver.py            # CSP çözücü
│   ├── 🧬 genetic_algorithm.py     # Genetic Algorithm
│   ├── 📊 detailed_reporter.py     # Detaylı raporlama
│   ├── 🎨 visualizer.py            # Görselleştirme
│   └── 🚁 drone.py                 # Drone sınıfı
├── 📁 data/                        # Test verileri
│   ├── sample_data.txt             # Scenario 1 (5 drone, 20 teslimat)
│   └── scenario2_data.txt          # Scenario 2 (10 drone, 50 teslimat)
└── 📁 results/                     # Çıktılar (otomatik oluşur)
```

## 🎮 Kullanım Örnekleri

### Temel Komutlar
```bash
# Sadece multi-trip (en hızlı)
python main.py --algorithm multitrip

# Görselleştirme ile
python main.py --algorithm multitrip --visualize

# Farklı veri seti ile
python main.py --data data/scenario2_data.txt

# Genetic Algorithm parametreleri
python main.py --algorithm ga --generations 200
```

### Çıktı Dosyaları
- `multitrip_routes.png` - Drone rotalarının haritası
- `performance_comparison.png` - Algoritma karşılaştırması
- `comprehensive_report.txt` - Detaylı performans analizi

## 🔧 Algoritma Detayları

### Multi-Trip Planner (Ana Yenilik)
- **Problem**: PDF'de drone'lar tek kullanımlıktı, %55 teslimat oranı
- **Çözüm**: Drone'lar şarj olup tekrar kullanılabiliyor
- **Sonuç**: %100 teslimat oranı, gerçekçi operasyonel model

### Teknik Özellikler
- **Çoklu Paket Yüklemesi**: Kapasite dolana kadar paket alır
- **Akıllı Şarj Yönetimi**: %30 bataryada otomatik şarj
- **Dinamik Zaman Yönetimi**: 8 saatlik operasyon simülasyonu
- **Öncelik Optimizasyonu**: Yüksek öncelikli teslimatlar önce

## 📈 Performans Analizi

### Scenario 1 (20 Teslimat)
- **Multi-Trip**: 20/20 teslimat (%100) - 12 tur
- **A***: 11/20 teslimat (%55) - 5 tur
- **GA**: 8/20 teslimat (%40) - genetik evrim

### Scenario 2 (50 Teslimat)
- **Skalabilite**: Büyük problemlerde de verimli
- **Performans**: <1 dakika çalışma süresi hedefi

## 🛠️ Geliştirici Notları

### Kritik İyileştirmeler
1. **Multi-Package Loading**: Tek turda birden fazla paket
2. **Şarj Döngüleri**: Gerçekçi operasyonel model
3. **Esnek Zaman Penceresi**: Geç teslimat toleransı
4. **Sonsuz Döngü Koruması**: Güvenli simülasyon

### Zaman Karmaşıklığı
- **A***: O(b^d) - branch factor × depth
- **CSP**: O(d^n) - domain × variables  
- **GA**: O(g×p×f) - generations × population × fitness
- **Multi-Trip**: O(t×d×n²) - time × drones × deliveries

## 📝 Lisans ve Katkı

Bu proje Kocaeli Üniversitesi TBL331 dersi kapsamında geliştirilmiştir.

## 🆘 Destek

Sorun yaşıyorsanız:
1. `KULLANIM_REHBERI.md` dosyasını inceleyin
2. `KOD_MIMARISI.md` ile algoritmaları anlayın
3. Terminal çıktısındaki hata mesajlarını kontrol edin

---

**🎉 Proje Başarıyla Tamamlandı!**  
*Multi-trip sistemi ile %100 teslimat oranı elde edildi!*
