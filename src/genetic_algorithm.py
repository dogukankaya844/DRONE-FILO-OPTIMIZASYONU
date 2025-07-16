"""
Genetic Algorithm (GA) implementasyonu - PDF'deki fitness fonksiyonuna göre
Bu dosya, teslimatları drone’lara en verimli şekilde paylaştırmak için genetik algoritma yöntemini kullanarak rastgele nüfus oluşturur, çaprazlama‑mutasyon döngüsüyle popülasyonu evrimleştirir ve en yüksek fitness değerine sahip çözümü bularak ilgili drone rotalarını ve performans istatistiklerini üretir.
"""
import random # Rastgele seçimler için
import math
from typing import List, Dict, Tuple, Optional
from .drone import Drone # Drone sınıfı
from .delivery_point import DeliveryPoint  # Teslimat sınıfı
from .no_fly_zone import NoFlyZone # No-fly zone sınıfı
from .graph_builder import DeliveryGraph # Mesafe grafı
from .astar import AStarPathfinder # A* rota bulucu (GA sonrası rota çıkarırken kullanılır)

class Individual:
    """GA için birey (kromozom) sınıfı"""
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint]):
        self.drones = drones
        self.deliveries = deliveries
        self.chromosome = {}  # drone_id -> [delivery_ids]
        self.fitness = 0.0 # Fitness değeri
        self.is_valid = True # Fizibilite bayrağı
        
        # Her drone için boş teslimat listesi hazırla
        for drone in drones:
            self.chromosome[drone.id] = []
            
    def randomize(self):
        """Rastgele geçerli kromozom oluştur"""
        available_deliveries = list(range(1, len(self.deliveries) + 1))
        random.shuffle(available_deliveries) # Teslimatları karıştır
        
        for delivery_id in available_deliveries:
            delivery = next(d for d in self.deliveries if d.id == delivery_id)
            
             # Teslimatı taşıyabilecek drone'ları bul
            capable_drones = []
            for drone in self.drones:
                current_weight = sum(next(d for d in self.deliveries if d.id == did).weight 
                                   for did in self.chromosome[drone.id])
                
                if current_weight + delivery.weight <= drone.max_weight:
                    capable_drones.append(drone.id)
            # Uygun drone varsa rastgele ata    
            if capable_drones:
                chosen_drone = random.choice(capable_drones)
                self.chromosome[chosen_drone].append(delivery_id)
                
    def calculate_fitness(self, graph: DeliveryGraph, no_fly_zones: List[NoFlyZone]) -> float:
        """
        Fitness fonksiyonu - PDF'deki formüle göre:
        fitness = (teslim_edilen_sayısı × 500) - (enerji_tüketimi × 0.1) - (kural_ihlali × 1000)
        """
        delivered_count = 0
        total_energy = 0.0
        rule_violations = 0
        
        for drone_id, delivery_list in self.chromosome.items():
            if not delivery_list:
                continue
                
            drone = next(d for d in self.drones if d.id == drone_id)
            
            # Teslimat sayısı
            delivered_count += len(delivery_list) # Teslimat sayısı artır
            
            # Drone’a ait enerji & ihlal hesapla
            energy, violations = self._calculate_drone_metrics(drone, delivery_list, graph, no_fly_zones)
            total_energy += energy
            rule_violations += violations
            
        # PDF'deki fitness formülü
        self.fitness = (delivered_count * 500) - (total_energy * 0.1) - (rule_violations * 1000)
        return self.fitness
        
    def _calculate_drone_metrics(self, drone: Drone, delivery_list: List[int], 
                                graph: DeliveryGraph, no_fly_zones: List[NoFlyZone]) -> Tuple[float, int]:
        """Drone için enerji tüketimi ve kural ihlallerini hesapla"""
        total_energy = 0.0
        violations = 0
        current_pos = drone.start_pos
        current_weight = 0.0
        current_time = 0
        
        # Teslimatları öncelik sırasına göre sırala
        deliveries = [next(d for d in self.deliveries if d.id == did) for did in delivery_list] 
        deliveries.sort(key=lambda x: x.priority, reverse=True)
        
        for delivery in deliveries:
            # Mesafe ve enerji hesapla
            distance = graph.euclidean_distance(current_pos, delivery.pos) # Mesafe
            current_weight += delivery.weight # Güncel yük
            
            # Kapasite kontrolü
            if current_weight > drone.max_weight:
                violations += 1
                
            energy = drone.calculate_energy_consumption(distance, current_weight)
            total_energy += energy
            
            # Zaman hesapla
            travel_time = distance / drone.speed
            current_time += travel_time
            
            # Zaman penceresi kontrolü
            if not (delivery.time_window[0] <= current_time <= delivery.time_window[1]):
                violations += 1
                
            # No-fly zone kontrolü
            for zone in no_fly_zones:
                if zone.is_active(current_time) and zone.line_intersects_polygon(current_pos, delivery.pos):
                    violations += 1
                    
            current_pos = delivery.pos # Konumu güncelle
            
        # Üsse dönüş enerji maliyeti
        return_distance = graph.euclidean_distance(current_pos, drone.start_pos)
        return_energy = drone.calculate_energy_consumption(return_distance, 0)
        total_energy += return_energy
        
        return total_energy, violations
        
    def is_feasible(self) -> bool:
        """Kapasite aşılıyor mu kontrol et"""
        for drone_id, delivery_list in self.chromosome.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            
            # Kapasite kontrolü
            total_weight = sum(next(d for d in self.deliveries if d.id == did).weight 
                             for did in delivery_list)
            if total_weight > drone.max_weight:
                return False
                
        return True
        
    def repair(self):
        """Kapasite aşımını düzelterek kromozomu onar"""
        for drone_id, delivery_list in self.chromosome.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            
            # Kapasite aşımını düzelt
            total_weight = 0
            valid_deliveries = []
            
            for delivery_id in delivery_list:
                delivery = next(d for d in self.deliveries if d.id == delivery_id)
                if total_weight + delivery.weight <= drone.max_weight:
                    valid_deliveries.append(delivery_id)
                    total_weight += delivery.weight
                    
            self.chromosome[drone_id] = valid_deliveries
            
    def copy(self):
        """Kromozomun kopyasını oluştur"""
        new_individual = Individual(self.drones, self.deliveries)
        new_individual.chromosome = {k: v.copy() for k, v in self.chromosome.items()}
        new_individual.fitness = self.fitness
        new_individual.is_valid = self.is_valid
        return new_individual


