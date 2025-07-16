"""
Drone sınıfı - Drone özelliklerini ve durumunu yönetir
Bu dosya, her bir drone’un konumu, batarya durumu, taşıma kapasitesi, enerji tüketimi ve teslimat süreci gibi tüm operasyonel davranışlarını kontrol ederek, rota planlama ve görev atama algoritmalarının doğru çalışmasını sağlar.
"""
import math
from typing import List, Tuple, Optional

class Drone:
    def __init__(self, id: int, max_weight: float, battery: int, speed: float, start_pos: Tuple[float, float]):
        self.id = id # Drone kimliği
        self.max_weight = max_weight # Taşıyabileceği en fazla ağırlık (kg)
        self.battery = battery  # Mevcut batarya (mAh)
        self.max_battery = battery # Tam şarj kapasitesi (sabit)
        self.speed = speed # Uçuş hızı (m/s)
        self.start_pos = start_pos  # Üs konumu
        self.current_pos = start_pos # Anlık konum
        self.current_weight = 0.0 # Taşınan toplam ağırlık
        self.route = [] # Ziyaret edilen noktalar listesi
        self.deliveries = []  # Tamamlanan teslimat kimlikleri
        self.is_charging = False  # Şarjda mı?
        self.charging_time = 0 # Şarjda geçirilen süre
        self.total_distance = 0.0 # Kat edilen mesafe (m)
        self.total_time = 0.0 # Uçuş süresi (s)
        
    def reset(self):
        """Drone'u başlangıç durumuna döndür"""
        self.current_pos = self.start_pos
        self.current_weight = 0.0
        self.battery = self.max_battery
        self.route = []
        self.deliveries = []
        self.is_charging = False
        self.charging_time = 0
        self.total_distance = 0.0
        self.total_time = 0.0
        
    def can_carry(self, weight: float) -> bool:
        """Drone'un ek ağırlık taşıyıp taşıyamayacağını kontrol et"""
        return self.current_weight + weight <= self.max_weight
        
    def get_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """İki nokta arasındaki Öklid mesafesini hesapla"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
    def calculate_energy_consumption(self, distance: float, weight: float) -> float:
        """Mesafe ve ağırlığa göre enerji tüketimini hesapla"""
        base_consumption = distance * 10  # Mesafeye bağlı temel tüketim
        weight_factor = 1 + (weight / self.max_weight) * 0.5  # Yük arttıkça tüketim artar
        return base_consumption * weight_factor
        
    def can_reach(self, destination: Tuple[float, float], package_weight: float) -> bool:
        """Hedef noktaya ulaşabilir mi kontrol et"""
        distance = self.get_distance(self.current_pos, destination)
        energy_needed = self.calculate_energy_consumption(distance, self.current_weight + package_weight)
        return self.battery >= energy_needed
        
    def move_to(self, destination: Tuple[float, float], package_weight: float = 0.0) -> bool:
        """Belirtilen noktaya uçuş (enerji ve zaman güncellenir)"""
        if not self.can_reach(destination, package_weight):
            return False
            
        distance = self.get_distance(self.current_pos, destination)
        energy_consumed = self.calculate_energy_consumption(distance, self.current_weight + package_weight)
        time_taken = distance / self.speed
        
        self.current_pos = destination
        self.battery -= energy_consumed
        self.total_distance += distance
        self.total_time += time_taken
        self.route.append(destination)
        
        return True
        
    def pick_up_package(self, weight: float) -> bool:
        """Paket alma işlemi (ağırlık ekler)"""
        if self.can_carry(weight):
            self.current_weight += weight
            return True
        return False
        
    def deliver_package(self, weight: float, delivery_id: int) -> bool:
        """Paket teslim etme (ağırlık düşer, teslimat kaydedilir)"""
        if self.current_weight >= weight:
            self.current_weight -= weight
            self.deliveries.append(delivery_id)
            return True
        return False
        
    def needs_charging(self) -> bool:
        """Şarj gerekiyor mu kontrol et"""
        return self.battery < self.max_battery * 0.2  # %20'nin altında şarj gerekir
        
    def charge(self, time_units: int = 1) -> bool:
        """Drone'u Üs konumunda şarj et"""
        if self.current_pos == self.start_pos:
            charge_rate = self.max_battery * 0.1  # Her birim zamanda %10 şarj
            self.battery = min(self.max_battery, self.battery + charge_rate * time_units)
            self.charging_time += time_units
            return True
        return False
        
    def return_to_base(self) -> bool:
        """Enerji yeterliyse üsse dön"""
        distance = self.get_distance(self.current_pos, self.start_pos)
        energy_needed = self.calculate_energy_consumption(distance, self.current_weight)
        
        if self.battery >= energy_needed:
            self.move_to(self.start_pos)
            return True
        return False
        
    def get_fitness_score(self) -> float:
        """Genetik algoritma için fitness skoru hesapla"""
        delivery_score = len(self.deliveries) * 100
        energy_penalty = (self.max_battery - self.battery) * 0.1
        distance_penalty = self.total_distance * 0.5
        
        return delivery_score - energy_penalty - distance_penalty
        
    def __str__(self) -> str:
        return f"Drone {self.id}: Pos({self.current_pos[0]:.1f},{self.current_pos[1]:.1f}), Weight: {self.current_weight:.1f}/{self.max_weight}, Battery: {self.battery:.0f}/{self.max_battery}, Deliveries: {len(self.deliveries)}"
        
    def __repr__(self) -> str:
        return self.__str__()
