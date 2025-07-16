# 🏗️ Kod Mimarisi ve Algoritma Açıklamaları

Bu dokümanda projenin kod yapısı, algoritma detayları ve implementasyon stratejileri açıklanmaktadır.

## 📁 Proje Yapısı

```
drone_delivery_optimization/
├── main.py                          # Ana program ve orkestrasyon
├── src/                            # Kaynak kodlar
│   ├── drone.py                    # Drone sınıfı ve temel operasyonlar
│   ├── delivery_point.py           # Teslimat noktası tanımları
│   ├── no_fly_zone.py             # Uçuş yasağı bölgeleri
│   ├── graph_builder.py           # Graf oluşturma ve yönetimi
│   ├── astar.py                   # A* algoritması implementasyonu
│   ├── csp_solver.py              # CSP çözücü algoritması
│   ├── genetic_algorithm.py       # Genetic Algorithm implementasyonu
│   ├── multi_trip_planner.py      # Multi-trip sistemi (Ana yenilik)
│   ├── detailed_reporter.py       # Kapsamlı raporlama sistemi
│   ├── visualizer.py              # Görselleştirme modülü
│   └── data_loader.py             # Veri yükleme ve işleme
├── data/                          # Test verileri
└── results/                       # Çıktılar (otomatik oluşur)
```

## 🔧 Ana Sınıflar ve Modüller

### 1. Multi-Trip Planner (Ana Yenilik) 🔄

**En önemli yenilik - PDF'deki şarj sistemini implemente eder**

```python
class MultiTripPlanner:
    def __init__(self, drones, deliveries, no_fly_zones, graph):
        self.time_horizon = 480        # 8 saat operasyon
        self.charge_time_per_cycle = 30 # 30dk şarj süresi
        self.battery_threshold = 0.3   # %30'da şarj et
```

**Kritik İyileştirme - Çoklu paket yüklemesi:**
```python
# TÜM PAKETLERİ BAŞTA AL (PDF'deki gibi)
total_trip_weight = sum(d.weight for d in trip_deliveries)
drone.current_weight = total_trip_weight

# Her teslimat noktasına git ve paketi bırak
for delivery in trip_deliveries:
    drone.current_weight -= delivery.weight  # Ağırlık azalt
```

### 2. Drone Sınıfı (`drone.py`)

```python
class Drone:
    def __init__(self, id, max_weight, battery, speed, start_pos):
        self.id = id                    # Benzersiz kimlik
        self.max_weight = max_weight    # Maksimum yük kapasitesi (kg)
        self.battery = battery          # Batarya kapasitesi (mAh)
        self.speed = speed              # Uçuş hızı (m/s)
        self.current_weight = 0.0       # Mevcut yük
        self.deliveries = []            # Tamamlanan teslimatlar
```

### 3. A* Algoritması (`astar.py`) 🎯

PDF'deki formülü kullanır:
```python
# Heuristik fonksiyon
h = distance + no_fly_zone_penalty
# f-score hesaplama
f_score = g_score + h_score
```

### 4. Genetic Algorithm (`genetic_algorithm.py`) 🧬

PDF'deki fitness formülünü kullanır:
```python
# Fitness fonksiyonu
fitness = (teslim_edilen_sayısı × 500) - (enerji_tüketimi × 0.1) - (kural_ihlali × 1000)
```

## 🔄 Algoritma Karşılaştırması

### Zaman Karmaşıklığı

| Algoritma | Big O | Açıklama |
|-----------|-------|----------|
| **A*** | O(b^d) | b=branching factor, d=depth |
| **CSP** | O(d^n) | d=domain size, n=variables |
| **GA** | O(g×p×f) | g=generations, p=population, f=fitness |
| **Multi-Trip** | O(t×d×n²) | t=time slots, d=drones, n=deliveries |

### Performans Karakteristikleri

#### Multi-Trip Planner (Ana Yenilik)
- **Avantajlar**: %100 teslimat, gerçekçi model, şarj sistemi
- **Kullanım**: Operasyonel drone filo yönetimi
- **Sonuç**: %55 → %100 teslimat oranı

#### A* Algoritması
- **Avantajlar**: Deterministik, hızlı
- **Dezavantajlar**: Tek-tur, sınırlı kapasite kullanımı

## 🚀 Kritik İyileştirmeler

### 1. Multi-Package Loading Sistemi

**Problem**: Drone'lar tek paket alıp teslim ediyordu.

**Çözüm**:
```python
# ÖNCESİ (Yanlış):
for each package:
    take_package() -> deliver() -> return_to_base()

# SONRASI (Doğru):
packages = select_packages_up_to_capacity()
take_all_packages()
for each delivery_location:
    drop_package()
return_to_base()
```

### 2. Şarj Döngüsü Sistemi

