"""
CSP (Constraint Satisfaction Problem) Çözücü - Dinamik kısıtlar için
Bu dosya, proje kapsamında drone teslimat görevlerinin adil, dengeli ve kısıtlarla uyumlu biçimde dağıtılmasını sağlar.
"""
from typing import List, Dict, Set, Tuple, Optional
from .drone import Drone # Drone sınıfını içeri aktar
from .delivery_point import DeliveryPoint # Teslimat noktası sınıfını içeri aktar
from .no_fly_zone import NoFlyZone # Uçuşa yasak bölge sınıfını içeri aktar
from .graph_builder import DeliveryGraph # Harita/bağlantı grafiğini yöneten sınıf

class CSPSolver:
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], 
                 no_fly_zones: List[NoFlyZone], graph: DeliveryGraph):
        self.drones = drones # Kullanılabilir drone listesi
        self.deliveries = deliveries # Tüm teslimat noktaları listesi
        self.no_fly_zones = no_fly_zones # Uçuşa yasak bölgeler
        self.graph = graph # Teslimat grafiği
        
        # CSP değişkenleri
        self.variables = {}  # drone_id -> [delivery_ids]  Değişkenler: drone_id -> atanacak teslimatlar
        self.domains = {}    # drone_id -> possible_delivery_sets Domain'ler: drone_id -> olası teslimat setleri
        self.constraints = [] # Uygulanacak tüm kısıtlar listesi
        
        self.setup_csp() # CSP problemini başlat
        
    def setup_csp(self):
        """CSP problemini kur"""
        # Değişkenler: Her drone için olası teslimat setleri
        for drone in self.drones:
            self.variables[drone.id] = [] # Başlangıçta boş değişken
            self.domains[drone.id] = self.get_possible_deliveries(drone) # Olası teslimat setleri
            
        # Kısıtları tanımla
        self.setup_constraints()
        
    def get_possible_deliveries(self, drone: Drone) -> List[Set[int]]:
        """Bir drone'un yapabileceği olası teslimat kombinasyonlarını bul"""
        possible_sets = []
        
        # Drone'un tekli teslimat yapabildiği durumlar
        for delivery in self.deliveries:
            if self.can_drone_handle_delivery(drone, delivery):
                possible_sets.append({delivery.id})
                
        # # Drone'un ikili kombinasyon yapabildiği teslimatlar
        for i, delivery1 in enumerate(self.deliveries):
            for j, delivery2 in enumerate(self.deliveries):
                if i != j and self.can_drone_handle_deliveries(drone, [delivery1, delivery2]):
                    possible_sets.append({delivery1.id, delivery2.id})
                    
        # # Üçlü kombinasyonlar (enerji ve kapasite izin veriyorsa)
        for i, delivery1 in enumerate(self.deliveries):
            for j, delivery2 in enumerate(self.deliveries):
                for k, delivery3 in enumerate(self.deliveries):
                    if (i != j != k and i != k and 
                        self.can_drone_handle_deliveries(drone, [delivery1, delivery2, delivery3])):
                        possible_sets.append({delivery1.id, delivery2.id, delivery3.id})
                        
        # Boş set de ekle (drone hiçbir teslimat yapmıyorsa) Hiçbir teslimat yapılmadığı durum
        possible_sets.append(set())
        
        return possible_sets
        
    def can_drone_handle_delivery(self, drone: Drone, delivery: DeliveryPoint) -> bool:
        """Drone tek bir teslimatı yapabilir mi?"""
        # Ağırlık kontrolü
        if delivery.weight > drone.max_weight: # Ağırlık fazla ise yapılamaz
            return False
            
        # Gidiş + dönüş mesafesi ve enerji hesabı
        distance_to_delivery = drone.get_distance(drone.start_pos, delivery.pos)
        distance_back = drone.get_distance(delivery.pos, drone.start_pos)
        total_distance = distance_to_delivery + distance_back
         # Taşınan yükle enerji ihtiyacı
        energy_needed = drone.calculate_energy_consumption(total_distance, delivery.weight)
        
        return energy_needed <= drone.battery #Batarya yeterli mi?
        
    def can_drone_handle_deliveries(self, drone: Drone, deliveries: List[DeliveryPoint]) -> bool:
        """Drone birden fazla teslimatı yapabilir mi?"""
        total_weight = sum(d.weight for d in deliveries) # Toplam ağırlık
        if total_weight > drone.max_weight: # Ağırlık sınırı
            return False
            
        # Basit bir rota tahmini (greedy)
        current_pos = drone.start_pos # Başlangıç noktası
        total_energy = 0 # Harcanacak enerji
        current_weight = 0 # O anki toplam ağırlık
        
        # Teslimatlar öncelik sırasına göre sıralanır
        sorted_deliveries = sorted(deliveries, key=lambda x: x.priority, reverse=True)
        
        for delivery in sorted_deliveries:
            distance = drone.get_distance(current_pos, delivery.pos)
            current_weight += delivery.weight
            energy = drone.calculate_energy_consumption(distance, current_weight)
            total_energy += energy
            current_pos = delivery.pos
            
        # Üsse dönüş enerjisi
        return_distance = drone.get_distance(current_pos, drone.start_pos)
        return_energy = drone.calculate_energy_consumption(return_distance, 0)
        total_energy += return_energy
        
        return total_energy <= drone.battery # Enerji sınırı
        
    def setup_constraints(self):
        """Kısıtları tanımla"""
        # Kısıt 1: Her teslimat sadece bir drone tarafından yapılabilir
        self.constraints.append(self.unique_delivery_constraint)
        
        # Kısıt 2: No-fly zone ihlali olmamalı
        self.constraints.append(self.no_fly_zone_constraint)
        
        # Kısıt 3: Teslim zamanına uyulsun
        self.constraints.append(self.time_window_constraint)
        
        # Kısıt 4: Kapasite aşımı olmasın
        self.constraints.append(self.capacity_constraint)
        #Kısıt 1: Teslimatlar benzersiz olmalı
    def unique_delivery_constraint(self, assignment: Dict[int, Set[int]]) -> bool:
        """Her teslimat sadece bir drone tarafından yapılmalı"""
        all_deliveries = set()
        
        for drone_id, delivery_set in assignment.items():
            if delivery_set.intersection(all_deliveries): # Teslimat başka drone ile çakışıyorsa
                return False
            all_deliveries.update(delivery_set)
            
        return True
        #Kısıt 2: No‑fly zone ihlali
    def no_fly_zone_constraint(self, assignment: Dict[int, Set[int]]) -> bool:
        """No-fly zone ihlali kontrolü"""
        current_time = 0  # Basit senaryoda tek zaman dilimi
        
        for drone_id, delivery_set in assignment.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            
            for delivery_id in delivery_set:
                delivery = next(d for d in self.deliveries if d.id == delivery_id)
                
                # Drone'dan teslimat noktasına rota
                for zone in self.no_fly_zones:
                    if (zone.is_active(current_time) and 
                        zone.line_intersects_polygon(drone.start_pos, delivery.pos)):
                        return False
                        
        return True
        #Kısıt 3: Zaman penceresi 
    def time_window_constraint(self, assignment: Dict[int, Set[int]]) -> bool:
        """Zaman penceresi kısıt kontrolü"""
        for drone_id, delivery_set in assignment.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            
            if len(delivery_set) > 1:
                # Çoklu teslimat için basit zaman kontrolü
                deliveries = [next(d for d in self.deliveries if d.id == did) for did in delivery_set]
                
                current_time = 0
                current_pos = drone.start_pos
                
                # Öncelik sırasına göre sırala
                sorted_deliveries = sorted(deliveries, key=lambda x: x.priority, reverse=True)
                
                for delivery in sorted_deliveries:
                    travel_time = drone.get_distance(current_pos, delivery.pos) / drone.speed
                    current_time += travel_time
                    
                    # Zaman penceresi kontrolü
                    if not (delivery.time_window[0] <= current_time <= delivery.time_window[1]):
                        return False
                        
                    current_pos = delivery.pos
                    
        return True
        #Kısıt 4: Kapasite
    def capacity_constraint(self, assignment: Dict[int, Set[int]]) -> bool:
        """Drone kapasitesi aşılıyor mu kontrolü"""
        for drone_id, delivery_set in assignment.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            
            total_weight = 0
            for delivery_id in delivery_set:
                delivery = next(d for d in self.deliveries if d.id == delivery_id)
                total_weight += delivery.weight
                
            if total_weight > drone.max_weight:
                return False
                
        return True
        
    def is_consistent(self, assignment: Dict[int, Set[int]]) -> bool:
        """Drone kapasitesi aşılıyor mu kontrolü"""
        for constraint in self.constraints:
            if not constraint(assignment):
                return False
        return True
        
    def backtrack_search(self) -> Optional[Dict[int, Set[int]]]:
        """Backtracking ile CSP çözümü bul"""
        assignment = {}
        return self.backtrack(assignment)
        
    def backtrack(self, assignment: Dict[int, Set[int]]) -> Optional[Dict[int, Set[int]]]:
        """Backtracking algoritması"""
        # Tamamlandı mı?
        if len(assignment) == len(self.drones):
            return assignment
            
        # Sonraki değişkeni seç
        unassigned_drones = [d.id for d in self.drones if d.id not in assignment]
        drone_id = unassigned_drones[0]
        
        # Domain değerlerini dene
        for delivery_set in self.domains[drone_id]:
            assignment[drone_id] = delivery_set
            
            if self.is_consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                    
            del assignment[drone_id]
            
        return None
        
    def forward_checking(self, assignment: Dict[int, Set[int]]) -> bool:
        """Domain daraltma ile ileriye dönük kontrol"""
        # Atanmış teslimatları topla
        assigned_deliveries = set()
        for delivery_set in assignment.values():
            assigned_deliveries.update(delivery_set)
            
        # Kalan drone'lar için domain'leri güncelle
        for drone_id in [d.id for d in self.drones if d.id not in assignment]:
            new_domain = []
            
            for delivery_set in self.domains[drone_id]:
                # Çakışma var mı?
                if not delivery_set.intersection(assigned_deliveries):
                    new_domain.append(delivery_set)
                    
            if not new_domain:
                return False  # Domain boş
                
            self.domains[drone_id] = new_domain
            
        return True
        
    def solve_with_forward_checking(self) -> Optional[Dict[int, Set[int]]]:
        """Forward checking ile geliştirilmiş CSP çözümü"""
        assignment = {}
        return self.backtrack_with_fc(assignment)
        
    def backtrack_with_fc(self, assignment: Dict[int, Set[int]]) -> Optional[Dict[int, Set[int]]]:
        """Forward checking ile backtracking"""
        if len(assignment) == len(self.drones):
            return assignment
            
        # Sonraki değişkeni seç (MRV heuristic)
        unassigned_drones = [d.id for d in self.drones if d.id not in assignment]
        drone_id = min(unassigned_drones, key=lambda d: len(self.domains[d]))
        
        # Domain'i kopyala (değişiklikler için)
        original_domains = {d_id: list(domain) for d_id, domain in self.domains.items()}
        
        for delivery_set in list(self.domains[drone_id]):
            assignment[drone_id] = delivery_set
            
            if self.is_consistent(assignment):
                if self.forward_checking(assignment):
                    result = self.backtrack_with_fc(assignment)
                    if result is not None:
                        return result
                        
            # Backtrack
            del assignment[drone_id]
            self.domains = original_domains
            
        return None
        
    def get_solution_quality(self, solution: Dict[int, Set[int]]) -> Dict:
        """Çözüm kalitesi metriklerini hesapla"""
        if not solution:
            return {'covered_deliveries': 0, 'total_deliveries': len(self.deliveries), 
                   'coverage_rate': 0.0, 'drone_utilization': 0.0}
            
        covered_deliveries = set()
        active_drones = 0
        
        for drone_id, delivery_set in solution.items():
            covered_deliveries.update(delivery_set)
            if delivery_set:
                active_drones += 1
                
        coverage_rate = len(covered_deliveries) / len(self.deliveries)
        drone_utilization = active_drones / len(self.drones)
        
        return {
            'covered_deliveries': len(covered_deliveries),
            'total_deliveries': len(self.deliveries),
            'coverage_rate': coverage_rate,
            'drone_utilization': drone_utilization,
            'active_drones': active_drones,
            'solution': solution
        }
    
    #Çözümü okunabilir biçimde yazdır
        
    def print_solution(self, solution: Dict[int, Set[int]]):
        """Çözümü yazdır"""
        if not solution:
            print("Çözüm bulunamadı!")
            return
            
        print("CSP Çözümü:")
        print("-" * 50)
        
        for drone_id, delivery_set in solution.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            print(f"Drone {drone_id} (Kapasite: {drone.max_weight}kg):")
            
            if delivery_set:
                total_weight = 0
                for delivery_id in delivery_set:
                    delivery = next(d for d in self.deliveries if d.id == delivery_id)
                    total_weight += delivery.weight
                    print(f"  - Teslimat {delivery_id}: {delivery.weight}kg, Öncelik: {delivery.priority}")
                print(f"  Toplam Ağırlık: {total_weight:.1f}kg")
            else:
                print("  - Teslimat yok")
            print()
            
        quality = self.get_solution_quality(solution)
        print(f"Çözüm Kalitesi:")
        print(f"- Kapsanan teslimatlar: {quality['covered_deliveries']}/{quality['total_deliveries']}")
        print(f"- Kapsama oranı: %{quality['coverage_rate']*100:.1f}")
        print(f"- Drone kullanım oranı: %{quality['drone_utilization']*100:.1f}")
