"""
Graf oluşturma modülü - Teslimat noktalarını düğüm, drone hareketlerini kenar olarak modellemek için
Bu dosya, tüm drone başlangıç noktaları ile teslimat lokasyonları arasındaki mesafeleri ve yasak bölgeleri dikkate alarak bir bağlantı ağı kurar; böylece algoritmalar, hangi drone’un hangi noktaya hangi maliyetle ulaşacağını hesaplayabilir.
"""
import math
from typing import List, Dict, Tuple, Set
from .drone import Drone # Drone bilgilerini kullanmak için
from .delivery_point import DeliveryPoint # Teslimat noktası bilgileri
from .no_fly_zone import NoFlyZone # Uçuşa yasak bölgeler için

class DeliveryGraph:
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone]):
        self.drones = drones # Tüm drone'ları saklar
        self.deliveries = deliveries # Teslimat noktalarını saklar
        self.no_fly_zones = no_fly_zones # Uçuşa yasak bölgeleri saklar
        self.graph = {}  # Komşuluk listesi (düğümden komşulara bağlantı)
        self.nodes = []  # Düğüm listesi (teslimatlar + drone başlangıçları)
        self.edges = {}  # Kenar maliyetleri (düğüm çifti -> maliyet)
        self.build_graph() # Başlangıçta grafı oluştur
        
    def build_graph(self):
        """Graf yapısını oluştur"""
        # Düğümleri oluştur
        self.nodes = [] # Düğümleri sıfırla
        
         # Drone başlangıç pozisyonlarını düğüm olarak ekle
        for drone in self.drones:
            node_id = f"drone_{drone.id}"
            self.nodes.append(node_id)
            self.graph[node_id] = {
                'pos': drone.start_pos, # Konum bilgisi
                'type': 'drone_start', # Tür bilgisi
                'drone_id': drone.id, # Drone kimliği
                'neighbors': [] # Komşu düğümler
            }
            
        # Teslimat noktalarını düğüm olarak ekle
        for delivery in self.deliveries:
            node_id = f"delivery_{delivery.id}"
            self.nodes.append(node_id)
            self.graph[node_id] = {
                'pos': delivery.pos, # Teslimat konumu
                'type': 'delivery', # Tür bilgisi
                'delivery_id': delivery.id, # Teslimat kimliği
                'weight': delivery.weight, # Paket ağırlığı
                'priority': delivery.priority, # Öncelik seviyesi
                'time_window': delivery.time_window, # Zaman aralığı
                'neighbors': [] # Komşular
            }
            
        # Kenarları oluştur
        self.build_edges() 
        
    def build_edges(self):
        """Tüm düğümler arasındaki kenarları oluştur"""
        for i, node1_id in enumerate(self.nodes):
            for j, node2_id in enumerate(self.nodes):
                if i != j: # Aynı düğümle bağlantı kurma
                    node1 = self.graph[node1_id]
                    node2 = self.graph[node2_id]
                    
                    # Kenar maliyetini hesapla
                    cost = self.calculate_edge_cost(node1, node2)
                    
                    # Komşuluk listesine ekle
                    self.graph[node1_id]['neighbors'].append({
                        'node_id': node2_id,
                        'cost': cost
                    })
                    
                    # Kenar maliyetini kaydet
                    self.edges[(node1_id, node2_id)] = cost 
                    
    def calculate_edge_cost(self, node1: Dict, node2: Dict) -> float:
        """İki düğüm arasındaki kenar maliyetini hesapla (PDF'deki formüle göre)"""
        distance = self.euclidean_distance(node1['pos'], node2['pos'])
        
        # Temel maliyet: mesafe
        base_cost = distance
        
        # Ağırlık maliyeti (sadece teslimat noktaları için)
        weight_cost = 0
        if node2['type'] == 'delivery':
            weight_cost = node2['weight'] * 100
            
        # Öncelik cezası (düşük öncelikli teslimatlar için)
        priority_penalty = 0
        if node2['type'] == 'delivery':
            priority_penalty = (6 - node2['priority']) * 100
            
        # No-fly zone cezası
        no_fly_penalty = self.calculate_no_fly_penalty(node1['pos'], node2['pos'])
        
        total_cost = base_cost + weight_cost + priority_penalty + no_fly_penalty # Toplam maliyet
        return total_cost
        
    def euclidean_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """İki nokta arasındaki Öklid mesafesini hesapla"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
    def calculate_no_fly_penalty(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> float:
        """No-fly zone cezasını hesapla"""
        penalty = 0
        
        for zone in self.no_fly_zones:
            # Rotanın yasak bölge ile kesişip kesişmediğini kontrol et
            if zone.line_intersects_polygon(start_pos, end_pos):
                penalty += 2000  # Yüksek ceza
                
        return penalty
        
    def get_neighbors(self, node_id: str) -> List[Dict]:
        """Bir düğümün komşularını getir"""
        return self.graph[node_id]['neighbors']
        
    def get_node_info(self, node_id: str) -> Dict:
        """Düğüm bilgilerini getir"""
        return self.graph[node_id]
        
    def get_edge_cost(self, node1_id: str, node2_id: str) -> float:
        """İki düğüm arasındaki kenar maliyetini getir"""
        return self.edges.get((node1_id, node2_id), float('inf'))
        
    def is_path_valid(self, path: List[str], drone: Drone, current_time: int = 0) -> bool:
        """Bir rotanın geçerli olup olmadığını kontrol et"""
        if not path:
            return True
            
        # Drone kapasitesini kontrol et
        total_weight = 0 # Toplam yük kontrolü
        temp_time = current_time # Geçici zaman takibi
        
        for i, node_id in enumerate(path):
            if node_id.startswith('delivery_'):
                node_info = self.get_node_info(node_id) 
                total_weight += node_info['weight'] # Ağırlık birikimi
                
                # Kapasite aşımı kontrolü
                if total_weight > drone.max_weight:
                    return False
                    
                # Zaman penceresi kontrolü
                if i > 0:
                    prev_node = path[i-1]
                    travel_time = self.get_travel_time(prev_node, node_id, drone)
                    temp_time += travel_time
                    
                time_window = node_info['time_window']
                if not (time_window[0] <= temp_time <= time_window[1]):
                    return False
                    
        return True
        
    def get_travel_time(self, node1_id: str, node2_id: str, drone: Drone) -> float:
        """İki düğüm arasındaki seyahat süresini hesapla"""
        node1 = self.get_node_info(node1_id)
        node2 = self.get_node_info(node2_id)
        distance = self.euclidean_distance(node1['pos'], node2['pos'])
        return distance / drone.speed # Hız formülü
        
    def get_deliveries_in_range(self, drone: Drone, max_distance: float = None) -> List[str]:
        """Belirtilen mesafedeki teslimat noktalarını getir"""
        if max_distance is None:
            max_distance = float('inf')
            
        deliveries_in_range = []
        drone_pos = drone.current_pos
        
        for node_id in self.nodes:
            if node_id.startswith('delivery_'):
                node_info = self.get_node_info(node_id)
                distance = self.euclidean_distance(drone_pos, node_info['pos'])
                
                if distance <= max_distance and drone.can_carry(node_info['weight']):  # Erişim mesafesi ve taşıma kontrolü
                    deliveries_in_range.append(node_id)
                    
        return deliveries_in_range
        
    def print_graph_stats(self):
        """Graf istatistiklerini yazdır"""
        print(f"Graf İstatistikleri:")
        print(f"- Toplam düğüm sayısı: {len(self.nodes)}")
        print(f"- Toplam kenar sayısı: {len(self.edges)}")
        print(f"- Drone başlangıç noktaları: {len(self.drones)}")
        print(f"- Teslimat noktaları: {len(self.deliveries)}")
        print(f"- No-fly zone sayısı: {len(self.no_fly_zones)}")
        
    def visualize_graph(self):
        """Graf görselleştirmesi için gerekli verileri hazırla"""
        nodes_data = []
        edges_data = []
        
        for node_id in self.nodes:
            node_info = self.get_node_info(node_id)
            nodes_data.append({
                'id': node_id,
                'pos': node_info['pos'],
                'type': node_info['type']
            })
            
        for (node1_id, node2_id), cost in self.edges.items():
            edges_data.append({
                'from': node1_id,
                'to': node2_id,
                'cost': cost
            })
            
        return nodes_data, edges_data