**Problem**: Drone'lar tek kullanımlıktı.

**Çözüm**:
```python
while time < 8_hours:
    if battery < 30%:
        return_to_base()
        charge(30_minutes)
    else:
        plan_and_execute_delivery_trip()
```

## 📊 Ana Program Akışı (`main.py`)

```python
def main():
    # 1. Veri yükleme
    drones, deliveries, no_fly_zones = load_data(args.data)
    
    # 2. Graf oluşturma
    graph = DeliveryGraph(drones, deliveries, no_fly_zones)
    
    # 3. Algoritma çalıştırma
    results = {}
    if args.algorithm in ['multitrip', 'all']:
        results['Multi-Trip'] = run_multi_trip_optimization(...)
    
    # 4. Görselleştirme
    if args.visualize:
        visualize_results(drones, deliveries, no_fly_zones, results)
    
    # 5. Rapor oluştur
    create_comprehensive_report(results, drones, deliveries, no_fly_zones)
```

## 🎯 Optimizasyon Stratejileri

### Multi-Trip Paket Seçimi (Greedy)
```python
# Öncelik sıralaması
sorted_deliveries = sorted(deliveries, 
                          key=lambda x: (x.priority, -x.weight), 
                          reverse=True)

# Kapasiteye kadar seç
for delivery in sorted_deliveries:
    if total_weight + delivery.weight <= drone.max_weight:
        selected_deliveries.append(delivery)
```

### Enerji Yönetimi
```python
# %30'da şarj et
if drone.battery < drone.max_battery * 0.3:
    return_to_base_and_charge()

# %70 güvenlik marjı
if estimated_energy <= drone.battery * 0.7:
    accept_delivery()
```

## 🔍 Debug Sistemi

Multi-Trip Planner detaylı debug bilgileri verir:

```python
print(f"🎯 Drone {drone.id} için paket seçimi (Kapasite: {drone.max_weight}kg):")
print(f"    ✅ Paket {delivery.id} seçildi: {delivery.weight:.1f}kg")
print(f"    📊 Tur özeti: {len(selected)} paket, {total_weight:.1f}kg")
```

## 🎨 Görselleştirme Elemanları

- **Drone'lar**: Mavi kareler (🔵)
- **Teslimatlar**: Renkli daireler (öncelik bazında)
- **No-Fly Zones**: Kırmızı saydam alanlar
- **Rotalar**: Renkli çizgiler

## 📊 Raporlama Sistemi

### DetailedReporter Sınıfı
```python
class DetailedReporter:
    def create_comprehensive_report(self, all_results, drones, deliveries):
        # 1. Problem tanımı
        # 2. Algoritma sonuçları
        # 3. Drone performans analizi
        # 4. Zaman karmaşıklığı analizi
        # 5. Öneriler
```

## ⚙️ Konfigürasyon

### Multi-Trip Parametreleri
```python
self.time_horizon = 480          # 8 saat (dakika)
self.charge_time_per_cycle = 30  # 30 dakika şarj
self.battery_threshold = 0.3     # %30'da şarj et
self.max_packages_per_trip = 8   # Tur başına max paket
```

## 🔒 Hata Yönetimi

### Sonsuz Döngü Koruması
```python
stuck_counter = 0
while remaining_deliveries and current_time < time_horizon:
    if not progress_made:
        stuck_counter += 1
        if stuck_counter >= 10:
            break  # Simülasyonu sonlandır
        current_time += 30  # Zaman ilerlet
```

## 🔄 Modüler Tasarım

### Yeni Algoritma Ekleme
1. Yeni algoritma sınıfı oluştur
2. main.py'ye entegre et
3. Standart sonuç formatı döndür

### Tasarım Prensipleri
- **Single Responsibility**: Her sınıf tek sorumluluk
- **Open/Closed**: Yeni algoritmalar için açık
- **Interface Consistency**: Tüm algoritmalar aynı format

## 📈 Performance Optimizasyonları

### Graf Optimizasyonu
```python
self.adjacency_list = defaultdict(list)  # Memory efficient
self.distance_cache = {}  # Distance caching
```

### A* Optimizasyonları
```python
# Priority queue ile heap kullanımı
import heapq
# Heuristic caching
heuristic_cache = {}
```

## 🧪 Test Stratejileri

### Unit Tests
```python
def test_drone_can_carry():
    drone = Drone(1, 5.0, 10000, 8.0, (0, 0))
    assert drone.can_carry(3.0) == True
```

### Performance Tests
```python
def test_scalability():
    # 50+ teslimat < 1 dakika hedefi
    assert execution_time < 60
```

---

Bu mimari, ölçeklenebilir ve maintainable bir sistem sağlar. Multi-trip sistemi ile %100 teslimat oranı elde edilmiştir.
