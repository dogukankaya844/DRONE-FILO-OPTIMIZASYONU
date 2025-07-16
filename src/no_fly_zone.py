"""
Uçuş yasağı bölgesi sınıfı - No-fly zone özelliklerini yönetir
Bu dosya, drone teslimat sisteminde uçuş yasağı bölgelerini (No-Fly Zones) tanımlamak ve yönetmek için kullanılır.
"""
from typing import List, Tuple
import math

class NoFlyZone:
    def __init__(self, id: int, coordinates: List[Tuple[float, float]], active_time: Tuple[int, int]):
        self.id = id  # No-fly bölge kimliği
        self.coordinates = coordinates # Bölgeyi tanımlayan çokgen koordinatları
        self.active_time = active_time # Bölgenin aktif olduğu zaman aralığı (başlangıç, bitiş)
        
    def is_active(self, current_time: int) -> bool:
        """Belirtilen zamanda bölge aktif mi kontrol et"""
        return self.active_time[0] <= current_time <= self.active_time[1] # Zaman kontrolü
        
    def point_in_polygon(self, point: Tuple[float, float]) -> bool:
        """Bir noktanın çokgen içinde olup olmadığını kontrol et (Ray casting algoritması)"""
        x, y = point # Noktanın koordinatları
        n = len(self.coordinates) # Çokgendeki köşe sayısı
        inside = False  # Başlangıçta dışarıda kabul edilir
        
        p1x, p1y = self.coordinates[0] # İlk köşe
        for i in range(1, n + 1):
            p2x, p2y = self.coordinates[i % n] # Sıradaki köşe (mod alarak kapanışı sağlar)
            if y > min(p1y, p2y):  # Y ekseni aralığına bak
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x # Kesim noktası X
                        if p1x == p2x or x <= xinters:
                            inside = not inside # İçeride/dışarıda geçiş
            p1x, p1y = p2x, p2y # Bir sonraki kenar için ilerle
            
        return inside # Sonuç olarak içeride mi dışarıda mı
        
    def line_intersects_polygon(self, start: Tuple[float, float], end: Tuple[float, float]) -> bool:
        """Bir çizginin çokgen ile kesişip kesişmediğini kontrol et"""
        # Başlangıç veya bitiş noktası polygon içindeyse kesişir
        if self.point_in_polygon(start) or self.point_in_polygon(end):
            return True
            
        # Çizgi polygon kenarlarıyla kesişiyor mu kontrol et
        n = len(self.coordinates)
        for i in range(n):
            p1 = self.coordinates[i]
            p2 = self.coordinates[(i + 1) % n] # Döngüsel kenar kapatma
            if self.line_segments_intersect(start, end, p1, p2):
                return True # Kesişim varsa
                
        return False # Hiçbiriyle kesişmiyorsa False
        
    def line_segments_intersect(self, p1: Tuple[float, float], q1: Tuple[float, float], 
                               p2: Tuple[float, float], q2: Tuple[float, float]) -> bool:
        """İki çizgi parçasının kesişip kesişmediğini kontrol et"""
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1]) # Yön belirleme formülü
            if val == 0:
                return 0   # Doğrusal (aynı doğru üzerinde)
            return 1 if val > 0 else 2  # Saat yönü (1) veya tersi (2)
            
        def on_segment(p, q, r): # q noktası p ve r arasında mı?
            return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                    q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
                    
        o1 = orientation(p1, q1, p2) # İlk çizgi ve p2
        o2 = orientation(p1, q1, q2) # İlk çizgi ve q2
        o3 = orientation(p2, q2, p1) # İkinci çizgi ve p1
        o4 = orientation(p2, q2, q1) # İkinci çizgi ve q1
        
         # Genel durumda kesişim kontrolü
        if o1 != o2 and o3 != o4:
            return True
            
        # Özel durumlar: doğrusal ve kesişme olabilir
        if (o1 == 0 and on_segment(p1, p2, q1)) or \
           (o2 == 0 and on_segment(p1, q2, q1)) or \
           (o3 == 0 and on_segment(p2, p1, q2)) or \
           (o4 == 0 and on_segment(p2, q1, q2)):
            return True
            
        return False # Kesişim yok
        
    def get_penalty(self, current_time: int) -> float:
        """Yasak bölgeye girme cezasını hesapla"""
        if self.is_active(current_time):
            return 2000  # Aktifse yüksek ceza uygulanır
        return 0 # Değilse ceza yok
        
    def get_center(self) -> Tuple[float, float]:
        """Polygon'un merkez noktasını hesapla"""
        sum_x = sum(coord[0] for coord in self.coordinates) # X koordinatları toplamı
        sum_y = sum(coord[1] for coord in self.coordinates) # Y koordinatları toplamı
        return (sum_x / len(self.coordinates), sum_y / len(self.coordinates)) # Ortalama alınır
        
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Polygon'un sınırlayıcı kutusunu hesapla (min_x, min_y, max_x, max_y)"""
        min_x = min(coord[0] for coord in self.coordinates)
        max_x = max(coord[0] for coord in self.coordinates)
        min_y = min(coord[1] for coord in self.coordinates)
        max_y = max(coord[1] for coord in self.coordinates)
        return (min_x, min_y, max_x, max_y) # Dört köşe değeri döndürülür
        
    def __str__(self) -> str:
        return f"NoFlyZone {self.id}: Coordinates: {self.coordinates}, Active: {self.active_time}"  # Yazdırıldığında okunabilir format
        
    def __repr__(self) -> str:
        return self.__str__() # Listeler içinde veya konsolda temsilini verir
 