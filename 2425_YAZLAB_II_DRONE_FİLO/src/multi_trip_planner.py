"""
Multi-Trip Planner - Drone'ların şarj olup tekrar kullanılmasını sağlar
Bu dosya, drone tabanlı teslimat sisteminde çoklu tur planlamasını gerçekleştiren ana modüldür. Bu dosya, her bir drone’un birden fazla teslimat turuna çıkmasını, gerektiğinde şarj olup yeniden görev almasını, teslimat önceliklerini ve zaman pencerelerini göz önünde bulundurarak optimum şekilde paketleri ulaştırmasını sağlar.
"""
import math
import time
from typing import List, Dict, Tuple, Optional, Set
from .drone import Drone # Drone sınıfını içe aktar
from .delivery_point import DeliveryPoint  # Teslimat noktası sınıfı
from .no_fly_zone import NoFlyZone # Uçuşa yasak bölge sınıfı
from .graph_builder import DeliveryGraph # Teslimat grafiğini yöneten sınıf
from .astar import AStarPathfinder # A* algoritması sınıfı

class MultiTripPlanner:
    """Çoklu tur teslimat planlayıcısı"""
    
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], 
                 no_fly_zones: List[NoFlyZone], graph: DeliveryGraph):
        self.drones = drones # Kullanılabilir drone listesi
        self.deliveries = deliveries # Teslimat noktaları listesi
        self.no_fly_zones = no_fly_zones # Yasak bölgeler
        self.graph = graph # Drone rotalarının bulunduğu grafik
        self.astar = AStarPathfinder(graph) # A* algoritması ile yol bulucu
        
        # Simülasyon parametreleri
        self.time_horizon = 480  # Simülasyon süresi (8 saat, dakika cinsinden)
        self.charge_time_per_cycle = 30  # 30 dakika şarj
        self.battery_threshold = 0.3  # %30'da şarj et
        
        # Sonuçlar
        self.completed_deliveries = [] # Başarılı teslimatlar
        self.drone_trips = {drone.id: [] for drone in drones} # Her drone için tur bilgisi
        self.drone_reports = {} # Drone'lara ait performans raporları
        
    def plan_multi_trip_delivery(self) -> Dict:
        """Çoklu tur teslimat planlaması yap"""
        print("🔄 Multi-trip planlama başlıyor...")
        start_time = time.time() # Başlangıç zamanı
        
        # Drone'ları sıfırla
        for drone in self.drones:
            drone.reset()
            
        remaining_deliveries = list(self.deliveries) # Teslim edilecek kalan paketler
        current_time = 0 # Teslim edilecek kalan paketler
        total_trips = 0 # Yapılan toplam tur sayısı
        stuck_counter = 0  # Sonsuz döngü koruması
        
        while remaining_deliveries and current_time < self.time_horizon:
            print(f"⏰ Zaman: {current_time}dk, Kalan teslimat: {len(remaining_deliveries)}")
            
            progress_made = False  # Bu döngüde ilerleme var mı?
            
            # Her drone için tur planla
            for drone in self.drones:
                if current_time >= self.time_horizon:
                    break
                    
                # Şarj gerekiyor mu kontrol et
                if drone.needs_charging() or drone.battery < drone.max_battery * self.battery_threshold:
                    charge_time = self.charge_drone(drone, current_time) # Şarj et
                    current_time += charge_time
                    continue
                
                # Bu drone için optimal teslimatları bul
                trip_deliveries = self.plan_single_trip(drone, remaining_deliveries, current_time)
                
                if trip_deliveries:
                    # Teslimatları gerçekleştir
                    trip_time = self.execute_trip(drone, trip_deliveries, current_time)
                    current_time += trip_time
                    total_trips += 1
                    progress_made = True
                    
                    # Tamamlanan teslimatları listeden çıkar
                    for delivery in trip_deliveries:
                        if delivery in remaining_deliveries:
                            remaining_deliveries.remove(delivery)
                            self.completed_deliveries.append(delivery)
                    
                    # Tur bilgilerini kaydet
                    self.drone_trips[drone.id].append({
                        'trip_number': len(self.drone_trips[drone.id]) + 1,
                        'deliveries': [d.id for d in trip_deliveries],
                        'start_time': current_time - trip_time,
                        'end_time': current_time,
                        'duration': trip_time,
                        'total_weight': sum(d.weight for d in trip_deliveries)
                    })
            
            # İlerleme yoksa ve kalan teslimat varsa, zamanı ilerlet
            if not progress_made and remaining_deliveries:
                stuck_counter += 1
                print(f"⚠️ İlerleme yok, zaman 30dk ilerletiliyor... (Stuck: {stuck_counter})")
                current_time += 30  # 30 dakika ilerlet
                
                # Çok uzun sıkıştıysa döngüyü kır
                if stuck_counter >= 10:
                    print("❌ 10 kez sıkıştı, simülasyon sonlandırılıyor")
                    break
            else:
                stuck_counter = 0  # İlerleme varsa counter'ı sıfırla
                
        execution_time = time.time() - start_time # Simülasyon süresi
        
        # Drone raporlarını oluştur
        self.generate_drone_reports()
        
         # Genel istatistikleri hesapla ve döndür
        delivery_count = len(self.completed_deliveries)
        delivery_rate = delivery_count / len(self.deliveries) if self.deliveries else 0
        
        print(f"✅ Multi-trip tamamlandı!")
        print(f"   - Toplam teslimat: {delivery_count}/{len(self.deliveries)}")
        print(f"   - Teslimat oranı: %{delivery_rate*100:.1f}")
        print(f"   - Toplam tur sayısı: {total_trips}")
        print(f"   - Çalışma süresi: {execution_time:.3f} saniye")
        
        return {
            'delivery_count': delivery_count,
            'delivery_rate': delivery_rate,
            'total_trips': total_trips,
            'completed_deliveries': self.completed_deliveries,
            'drone_trips': self.drone_trips,
            'drone_reports': self.drone_reports,
            'execution_time': execution_time,
            'routes': self.get_solution_routes()
        }
    
    def plan_single_trip(self, drone: Drone, available_deliveries: List[DeliveryPoint], 
                        current_time: int) -> List[DeliveryPoint]:
        """Tek bir tur için optimal teslimatları seç - KAPASİTEYE KADAR ÇOKLU PAKET"""
        if not available_deliveries:
            return [] # Teslimat yoksa boş liste döndür
            
        # Drone'un başlangıç konumuna dön ve ağırlığını sıfırla
        drone.current_pos = drone.start_pos
        drone.current_weight = 0
        
        # Öncelik ve ağırlığa göre sıralama (öncelik yüksek ve hafif olanlar önde)
        sorted_deliveries = sorted(available_deliveries, 
                                 key=lambda x: (x.priority, -x.weight), 
                                 reverse=True)
        
        selected_deliveries = [] # Seçilen teslimatlar listesi
        total_weight = 0 # Toplam ağırlık
        
        print(f"  🎯 Drone {drone.id} için paket seçimi (Kapasite: {drone.max_weight}kg):")
        
         # Açgözlü yaklaşım: kapasite dolana kadar uygun paketleri ekle
        for delivery in sorted_deliveries:
            # Ağırlık kontrolü kapasiteyi aşıyorsa geç
            if total_weight + delivery.weight > drone.max_weight:
                print(f"    ⚠️ Paket {delivery.id} ({delivery.weight:.1f}kg) çok ağır (kalan: {drone.max_weight - total_weight:.1f}kg)")
                continue
            
            # Zaman penceresi kontrolü - DAHA ESNEK
            # Zaman penceresi geçmişse bile kabul et ama ceza ver
            time_penalty = 0
            if current_time < delivery.time_window[0]:
                # Henüz erken, bekleyebiliriz
                time_penalty = (delivery.time_window[0] - current_time) * 0.1
            elif current_time > delivery.time_window[1]:
                # Geç kaldık ama yine de kabul edelim
                time_penalty = (current_time - delivery.time_window[1]) * 0.2
                print(f"    ⏰ Paket {delivery.id} geç teslimat (penalty: {time_penalty:.1f})")
            
            # Çok geç değilse kabul et (2 saate kadar tolere et)
            if current_time > delivery.time_window[1] + 120:  # 2 saat geç limit
                print(f"    ❌ Paket {delivery.id} çok geç ({current_time}dk > {delivery.time_window[1] + 120}dk)")
                continue
                
            # YAKLAŞIK enerji kontrolü (basitleştirilmiş)
            # Ortalama mesafe yaklaşımı kullan
            avg_distance = 50  # Ortalama teslimat mesafesi
            estimated_energy = drone.calculate_energy_consumption(
                avg_distance * len(selected_deliveries) + 100, total_weight + delivery.weight
            )
            
            if estimated_energy <= drone.battery * 0.7:  # %70 güvenlik marjı
                selected_deliveries.append(delivery)
                total_weight += delivery.weight
                print(f"    ✅ Paket {delivery.id} seçildi: {delivery.weight:.1f}kg (Öncelik: {delivery.priority})")
                
                # Maksimum paket sayısı sınırı (rota optimizasyonu için)
                if len(selected_deliveries) >= 8:  # Maksimum 8 paket/tur
                    print(f"    🔄 Maksimum paket sayısına ulaşıldı (8)")
                    break
            else:
                print(f"    🔋 Paket {delivery.id} enerji yetersizliği")
        
        print(f"    📊 Tur özeti: {len(selected_deliveries)} paket, {total_weight:.1f}/{drone.max_weight:.1f}kg (%{(total_weight/drone.max_weight)*100:.1f})")
        
        return selected_deliveries # Seçilen paketleri döndür
    
    def execute_trip(self, drone: Drone, trip_deliveries: List[DeliveryPoint], 
                    start_time: int) -> int:
        """Teslimat turunu gerçekleştir ve süreyi döndür - TÜM PAKETLERİ BİRDEN AL"""
        if not trip_deliveries:
            return 0 # Teslimat yoksa süre 0
            
        total_time = 0 # Toplam geçen süre
        current_pos = drone.start_pos # Drone başlangıçta üste
        
        # ÖNEMLİ: TÜM PAKETLERİ BAŞTA AL (PDF'deki gibi)
        total_trip_weight = sum(d.weight for d in trip_deliveries)
        drone.current_weight = total_trip_weight # Drone taşıma yükü
        
        print(f"  🚁 Drone {drone.id}: {len(trip_deliveries)} paket alındı ({total_trip_weight:.1f}kg)")
        
        # Her teslimat noktasına git ve paketi bırak
        for i, delivery in enumerate(trip_deliveries):
            # Teslimat noktasına git
            distance = drone.get_distance(current_pos, delivery.pos)  # Mesafe hesapla
            travel_time = distance / drone.speed / 60  # dakika
            
            # Enerji tüket (mevcut ağırlıkla)
            energy_consumed = drone.calculate_energy_consumption(distance, drone.current_weight)
            drone.battery -= energy_consumed # Bataryadan düş
            
            # Teslimat noktasına var
            drone.total_distance += distance # Toplam mesafeye ekle
            total_time += travel_time + 2  # 2 dakika teslimat süresi
            current_pos = delivery.pos # Yeni konum
            
            # Paketi bırak (ağırlık azalt)
            drone.current_weight -= delivery.weight  # Paket bırakıldı
            drone.deliveries.append(delivery.id) # Kayıt tut
            
            print(f"    📦 Teslimat {i+1}/{len(trip_deliveries)}: {delivery.weight:.1f}kg bırakıldı, kalan: {drone.current_weight:.1f}kg")
        
        # Üsse dön (artık boş)
        distance_to_base = drone.get_distance(current_pos, drone.start_pos)
        return_time = distance_to_base / drone.speed / 60
        total_time += return_time
        
        # Enerji tüket (boş olarak)
        energy_consumed = drone.calculate_energy_consumption(distance_to_base, 0) # Boş dönüş
        drone.battery -= energy_consumed
        drone.total_distance += distance_to_base
        drone.current_pos = drone.start_pos
        
        print(f"    🏠 Drone {drone.id} üsse döndü, toplam süre: {int(total_time)}dk")
        
        return int(total_time) # Turu tamamlamak için geçen süre
    
    def charge_drone(self, drone: Drone, current_time: int) -> int:
        """Drone'u şarj et"""
        if drone.current_pos != drone.start_pos:
            # Üsse dön
            distance = drone.get_distance(drone.current_pos, drone.start_pos)
            return_time = distance / drone.speed / 60
            drone.move_to(drone.start_pos)
            current_time += return_time
        
        # Şarj et
        drone.charge(self.charge_time_per_cycle) # Şarj et
        return self.charge_time_per_cycle # Şarj süresini döndür
    
    def generate_drone_reports(self):
        """Her drone için detaylı rapor oluştur"""
        for drone in self.drones:
            trips = self.drone_trips[drone.id]
            total_deliveries = sum(len(trip['deliveries']) for trip in trips)
            
            self.drone_reports[drone.id] = {
                'drone_id': drone.id,
                'total_trips': len(trips),
                'total_deliveries': total_deliveries,
                'total_distance': drone.total_distance,
                'total_time': drone.total_time,
                'charging_cycles': drone.charging_time // self.charge_time_per_cycle,
                'energy_efficiency': total_deliveries / (drone.max_battery - drone.battery + 1),
                'utilization_rate': (drone.total_time / self.time_horizon) * 100 if self.time_horizon > 0 else 0,
                'trips_detail': trips,
                'final_battery': drone.battery,
                'average_deliveries_per_trip': total_deliveries / len(trips) if trips else 0
            }
    
    def get_solution_routes(self) -> Dict:
        """Çözüm rotalarını döndür"""
        routes = {}
        for drone_id, trips in self.drone_trips.items():
            if trips:
                # Her trip için rota oluştur
                drone_routes = []
                for trip in trips:
                    route = [f"drone_{drone_id}"]
                    route.extend([f"delivery_{d_id}" for d_id in trip['deliveries']])
                    route.append(f"drone_{drone_id}")  # Üsse dönüş
                    drone_routes.append(route)
                
                # Tüm rotaları birleştir
                full_route = [f"drone_{drone_id}"]
                for trip_route in drone_routes:
                    full_route.extend(trip_route[1:])  # İlk drone pozisyonunu tekrarlama
                
                routes[drone_id] = full_route
                
        return routes # Her drone için tam rota
    
    def print_detailed_report(self):
        """Detaylı raporu yazdır"""
        print("\n" + "="*60)
        print("🔄 MULTI-TRIP DETAYLI RAPOR")
        print("="*60)
        
        for drone_id, report in self.drone_reports.items():
            print(f"\n🚁 DRONE {drone_id}:")
            print(f"   - Toplam tur sayısı: {report['total_trips']}")
            print(f"   - Toplam teslimat: {report['total_deliveries']}")
            print(f"   - Toplam mesafe: {report['total_distance']:.1f}m")
            print(f"   - Şarj döngüsü: {report['charging_cycles']} kez")
            print(f"   - Kullanım oranı: %{report['utilization_rate']:.1f}")
            print(f"   - Tur başına ort. teslimat: {report['average_deliveries_per_trip']:.1f}")
            print(f"   - Kalan batarya: {report['final_battery']:.0f}mAh")
            
            # Tur detayları
            if report['trips_detail']:
                print(f"   📋 Tur Detayları:")
                for trip in report['trips_detail']:
                    print(f"      Tur {trip['trip_number']}: {len(trip['deliveries'])} teslimat, "
                          f"{trip['duration']}dk ({trip['start_time']}-{trip['end_time']}dk), "
                          f"{trip['total_weight']:.1f}kg")
                          
        # Genel istatistikler
        total_trips = sum(len(trips) for trips in self.drone_trips.values())
        total_deliveries = len(self.completed_deliveries)
        avg_deliveries_per_trip = total_deliveries / total_trips if total_trips > 0 else 0
        
        print(f"\n📊 GENEL İSTATİSTİKLER:")
        print(f"   - Toplam tur sayısı: {total_trips}")
        print(f"   - Tamamlanan teslimat: {total_deliveries}/{len(self.deliveries)}")
        print(f"   - Tur başına ortalama teslimat: {avg_deliveries_per_trip:.1f}")
        if self.drone_reports:
            best_drone = max(self.drone_reports.keys(), 
                           key=lambda x: self.drone_reports[x]['total_deliveries'])
            print(f"   - En verimli drone: Drone {best_drone}")
