"""
Veri yükleme modülü - Dosyalardan drone, teslimat ve no-fly zone verilerini okumak için
DataLoader dosyası, drone teslimat sistemi için gerekli olan drone bilgileri, teslimat noktaları ve no-fly zone (uçuşa yasak bölgeler) verilerini farklı formatlardan yüklemek için kullanılır
"""
import csv # CSV dosyaları için modül
from typing import List, Dict, Tuple  #Tip tanımları için, fonksiyonlarda kullanılacak
from .drone import Drone # Drone sınıfı tanımı içe aktarılıyor
from .delivery_point import DeliveryPoint # Teslimat noktası sınıfı içe aktarılıyor
from .no_fly_zone import NoFlyZone  # No-fly zone sınıfı içe aktarılıyor

class DataLoader:
    def __init__(self):
        pass
        
    def load_from_txt(self, filename: str) -> Tuple[List[Drone], List[DeliveryPoint], List[NoFlyZone]]:
        """Txt dosyasından verileri yükle"""
        drones = [] # Drone objeleri için liste
        deliveries = [] # Teslimat noktaları için liste
        no_fly_zones = [] # Uçuşa yasak bölgeler için liste
        
        current_section = None # Dosya içindeki bölüm bilgisi
        
        with open(filename, 'r', encoding='utf-8') as file: # Dosya UTF-8 kodlamayla açılıyor
            for line in file: # Satır satır dosya okunuyor
                line = line.strip() # Satırdaki boşluk ve yeni satır karakterleri temizle
                
                if not line:
                    continue # Boş satırlar atlanıyor
                    
                # # Bölüm başlıklarına göre mevcut bölümü güncelle
                if line == "DRONLAR":
                    current_section = "drones"
                    continue
                elif line == "TESLIMATLAR":
                    current_section = "deliveries"
                    continue
                elif line == "UCUSA_YASAK_BOLGELER":
                    current_section = "no_fly_zones"
                    continue
                    
                # Header satırlarını (alan adları) atla, 
                if ("id," in line and "max_weight," in line) or \
                   ("id," in line and "pos_x," in line) or \
                   ("id," in line and "coord1_x," in line):
                    continue 
                    
                # Veri satırlarını işle
                if current_section == "drones":
                    drones.append(self._parse_drone_line(line))
                elif current_section == "deliveries":
                    deliveries.append(self._parse_delivery_line(line))
                elif current_section == "no_fly_zones":
                    no_fly_zones.append(self._parse_no_fly_zone_line(line))
                    
        return drones, deliveries, no_fly_zones
        
    def _parse_drone_line(self, line: str) -> Drone:
        """Drone satırını parçalara ayır"""
        parts = line.split(',') # Virgülle ayır
        
        drone_id = int(parts[0]) # Drone ID integer olarak al
        max_weight = float(parts[1])  # Maks ağırlık float olarak al
        battery = int(parts[2])  # Batarya kapasitesi integer olarak al
        speed = float(parts[3]) # Hız float olarak al
        start_pos_x = float(parts[4]) # Başlangıç X koordinatı float olarak al
        start_pos_y = float(parts[5]) # Başlangıç Y koordinatı float olarak al
        # Drone objesi oluştur
        return Drone(drone_id, max_weight, battery, speed, (start_pos_x, start_pos_y))
        
    def _parse_delivery_line(self, line: str) -> DeliveryPoint:
        """Teslimat satırını parse et"""
        parts = line.split(',') # Virgülle ayır
        
        delivery_id = int(parts[0]) # Teslimat ID integer
        pos_x = float(parts[1]) # Konum X float
        pos_y = float(parts[2]) # Konum Y float
        weight = float(parts[3]) # Paket ağırlığı float
        priority = int(parts[4]) # Öncelik integer
        time_window_start = int(parts[5]) # Zaman penceresi başlangıcı int
        time_window_end = int(parts[6]) # Zaman penceresi sonu int
        # Teslimat noktası objesi oluştur
        return DeliveryPoint(delivery_id, (pos_x, pos_y), weight, priority, 
                           (time_window_start, time_window_end))
        
    def _parse_no_fly_zone_line(self, line: str) -> NoFlyZone:
        """No-fly zone satırını parçalara ayır"""
        parts = line.split(',') # Virgülle ayır
        
        zone_id = int(parts[0]) # Bölge ID int
        
        # 4 köşe koordinatlarını sırayla al
        coordinates = []
        for i in range(1, 9, 2):  # (x1,y1), (x2,y2), (x3,y3), (x4,y4)
            x = float(parts[i])
            y = float(parts[i + 1])
            coordinates.append((x, y))
            
        active_start = int(parts[9]) # Aktif başlangıç zamanı int
        active_end = int(parts[10]) # Aktif bitiş zamanı int
        
        return NoFlyZone(zone_id, coordinates, (active_start, active_end))
        
    def load_python_data(self, drones_data: List[Dict], deliveries_data: List[Dict], 
                        no_fly_zones_data: List[Dict]) -> Tuple[List[Drone], List[DeliveryPoint], List[NoFlyZone]]:
        """Python dictionary'lerinden verileri yükle"""
        drones = []
        deliveries = []
        no_fly_zones = []
        
        # Drone dictlerinden Drone objeleri oluştur
        for drone_data in drones_data:
            drone = Drone(
                id=drone_data["id"],
                max_weight=drone_data["max_weight"],
                battery=drone_data["battery"],
                speed=drone_data["speed"],
                start_pos=drone_data["start_pos"]
            )
            drones.append(drone)
            
        # Teslimat dictlerinden DeliveryPoint objeleri oluştur
        for delivery_data in deliveries_data:
            # Veri formatı tutarsızlığını düzelt
            weight = delivery_data.get("weight", delivery_data.get("ağırlık", 0))
            priority = delivery_data.get("priority", delivery_data.get("öncelik", 1))
            time_window = delivery_data.get("time_window", delivery_data.get("zaman_penceresi", (0, 60)))
            
            # Virgüllü sayıları düzelt
            if isinstance(weight, str):
                weight = float(weight.replace(',', '.'))
                
            delivery = DeliveryPoint(
                id=delivery_data["id"],
                pos=delivery_data["pos"],
                weight=weight,
                priority=priority,
                time_window=time_window
            )
            deliveries.append(delivery)
            
         # No-fly zone dictlerinden NoFlyZone objeleri oluştur
        for zone_data in no_fly_zones_data:
            coordinates = zone_data.get("coordinates", zone_data.get("koordinatlar", []))
            active_time = zone_data.get("active_time", zone_data.get("etkin_zaman", (0, 120)))
            zone_id = zone_data.get("id", zone_data.get("kimlik", 0))
            
            zone = NoFlyZone(
                id=zone_id,
                coordinates=coordinates,
                active_time=active_time
            )
            no_fly_zones.append(zone)
            
        return drones, deliveries, no_fly_zones
        
    def save_to_txt(self, drones: List[Drone], deliveries: List[DeliveryPoint], 
                   no_fly_zones: List[NoFlyZone], filename: str):
        """Verileri txt dosyasına kaydet"""
        with open(filename, 'w', encoding='utf-8') as file:
            # Drone'ları kaydet
            file.write("DRONLAR\n")
            file.write("id,max_weight,battery,speed,start_pos_x,start_pos_y\n")
            for drone in drones:
                file.write(f"{drone.id},{drone.max_weight},{drone.battery},"
                          f"{drone.speed},{drone.start_pos[0]},{drone.start_pos[1]}\n")
            
            # Teslimatları kaydet
            file.write("\nTESLIMATLAR\n")
            file.write("id,pos_x,pos_y,weight,priority,time_window_start,time_window_end\n")
            for delivery in deliveries:
                file.write(f"{delivery.id},{delivery.pos[0]},{delivery.pos[1]},"
                          f"{delivery.weight},{delivery.priority},"
                          f"{delivery.time_window[0]},{delivery.time_window[1]}\n")
            
            # No-fly zone'ları kaydet
            file.write("\nUCUSA_YASAK_BOLGELER\n")
            file.write("id,coord1_x,coord1_y,coord2_x,coord2_y,coord3_x,coord3_y,coord4_x,coord4_y,active_start,active_end\n")
            for zone in no_fly_zones:
                coords = zone.coordinates
                file.write(f"{zone.id},{coords[0][0]},{coords[0][1]},{coords[1][0]},{coords[1][1]},"
                          f"{coords[2][0]},{coords[2][1]},{coords[3][0]},{coords[3][1]},"
                          f"{zone.active_time[0]},{zone.active_time[1]}\n")
                          
    def print_data_summary(self, drones: List[Drone], deliveries: List[DeliveryPoint], 
                          no_fly_zones: List[NoFlyZone]):
        """Yüklenen veri özetini yazdır"""
        print("Veri Yükleme Özeti:")
        print("=" * 50)
        # Drone sayısını ve özelliklerini yazar
        print(f"Toplam Drone Sayısı: {len(drones)}")
        for drone in drones:
            print(f"  - Drone {drone.id}: {drone.max_weight}kg kapasite, "
                  f"{drone.battery}mAh batarya, {drone.speed}m/s hız")
        # Teslimat sayısı, toplam ağırlık ve öncelik dağılımını yazar
        print(f"\nToplam Teslimat Sayısı: {len(deliveries)}")
        priority_count = {}
        total_weight = 0
        for delivery in deliveries:
            priority_count[delivery.priority] = priority_count.get(delivery.priority, 0) + 1
            total_weight += delivery.weight
            
        print(f"  - Toplam ağırlık: {total_weight:.1f}kg")
        print(f"  - Öncelik dağılımı: {priority_count}")
          # No-fly zone sayısı ve aktif zaman aralıklarını yazar
        print(f"\nToplam No-Fly Zone Sayısı: {len(no_fly_zones)}")
        for zone in no_fly_zones:
            print(f"  - Zone {zone.id}: Aktif {zone.active_time[0]}-{zone.active_time[1]} zaman aralığında")
            
        #Kapasite analizi yapar, toplam drone kapasitesi ve teslimat ağırlığını karşılaştırır
        total_drone_capacity = sum(drone.max_weight for drone in drones)
        capacity_utilization = (total_weight / total_drone_capacity) * 100 if total_drone_capacity > 0 else 0
        
        print(f"\nKapasite Analizi:")
        print(f"  - Toplam drone kapasitesi: {total_drone_capacity:.1f}kg")
        print(f"  - Toplam teslimat ağırlığı: {total_weight:.1f}kg")
        print(f"  - Teorik kapasite kullanımı: %{capacity_utilization:.1f}")
        # Kapasite durumuna göre uyarı veya onay mesajı verir
        if capacity_utilization > 100:
            print("  ⚠️  UYARI: Toplam teslimat ağırlığı drone kapasitesini aşıyor!")
        elif capacity_utilization > 80:
            print("  ⚠️  Yüksek kapasite kullanımı - zorlayıcı senaryo")
        else:
            print("  ✅ Makul kapasite kullanımı")
