"""
Teslimat noktası sınıfı - Teslimat özelliklerini yönetir
Bu dosya, proje kapsamında her teslimat noktasının özelliklerini ve durumunu yönetmek için kullanılır. Teslimatların zamanında, önceliklerine uygun ve doğru şekilde gerçekleştirilmesini sağlamak amacıyla gerekli fonksiyonları sağlar.
"""
from typing import Tuple

class DeliveryPoint:
    def __init__(self, id: int, pos: Tuple[float, float], weight: float, priority: int, time_window: Tuple[int, int]):
        self.id = id # Teslimat noktasının benzersiz kimliği
        self.pos = pos # Teslimatın yapılacağı konum (x, y koordinatları)
        self.weight = weight # Teslimatın ağırlığı (kg cinsinden)
        self.priority = priority  # Teslimat öncelik seviyesi (1-5 arası, 5 en yüksek öncelik)
        self.time_window = time_window  # Teslimatın yapılması gereken zaman aralığı (başlangıç ve bitiş zamanı)
        self.is_delivered = False  # Teslimatın tamamlanıp tamamlanmadığını gösteren bayrak
        self.delivery_time = None # Teslimatın gerçekleştiği zaman (int, sistem zamanıyla)
        self.assigned_drone = None # Teslimatı gerçekleştiren drone'un kimliği
        
    def is_within_time_window(self, current_time: int) -> bool:
        """Mevcut zaman teslimat penceresinde mi kontrol et"""
        return self.time_window[0] <= current_time <= self.time_window[1]
        
    def get_priority_penalty(self) -> float:
        """Öncelik seviyesine göre ceza hesapla"""
        # Yüksek öncelikli teslimatlar (5) daha az ceza alır
        return (6 - self.priority) * 100
        
    def get_time_penalty(self, current_time: int) -> float:
        """Zaman penceresi dışında teslimat yapmak için ceza hesapla"""
        if self.is_within_time_window(current_time):
            return 0 # Zaman penceresi içindeyse ceza yok
        elif current_time < self.time_window[0]:
            # Erken teslimat cezası
            return (self.time_window[0] - current_time) * 50
        else:
            # Geç teslimat cezası (daha ağır)
            return (current_time - self.time_window[1]) * 100
            
    def mark_delivered(self, delivery_time: int, drone_id: int):
        """Teslimatı tamamlanmış olarak işaretle"""
        self.is_delivered = True
        self.delivery_time = delivery_time
        self.assigned_drone = drone_id
        
    def reset(self):
        """Teslimat durumunu yeniden aktif (tamamlanmamış) hale getirir, önceki bilgileri temizler"""
        self.is_delivered = False
        self.delivery_time = None
        self.assigned_drone = None
        
    def __str__(self) -> str:
        """Nesnenin okunabilir string hali, teslimat durumu ile birlikte temel bilgileri verir"""
        status = "Delivered" if self.is_delivered else "Pending"
        return f"Delivery {self.id}: Pos({self.pos[0]:.1f},{self.pos[1]:.1f}), Weight: {self.weight}kg, Priority: {self.priority}, Time Window: {self.time_window}, Status: {status}"
        
    def __repr__(self) -> str:
        return self.__str__()
