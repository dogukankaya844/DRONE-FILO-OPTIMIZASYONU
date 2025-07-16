"""
Veri üreteci - Rastgele drone, teslimat noktası ve no-fly zone oluşturmak için
Bu dosya, algoritmaların test edilmesi için gerçekçi ve rastgele veri setleri sağlar. Böylece kullanıcılar, farklı zorluk seviyelerinde senaryolar oluşturarak CSP, Genetik Algoritma veya A* gibi algoritmaların performansını ölçebilir.
"""
import random # Rastgele sayı üretmek için
import json # JSON formatında veri kaydetmek/yüklemek için
from typing import List, Dict, Tuple # Tür ipuçları için

class DataGenerator:
    def __init__(self, map_size: Tuple[int, int] = (100, 100)):
        self.map_size = map_size # Haritanın boyutları
        self.min_x, self.min_y = 0, 0 # Minimum koordinatlar
        self.max_x, self.max_y = map_size # Maksimum koordinatlar
        
    def generate_drones(self, count: int) -> List[Dict]:
        """Rastgele drone'lar oluştur"""
        drones = [] # Drone listesi
        
        for i in range(1, count + 1): # Belirtilen sayıda drone oluştur
            drone = {
                "id": i, # Drone kimliği
                "max_weight": round(random.uniform(2.0, 6.0), 1), # Maksimum taşıma kapasitesi
                "battery": random.randint(8000, 20000), # Batarya kapasitesi
                "speed": round(random.uniform(5.0, 12.0), 1), # Uçuş hızı
                "start_pos": (  #Başlangıç pozisyonu
                    random.randint(self.min_x, self.max_x),
                    random.randint(self.min_y, self.max_y)
                )
            }
            drones.append(drone) # Listeye ekle
            
        return drones # Drone listesi döndürülür
        
    def generate_deliveries(self, count: int, time_range: Tuple[int, int] = (0, 120)) -> List[Dict]:
        """Rastgele teslimat noktaları oluştur"""
        deliveries = []
        
        for i in range(1, count + 1):
            # Teslimat için zaman penceresi oluştur
            start_time = random.randint(time_range[0], time_range[1] - 20)
            window_duration = random.randint(20, 60)
            end_time = min(start_time + window_duration, time_range[1])
            
            delivery = {
                "id": i, # Teslimat ID
                "pos": ( # Teslimat pozisyonu
                    random.randint(self.min_x, self.max_x),
                    random.randint(self.min_y, self.max_y)
                ),
                "weight": round(random.uniform(0.5, 5.0), 1), # Paket ağırlığı
                "priority": random.randint(1, 5), # Öncelik seviyesi (1-5)
                "time_window": (start_time, end_time) # Teslimat için zaman aralığı
            }
            deliveries.append(delivery)
            
        return deliveries
        
    def generate_no_fly_zones(self, count: int, time_range: Tuple[int, int] = (0, 120)) -> List[Dict]:
        """Rastgele no-fly zone'lar oluştur"""
        zones = []
        
        for i in range(1, count + 1):
            # Rastgele merkez koordinat belirle
            center_x = random.randint(self.min_x + 20, self.max_x - 20)
            center_y = random.randint(self.min_y + 20, self.max_y - 20)
            
            # Rastgele alan boyutları
            width = random.randint(10, 30)
            height = random.randint(10, 30)
            
            # # Dikdörtgenin 4 köşesi (saat yönüyle)
            coordinates = [
                (center_x - width//2, center_y - height//2),
                (center_x + width//2, center_y - height//2),
                (center_x + width//2, center_y + height//2),
                (center_x - width//2, center_y + height//2)
            ]
            
            # No-fly zone aktif olduğu zaman
            start_time = random.randint(time_range[0], time_range[1] - 30)
            duration = random.randint(30, 90)
            end_time = min(start_time + duration, time_range[1])
            
            zone = {
                "id": i, 
                "coordinates": coordinates, # Koordinat listesi
                "active_time": (start_time, end_time) # Aktiflik zamanı
            }
            zones.append(zone)
            
        return zones
        
    def generate_scenario(self, drone_count: int, delivery_count: int, 
                         zone_count: int, scenario_name: str = "custom") -> Dict:
        """Tam bir senaryo oluştur (drone, teslimat, no-fly zone içeren)"""
        scenario = {
            "name": scenario_name, # Senaryo adı
            "map_size": self.map_size, # Drone listesi
            "drones": self.generate_drones(drone_count), # Teslimat listesi
            "deliveries": self.generate_deliveries(delivery_count),
            "no_fly_zones": self.generate_no_fly_zones(zone_count) # No-fly bölge listesi
        }
        
        return scenario
        
    def save_scenario_to_file(self, scenario: Dict, filename: str):
        """Senaryoyu JSON dosyasına kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scenario, f, indent=2, ensure_ascii=False)
            
    def load_scenario_from_file(self, filename: str) -> Dict:
        """Senaryoyu JSON dosyasından yükle"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def save_scenario_to_txt(self, scenario: Dict, filename: str):
        """Senaryoyu proje gereksinimlerine uygun txt formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Drone bilgileri
            f.write("DRONLAR\n")
            f.write("id,max_weight,battery,speed,start_pos_x,start_pos_y\n")
            for drone in scenario["drones"]:
                f.write(f"{drone['id']},{drone['max_weight']},{drone['battery']},"
                       f"{drone['speed']},{drone['start_pos'][0]},{drone['start_pos'][1]}\n")
            # Teslimat bilgileri
            f.write("\nTESLIMATLAR\n")
            f.write("id,pos_x,pos_y,weight,priority,time_window_start,time_window_end\n")
            for delivery in scenario["deliveries"]:
                f.write(f"{delivery['id']},{delivery['pos'][0]},{delivery['pos'][1]},"
                       f"{delivery['weight']},{delivery['priority']},"
                       f"{delivery['time_window'][0]},{delivery['time_window'][1]}\n")
            # No-fly zone bilgileri
            f.write("\nUCUSA_YASAK_BOLGELER\n")
            f.write("id,coord1_x,coord1_y,coord2_x,coord2_y,coord3_x,coord3_y,coord4_x,coord4_y,active_start,active_end\n")
            for zone in scenario["no_fly_zones"]:
                coords = zone["coordinates"]
                f.write(f"{zone['id']},{coords[0][0]},{coords[0][1]},{coords[1][0]},{coords[1][1]},"
                       f"{coords[2][0]},{coords[2][1]},{coords[3][0]},{coords[3][1]},"
                       f"{zone['active_time'][0]},{zone['active_time'][1]}\n")
                       
    def generate_test_scenarios(self):
        """PDF'deki test senaryolarını oluştur"""
        # Senaryo 1: 5 drone, 20 teslimat, 2 no-fly zone
        scenario1 = self.generate_scenario(5, 20, 2, "Senaryo_1")
        
        # Senaryo 2: 10 drone, 50 teslimat, 5 dinamik no-fly zone
        scenario2 = self.generate_scenario(10, 50, 5, "Senaryo_2")
        
        return scenario1, scenario2
        
    def create_balanced_scenario(self, drone_count: int, delivery_count: int, 
                               zone_count: int) -> Dict:
        """Dengeli bir senaryo oluştur (daha gerçekçi)"""
        # Drone'ları farklı kapasitelerde oluştur
        drones = [] # Drone listesi
        capacity_ranges = [(2.0, 3.0), (3.0, 4.5), (4.5, 6.0)] # Farklı kapasite grupları
        
        for i in range(1, drone_count + 1):
            capacity_range = capacity_ranges[i % len(capacity_ranges)]
            
            drone = {
                "id": i,
                "max_weight": round(random.uniform(*capacity_range), 1),
                "battery": random.randint(10000, 18000),
                "speed": round(random.uniform(6.0, 10.0), 1),
                "start_pos": (
                    random.randint(10, 90),
                    random.randint(10, 90)
                )
            }
            drones.append(drone)
            
        # Teslimatları öncelik dağılımı ile oluştur
        deliveries = [] # Teslimat listesi
        priority_weights = [0.1, 0.2, 0.4, 0.2, 0.1]  # 1-5 öncelik dağılımı
        
        for i in range(1, delivery_count + 1):
            priority = random.choices(range(1, 6), weights=priority_weights)[0]
            
            # Yüksek öncelikli teslimatlar için daha kısa zaman penceresi
            if priority >= 4:
                window_duration = random.randint(15, 30)
            else:
                window_duration = random.randint(30, 60)
                
            start_time = random.randint(0, 120 - window_duration)
            
            delivery = {
                "id": i,
                "pos": (
                    random.randint(5, 95),
                    random.randint(5, 95)
                ),
                "weight": round(random.uniform(0.5, 4.0), 1),
                "priority": priority,
                "time_window": (start_time, start_time + window_duration)
            }
            deliveries.append(delivery)
            
        # No-fly zone'ları stratejik konumlarda oluştur
        zones = self.generate_no_fly_zones(zone_count) # Yasak bölgeler
        
        scenario = {
            "name": "Balanced_Scenario",
            "map_size": self.map_size,
            "drones": drones,
            "deliveries": deliveries,
            "no_fly_zones": zones
        }
        
        return scenario
        
    def print_scenario_stats(self, scenario: Dict):
        """Senaryo hakkında özet istatistikleri yazdırır"""
        print(f"Senaryo: {scenario['name']}")
        print("-" * 40)
        print(f"Harita boyutu: {scenario['map_size']}")
        print(f"Drone sayısı: {len(scenario['drones'])}")
        print(f"Teslimat sayısı: {len(scenario['deliveries'])}")
        print(f"No-fly zone sayısı: {len(scenario['no_fly_zones'])}")
        
        # Drone istatistikleri
        total_capacity = sum(d['max_weight'] for d in scenario['drones'])
        avg_capacity = total_capacity / len(scenario['drones'])
        print(f"Toplam drone kapasitesi: {total_capacity:.1f}kg")
        print(f"Ortalama drone kapasitesi: {avg_capacity:.1f}kg")
        
        # Teslimat istatistikleri
        total_weight = sum(d['weight'] for d in scenario['deliveries'])
        avg_weight = total_weight / len(scenario['deliveries'])
        priority_dist = {}
        for d in scenario['deliveries']:
            priority_dist[d['priority']] = priority_dist.get(d['priority'], 0) + 1
            
        print(f"Toplam teslimat ağırlığı: {total_weight:.1f}kg")
        print(f"Ortalama paket ağırlığı: {avg_weight:.1f}kg")
        print(f"Öncelik dağılımı: {priority_dist}")
        
        # Kapasite analizi
        capacity_utilization = (total_weight / total_capacity) * 100 if total_capacity > 0 else 0
        print(f"Teorik kapasite kullanımı: %{capacity_utilization:.1f}")
        
        if capacity_utilization > 100:
            print("⚠️  Toplam teslimat ağırlığı drone kapasitesini aşıyor!")
        elif capacity_utilization > 80:
            print("⚠️  Yüksek kapasite kullanımı - zorlayıcı senaryo")
        else:
            print("✅ Makul kapasite kullanımı")
