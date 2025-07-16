"""
A* Algoritması implementasyonu - PDF'deki formüle göre optimum rota bulma
Bu modül, drone’un gerçek zamanlı karar verme süreçlerinde en iyi hareket rotasını bulmasını sağlar. 
"""
import heapq # Öncelikli kuyruk için (A* algoritmasında açık düğümleri tutmak için)
import math # Matematiksel işlemler için (örneğin mesafe hesapları)
from typing import List, Dict, Tuple, Optional, Set # Tip ipuçları için
from .graph_builder import DeliveryGraph # Projedeki teslimat grafı sınıfı
from .drone import Drone # Drone sınıfı (özellikleri, kapasite vb.)
from .no_fly_zone import NoFlyZone  # Uçuşa yasak alanların modeli

class AStarPathfinder:
    def __init__(self, graph: DeliveryGraph):
        self.graph = graph # Teslimat noktaları ve no-fly zone içeren grafik objesini saklar
        
    def heuristic(self, node1_id: str, node2_id: str, current_time: int = 0) -> float:
        """
        A* heuristik fonksiyonu - PDF'deki formüle göre
        h = distance + no_fly_zone_penalty
        """
        node1 = self.graph.get_node_info(node1_id) # Başlangıç düğüm bilgisi (koordinatlar vs.)
        node2 = self.graph.get_node_info(node2_id) # Hedef düğüm bilgisi
        
        # Temel mesafe hesaplanır
        distance = self.graph.euclidean_distance(node1['pos'], node2['pos'])
        
        # No-fly zone cezası: Eğer güzergah no-fly zone ile kesişiyorsa ekstra ceza eklenir
        no_fly_penalty = 0
        for zone in self.graph.no_fly_zones:
            if zone.is_active(current_time) and zone.line_intersects_polygon(node1['pos'], node2['pos']):
                no_fly_penalty += 1000  # Heuristik için daha düşük ceza
                
        return distance + no_fly_penalty # Toplam heuristik değer döner
        
    def find_path(self, start_node: str, goal_nodes: List[str], drone: Drone, 
                  current_time: int = 0, avoid_nodes: Set[str] = None) -> Optional[List[str]]:
        """
        A* algoritması ile start_node'dan goal_nodes listesindeki herhangi bir düğüme 
        drone özellikleri ve zaman kısıtlarını dikkate alarak en kısa uygun yolu bulur.
        start_node: başlangıç düğümü
        goal_nodes: hedef düğümler listesi
        drone: rota planlanan drone
        current_time: mevcut zaman
        avoid_nodes: kaçınılması gereken düğümler
        """
        if avoid_nodes is None:
            avoid_nodes = set() # Default boş küme (kaçınılacak düğüm yok)
            
        #Açık düğümler öncelik kuyruğu (f_score, g_score, düğüm id, takip edilen yol, geçen zaman, ağırlık)
        open_set = []
        heapq.heappush(open_set, (0, 0, start_node, [start_node], current_time, 0.0))
        
        # Ziyaret edilen düğümler
        visited = set() 
        
        # En iyi g_score'lar
        g_scores = {start_node: 0} # Başlangıç düğümünün maliyeti 0
        
        while open_set:
            f_score, g_score, current_node, path, time, current_weight = heapq.heappop(open_set)
            
            # Hedef düğümlerden birine ulaştık mı?
            if current_node in goal_nodes:
                return path # Hedefe ulaşıldı, yolu döndür
                
            # Bu düğümü zaten ziyaret ettik mi?
            if current_node in visited:
                continue # Önceden ziyaret edilmiş düğüme tekrar bakma
                
            visited.add(current_node) # Düğüm ziyaret edildi olarak işaretlenir
            
            # Komşuları kontrol et
            neighbors = self.graph.get_neighbors(current_node)  # Komşu düğümleri al
            
            for neighbor_info in neighbors:
                neighbor_node = neighbor_info['node_id']
                
                # Kaçınılması gereken düğümler
                if neighbor_node in avoid_nodes:
                    continue # Kaçınılan düğümlere gitme
                    
                # Drone kapasitesi kontrolü
                neighbor_data = self.graph.get_node_info(neighbor_node)
                new_weight = current_weight
                
                if neighbor_data['type'] == 'delivery':
                    new_weight += neighbor_data['weight'] # Yeni teslimat ağırlığı ekle
                    if new_weight > drone.max_weight:
                        continue # Drone kapasitesi aşılırsa atla
                        
                # Zaman penceresi kontrolü
                travel_time = self.graph.get_travel_time(current_node, neighbor_node, drone)
                new_time = time + travel_time
                
                if neighbor_data['type'] == 'delivery':
                    time_window = neighbor_data['time_window']
                    if not (time_window[0] <= new_time <= time_window[1]):
                        continue # Teslimat zaman penceresine uymazsa atla
                
                # Yeni g_score hesapla
                edge_cost = self.graph.get_edge_cost(current_node, neighbor_node)
                tentative_g_score = g_score + edge_cost
                
                # Bu daha iyi bir yol mu?
                if neighbor_node not in g_scores or tentative_g_score < g_scores[neighbor_node]:
                    g_scores[neighbor_node] = tentative_g_score
                    
                    # En yakın hedef düğüme heuristik hesapla
                    h_score = min(self.heuristic(neighbor_node, goal, new_time) for goal in goal_nodes)
                    f_score = tentative_g_score + h_score
                    
                    new_path = path + [neighbor_node]
                    # Kuyruğa ekle (öncelik f_score)
                    heapq.heappush(open_set, (f_score, tentative_g_score, neighbor_node, 
                                            new_path, new_time, new_weight))
        
        return None  # Yol bulunamadıysa None döner
        
    def find_optimal_delivery_route(self, drone: Drone, available_deliveries: List[str], 
                                   current_time: int = 0) -> Tuple[List[str], float]:
        """
        Tek bir drone için, verilen teslimatlar arasından en uygun rotayı bul.
        """
        if not available_deliveries:
            return [], 0.0 # Teslimat yoksa boş yol ve 0 maliyet
            
        drone_start = f"drone_{drone.id}" # Başlangıç düğümü (drone id'si ile)
        best_route = []
        best_cost = float('inf') # En iyi maliyet başta sonsuz
        
        # Her teslimat noktası için en iyi rotayı bul
        for delivery_id in available_deliveries:
            delivery_node = f"delivery_{delivery_id}"
            
            # Drone'dan teslimat noktasına rota bul
            route = self.find_path(drone_start, [delivery_node], drone, current_time)
            
            if route:
                # Rota maliyetini hesapla
                total_cost = self.calculate_route_cost(route, current_time)
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_route = route
                    
        return best_route, best_cost
        
    def find_multi_delivery_route(self, drone: Drone, delivery_list: List[str], 
                                 current_time: int = 0, max_deliveries: int = 5) -> List[str]:
        """
        Bir drone için, teslimat listesinden maksimum (max_deliveries) sayıda teslimatı
        greedy (açgözlü) yöntemle seçerek, uygun en iyi rotayı oluşturur.
        """
        if not delivery_list:
            return [] # Teslimat yoksa boş yol
            
        route = [f"drone_{drone.id}"] # Başlangıç noktası
        remaining_deliveries = set(delivery_list)
        current_node = f"drone_{drone.id}"
        current_weight = 0.0
        time = current_time
        
        while remaining_deliveries and len(route) - 1 < max_deliveries:
            best_next = None
            best_cost = float('inf')
            
            # En yakın ve uygun teslimat noktasını bul
            for delivery_id in remaining_deliveries:
                delivery_node = f"delivery_{delivery_id}"
                delivery_info = self.graph.get_node_info(delivery_node)
                
                # Kapasite kontrolü
                if current_weight + delivery_info['weight'] > drone.max_weight:
                    continue
                    
                # Zaman kontrolü
                travel_time = self.graph.get_travel_time(current_node, delivery_node, drone)
                arrival_time = time + travel_time
                
                if not (delivery_info['time_window'][0] <= arrival_time <= delivery_info['time_window'][1]):
                    continue
                    
                # Maliyet hesapla
                cost = self.graph.get_edge_cost(current_node, delivery_node)
                
                if cost < best_cost:
                    best_cost = cost
                    best_next = delivery_node
                    
            if best_next is None:
                break # Uygun teslimat kalmadı
                
            # En iyi seçimi rotaya ekle
            route.append(best_next) # En uygun teslimat eklenir
            remaining_deliveries.remove(best_next.split('_')[1]) # Teslimat çıkarılır
            
            # Durumları güncelle
            current_node = best_next
            delivery_info = self.graph.get_node_info(best_next)
            current_weight += delivery_info['weight']
            time += self.graph.get_travel_time(route[-2], best_next, drone)
            
        return route
        
    def calculate_route_cost(self, route: List[str], start_time: int = 0) -> float:
        """Rota maliyetini hesapla"""
        if len(route) < 2:
            return 0.0 # Yeterli nokta yoksa maliyet sıfır
             
        total_cost = 0.0 # Toplam maliyet toplayıcısı
         # Her ardışık düğüm çifti için maliyeti topla
        for i in range(len(route) - 1):
            cost = self.graph.get_edge_cost(route[i], route[i + 1]) # Kenar maliyetini al
            total_cost += cost # Toplam maliyete ekle
            
        return total_cost  # Tamamlanan toplam maliyeti döndür
        
    def is_route_feasible(self, route: List[str], drone: Drone, start_time: int = 0) -> bool:
        """Verilen rotanın drone kapasitesi, zaman pencereleri ve batarya açısından geçerli olup olmadığını kontrol eder."""
        if not route:
            return True # Boş rota geçerli sayılır
            
        current_weight = 0.0 # Taşınan toplam yük
        current_time = start_time # Şu anki varış/zaman damgası
        current_battery = drone.battery # Bataryanın kalan enerjisi (mAh, Wh vs.)
        
        for i, node_id in enumerate(route):
            if node_id.startswith('delivery_'):
                node_info = self.graph.get_node_info(node_id) # Teslimat düğümü bilgisi
                
                # Kapasite kontrolü
                current_weight += node_info['weight'] # Yeni yükü ekle
                if current_weight > drone.max_weight: # Kapasiteyi aşarsa
                    return False # Kapasite aşıldı rota geçersiz
                    
                # Zaman penceresi kontrolü
                if i > 0:  # Başlangıç düğümü değilse
                     # Önceki düğümden buraya uçuş süresi
                    travel_time = self.graph.get_travel_time(route[i-1], node_id, drone)
                    current_time += travel_time #Varış zamanı güncelle
                    
                time_window = node_info['time_window'] # Kabul edilen zaman aralığı
                if not (time_window[0] <= current_time <= time_window[1]): 
                    return False # Zaman penceresine uyulmadı
                    
                # Batarya kontrolü
                if i > 0: 
                    prev_node = self.graph.get_node_info(route[i-1]) # Önceki düğüm
                    distance = self.graph.euclidean_distance(prev_node['pos'], node_info['pos']) # Uçuş mesafesi
                     # Taşıdığı mevcut yükle mesafe için gereken enerji
                    energy_needed = drone.calculate_energy_consumption(distance, current_weight)
                    current_battery -= energy_needed  # Bataryadan tüketim düş
                    
                    if current_battery < 0: # Negatifse
                        return False # Batarya yetersiz
                        
        return True # Tüm kontroller başarılıysa rota uygun
        
    def get_route_statistics(self, route: List[str], drone: Drone, start_time: int = 0) -> Dict:
        """rotaya dair mesafe, zaman, enerji tüketimi, teslimat sayısı ve maliyet gibi istatistikleri hesaplar."""
        if not route: # Boş rotaya varsayılan istatistikler
            return {'distance': 0, 'time': 0, 'energy': 0, 'deliveries': 0, 'cost': 0}
            
        total_distance = 0.0 # Toplam kat edilen mesafe
        total_time = 0.0 # Toplam uçuş süresi
        total_energy = 0.0  # Toplam enerji tüketimi
        delivery_count = 0  # Teslimat adedi
        current_weight = 0.0 # Anlık taşıma ağırlığı (kg)
         # Her ardışık düğüm çifti için istatistikleri topla
        for i in range(len(route) - 1):
            node1 = self.graph.get_node_info(route[i])
            node2 = self.graph.get_node_info(route[i + 1])
            
            # Mesafe
            distance = self.graph.euclidean_distance(node1['pos'], node2['pos'])
            total_distance += distance
            
            # Zaman
            travel_time = distance / drone.speed
            total_time += travel_time
            
            # Teslimat ve ağırlık yönetimi
            if node2['type'] == 'delivery':
                current_weight += node2['weight'] # Yeni yük eklendi
                delivery_count += 1 # Teslimat sayacı
              # Enerji hesapla (yükle ilişkili) 
            energy = drone.calculate_energy_consumption(distance, current_weight)
            total_energy += energy
             # Kenar maliyetlerinin toplamı (mesafeye ek diğer maliyetler olabilir)
        total_cost = self.calculate_route_cost(route, start_time)
        
        return {
            'distance': total_distance,
            'time': total_time,
            'energy': total_energy,
            'deliveries': delivery_count,
            'cost': total_cost,
            'route': route
        }