class GeneticAlgorithm:
    """Genetic Algorithm ana sınıfı"""
    
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], 
                 no_fly_zones: List[NoFlyZone], graph: DeliveryGraph):
        self.drones = drones
        self.deliveries = deliveries
        self.no_fly_zones = no_fly_zones
        self.graph = graph
        
        # GA parametreleri
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 5
        
        self.population = []
        self.best_individual = None
        self.fitness_history = []
        
    def initialize_population(self):
        """Başlangıç popülasyonunu oluştur"""
        self.population = []
        
        for _ in range(self.population_size):
            individual = Individual(self.drones, self.deliveries)
            individual.randomize()
            individual.repair()
            individual.calculate_fitness(self.graph, self.no_fly_zones)
            self.population.append(individual)
            
    def selection(self, tournament_size: int = 3) -> Individual:
        """Tournament selection ile ebeveyn seç"""
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
        
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """İki ebeveynden çaprazlama ile yeni bireyler üret"""
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        if random.random() < self.crossover_rate:
            # Drone bazlı çaprazlama
            crossover_point = random.randint(1, len(self.drones) - 1)
            drone_ids = [drone.id for drone in self.drones]
            
            for i in range(crossover_point):
                drone_id = drone_ids[i]
                # Teslimatları değiştir
                child1.chromosome[drone_id], child2.chromosome[drone_id] = \
                    child2.chromosome[drone_id].copy(), child1.chromosome[drone_id].copy()
                    
            # Çakışan teslimatları temizle
            self._resolve_conflicts(child1)
            self._resolve_conflicts(child2)
            
        return child1, child2
        
    def _resolve_conflicts(self, individual: Individual):
        """Çakışan teslimatları çöz"""
        all_deliveries = []
        for delivery_list in individual.chromosome.values():
            all_deliveries.extend(delivery_list)
            
        # Tekrarlananları bul
        unique_deliveries = list(set(all_deliveries))
        duplicates = [d for d in all_deliveries if all_deliveries.count(d) > 1]
        
        # Tekrarları temizle
        for drone_id in individual.chromosome:
            individual.chromosome[drone_id] = [d for d in individual.chromosome[drone_id] 
                                             if d not in duplicates or 
                                             individual.chromosome[drone_id].index(d) == 0]
                                             
    def mutate(self, individual: Individual):
        """Mutasyon operatörü"""
        if random.random() < self.mutation_rate:
            mutation_type = random.choice(['swap', 'move', 'add', 'remove'])
            
            if mutation_type == 'swap':
                self._swap_mutation(individual)
            elif mutation_type == 'move':
                self._move_mutation(individual)
            elif mutation_type == 'add':
                self._add_mutation(individual)
            elif mutation_type == 'remove':
                self._remove_mutation(individual)
                
        individual.repair() # Kapasiteyi yine kontrol et
         #Mutasyon türleri ---
    def _swap_mutation(self, individual: Individual):
        """İki drone arasında teslimat değişimi"""
        drone_ids = [d.id for d in self.drones if individual.chromosome[d.id]]
        if len(drone_ids) >= 2:
            drone1, drone2 = random.sample(drone_ids, 2)
            
            if (individual.chromosome[drone1] and individual.chromosome[drone2]):
                # Rastgele teslimat seç ve değiştir
                delivery1 = random.choice(individual.chromosome[drone1])
                delivery2 = random.choice(individual.chromosome[drone2])
                
                # Değiştir
                individual.chromosome[drone1].remove(delivery1)
                individual.chromosome[drone2].remove(delivery2)
                individual.chromosome[drone1].append(delivery2)
                individual.chromosome[drone2].append(delivery1)
                
    def _move_mutation(self, individual: Individual):
        """Bir teslimatı başka drone'a taşı"""
        # Teslimatı olan drone'ları bul
        source_drones = [d.id for d in self.drones if individual.chromosome[d.id]]
        
        if source_drones:
            source_drone = random.choice(source_drones)
            target_drone = random.choice([d.id for d in self.drones])
            
            if individual.chromosome[source_drone]:
                delivery = random.choice(individual.chromosome[source_drone])
                individual.chromosome[source_drone].remove(delivery)
                individual.chromosome[target_drone].append(delivery)
                
    def _add_mutation(self, individual: Individual):
        """Atanmamış teslimat ekle"""
        assigned_deliveries = set()
        for delivery_list in individual.chromosome.values():
            assigned_deliveries.update(delivery_list)
            
        unassigned = [d.id for d in self.deliveries if d.id not in assigned_deliveries]
        
        if unassigned:
            delivery_id = random.choice(unassigned)
            drone_id = random.choice([d.id for d in self.drones])
            individual.chromosome[drone_id].append(delivery_id)
            
    def _remove_mutation(self, individual: Individual):
        """Rastgele teslimat kaldır"""
        drone_ids = [d.id for d in self.drones if individual.chromosome[d.id]]
        
        if drone_ids:
            drone_id = random.choice(drone_ids)
            if individual.chromosome[drone_id]:
                delivery = random.choice(individual.chromosome[drone_id])
                individual.chromosome[drone_id].remove(delivery)
                
    def evolve(self) -> Individual:
        """GA'yı çalıştır ve en iyi çözümü döndür"""
        print("Genetic Algorithm başlatılıyor...")
        
        # Başlangıç popülasyonu
        self.initialize_population()
        
        for generation in range(self.generations):
            # Fitness değerlendirmesi
            for individual in self.population:
                individual.calculate_fitness(self.graph, self.no_fly_zones)
                
            # En iyi bireyi bul
            current_best = max(self.population, key=lambda x: x.fitness)
            if self.best_individual is None or current_best.fitness > self.best_individual.fitness:
                self.best_individual = current_best.copy()
                
            self.fitness_history.append(current_best.fitness)
            
            # İlerleme raporu
            if generation % 10 == 0:
                avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
                print(f"Nesil {generation}: En iyi fitness = {current_best.fitness:.2f}, "
                      f"Ortalama = {avg_fitness:.2f}")
                
            # Yeni nesil oluştur
            new_population = []
            
            # Elite seçimi
            elite = sorted(self.population, key=lambda x: x.fitness, reverse=True)[:self.elite_size]
            new_population.extend([ind.copy() for ind in elite])
            
            # Geri kalan popülasyonu üret
            while len(new_population) < self.population_size:
                parent1 = self.selection()
                parent2 = self.selection()
                
                child1, child2 = self.crossover(parent1, parent2)
                
                self.mutate(child1)
                self.mutate(child2)
                
                child1.calculate_fitness(self.graph, self.no_fly_zones)
                child2.calculate_fitness(self.graph, self.no_fly_zones)
                
                new_population.extend([child1, child2])
                
            # Popülasyon boyutunu ayarla
            self.population = new_population[:self.population_size]
            
        print(f"GA tamamlandı. En iyi fitness: {self.best_individual.fitness:.2f}")
        return self.best_individual
        
    def get_solution_routes(self, individual: Individual) -> Dict[int, List[str]]:
        """Çözümden drone rotalarını çıkar"""
        routes = {}
        
        for drone_id, delivery_list in individual.chromosome.items():
            if delivery_list:
                route = [f"drone_{drone_id}"]
                
                # Teslimatları öncelik sırasına göre sırala
                deliveries = [next(d for d in self.deliveries if d.id == did) for did in delivery_list]
                deliveries.sort(key=lambda x: x.priority, reverse=True)
                
                for delivery in deliveries:
                    route.append(f"delivery_{delivery.id}")
                    
                routes[drone_id] = route
            else:
                routes[drone_id] = []
                
        return routes
        
    def print_solution(self, individual: Individual):
        """Çözümü yazdır"""
        print("\nGenetic Algorithm Çözümü:")
        print("=" * 60)
        print(f"Fitness Skoru: {individual.fitness:.2f}")
        
        total_deliveries = 0
        total_weight = 0.0
        
        for drone_id, delivery_list in individual.chromosome.items():
            drone = next(d for d in self.drones if d.id == drone_id)
            print(f"\nDrone {drone_id} (Kapasite: {drone.max_weight}kg, Batarya: {drone.battery}mAh):")
            
            if delivery_list:
                drone_weight = 0
                for delivery_id in delivery_list:
                    delivery = next(d for d in self.deliveries if d.id == delivery_id)
                    drone_weight += delivery.weight
                    total_weight += delivery.weight
                    print(f"  - Teslimat {delivery_id}: Pos{delivery.pos}, "
                          f"Ağırlık: {delivery.weight}kg, Öncelik: {delivery.priority}")
                    
                total_deliveries += len(delivery_list)
                print(f"  Toplam ağırlık: {drone_weight:.1f}kg")
                print(f"  Kapasite kullanımı: %{(drone_weight/drone.max_weight)*100:.1f}")
            else:
                print("  - Teslimat atanmamış")
                
        print(f"\nÖzet:")
        print(f"- Toplam teslimat: {total_deliveries}/{len(self.deliveries)}")
        print(f"- Kapsama oranı: %{(total_deliveries/len(self.deliveries))*100:.1f}")
        print(f"- Toplam ağırlık: {total_weight:.1f}kg")
        
        active_drones = sum(1 for dl in individual.chromosome.values() if dl)
        print(f"- Aktif drone sayısı: {active_drones}/{len(self.drones)}")
