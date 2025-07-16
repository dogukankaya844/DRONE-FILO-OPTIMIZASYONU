"""
Görselleştirme modülü - Teslimat rotalarını ve haritayı görselleştirmek için
Bu dosya, drone teslimat senaryosundaki önemli bileşenleri grafiksel olarak görselleştirmek için kullanılır. Ayrıca algoritma performans karşılaştırmaları, genetik algoritmanın fitness evrimi ve drone kapasite kullanımı gibi analizleri grafikler halinde sunar. 
"""
import matplotlib.pyplot as plt # Grafik çizimi için temel kütüphane
import matplotlib.patches as patches # Şekiller (poligon, kutu vs) çizmek için
from matplotlib.patches import Polygon  # Çokgen çizimi için
import numpy as np # Matematiksel işlemler ve dizi yönetimi için
from typing import List, Dict, Tuple, Optional # Tip kontrolü için
from .drone import Drone # Tip kontrolü için
from .delivery_point import DeliveryPoint # Teslimat noktası nesnesi
from .no_fly_zone import NoFlyZone # Uçuş yasağı bölgesi nesnesi

class Visualizer:
    def __init__(self, map_size: Tuple[int, int] = (100, 100)):
        self.map_size = map_size # Haritanın genişlik ve yükseklik boyutları
        # Farklı drone ve rotalar için kullanacağımız renk paleti
        self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan'] 
        
    def plot_scenario(self, drones: List[Drone], deliveries: List[DeliveryPoint], 
                     no_fly_zones: List[NoFlyZone], routes: Dict[int, List] = None,
                     current_time: int = 0, save_path: str = None):
        """Senaryodaki tüm öğeleri (dronlar, teslimatlar, no-fly zone'lar ve rotalar) tek haritada gösterir"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 10)) # Grafik ve eksen oluştur
        
        # Harita sınırlarını ve oranını ayarla
        ax.set_xlim(0, self.map_size[0])
        ax.set_ylim(0, self.map_size[1])
        ax.set_aspect('equal') # X ve Y ölçekleri eşit olsun (bozulmasın)
        ax.grid(True, alpha=0.3)  # Hafif şeffaf grid çiz
        
        # No-fly zone'ları çiz
        self._plot_no_fly_zones(ax, no_fly_zones, current_time)
        
        # Teslimat noktalarını çiz
        self._plot_deliveries(ax, deliveries)
        
        # Drone'ları çiz
        self._plot_drones(ax, drones)
        
        # Rotaları çiz (varsa)
        if routes:
            self._plot_routes(ax, routes, drones, deliveries)
            
        # Başlık ve etiketler
        ax.set_title(f'Drone Teslimat Haritası (Zaman: {current_time})', fontsize=16, fontweight='bold')
        ax.set_xlabel('X Koordinatı (m)', fontsize=12)
        ax.set_ylabel('Y Koordinatı (m)', fontsize=12)
        
         # Grafik üzerinde açıklama kutusu (legend) ekle
        self._add_legend(ax, has_routes=(routes is not None))
        
        plt.tight_layout() # Grafiğin kenarlara taşmaması için ayar
        # Kaydetme yolu verilmişse resmi dosyaya kaydet
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Harita kaydedildi: {save_path}")
        
        plt.show(block=True)  # # Grafiği göster ve programın devam etmesini beklet
        plt.pause(2)  # Gösterim sonrası 2 saniye bekle
            
    def _plot_no_fly_zones(self, ax, no_fly_zones: List[NoFlyZone], current_time: int):
        """No-fly zone'ları çiz"""
        for zone in no_fly_zones:
            ## Bölge şu an aktif mi?
            is_active = zone.is_active(current_time)
            
            # Aktif bölgeler koyu kırmızı, pasifler açık kırmızı ile gösterilir
            color = 'red' if is_active else 'lightcoral'
            alpha = 0.6 if is_active else 0.3 # Aktiflik durumuna göre şeffaflık
            
             # Bölge koordinatlarından çokgen nesnesi oluştur
            polygon = Polygon(zone.coordinates, closed=True, 
                            facecolor=color, alpha=alpha, 
                            edgecolor='darkred', linewidth=2)
            ax.add_patch(polygon) # Çokgeni haritaya ekle
            
            # Bölge kimliği ve aktif/pasif durumu merkeze yazılır
            center = zone.get_center()
            status = "AKTİF" if is_active else "PASİF"
            ax.text(center[0], center[1], f'Z{zone.id}\n{status}', 
                   ha='center', va='center', fontsize=8, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                   
    def _plot_deliveries(self, ax, deliveries: List[DeliveryPoint]):
        """Teslimat noktalarını çiz"""
       # Öncelik seviyesine göre renk ve nokta büyüklükleri
        priority_colors = {1: 'lightblue', 2: 'yellow', 3: 'orange', 4: 'red', 5: 'darkred'}
        priority_sizes = {1: 50, 2: 70, 3: 90, 4: 110, 5: 130}
        
        for delivery in deliveries:
            color = priority_colors.get(delivery.priority, 'gray') # Öncelik renkleri
            size = priority_sizes.get(delivery.priority, 80) # Nokta büyüklüğü
            marker = 'o' if not delivery.is_delivered else 's' # Teslim edilmişse kare, edilmemişse daire
            
            
            # Teslimat noktası
            ax.scatter(delivery.pos[0], delivery.pos[1], c=color, s=size, 
                      marker=marker, edgecolors='black', linewidth=1.5,
                      label=f'Öncelik {delivery.priority}' if delivery.id == 1 else "")
            
            # Noktanın yanında teslimat ID ve ağırlık bilgisi gösterilir
            ax.annotate(f'T{delivery.id}\n{delivery.weight}kg', 
                       (delivery.pos[0], delivery.pos[1]), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, ha='left')
                       
    def _plot_drones(self, ax, drones: List[Drone]):
        """Drone'ları çiz"""
        for i, drone in enumerate(drones):
            color = self.colors[i % len(self.colors)] # Renk döngüsü
            
            # Drone'nun mevcut konumunu çizer
            ax.scatter(drone.current_pos[0], drone.current_pos[1], 
                      c=color, s=200, marker='^', edgecolors='black', 
                      linewidth=2, label=f'Drone {drone.id}')
            
            # Drone ID ve anlık yük bilgisi etiket olarak eklenir
            info_text = f'D{drone.id}\n{drone.current_weight:.1f}/{drone.max_weight}kg'
            ax.annotate(info_text, (drone.current_pos[0], drone.current_pos[1]), 
                       xytext=(0, -20), textcoords='offset points',
                       fontsize=8, ha='center', fontweight='bold')
                       
    def _plot_routes(self, ax, routes: Dict[int, List], drones: List[Drone], 
                    deliveries: List[DeliveryPoint]):
        """Dronların rotalarını çizgi ve ok işaretleriyle harita üzerinde gösterir"""
        for drone_id, route in routes.items():
            if not route or len(route) < 2:
                continue  # Yeterli nokta yoksa çizme
                 
            drone = next(d for d in drones if d.id == drone_id) # Drone nesnesini bul
            color = self.colors[drone_id % len(self.colors)] # Drone'nun rengi
            
            # Rota noktalarını topla
            route_points = []
            # Rotadaki her node'un (drone ya da teslimat) koordinatını al
            for node_id in route:
                if node_id.startswith('drone_'):
                    route_points.append(drone.start_pos) # Başlangıç noktası
                elif node_id.startswith('delivery_'):
                    delivery_id = int(node_id.split('_')[1])
                    delivery = next(d for d in deliveries if d.id == delivery_id)
                    route_points.append(delivery.pos)
                    
            # Noktalar arasına çizgi çiz
            if len(route_points) >= 2:
                x_coords = [p[0] for p in route_points]
                y_coords = [p[1] for p in route_points]
                
                ax.plot(x_coords, y_coords, color=color, linewidth=2, 
                       linestyle='-', alpha=0.7)
                
                # Ok işaretleri ekle
                for i in range(len(route_points) - 1):
                    start = route_points[i]
                    end = route_points[i + 1]
                    
                    # Orta nokta
                    mid_x = (start[0] + end[0]) / 2
                    mid_y = (start[1] + end[1]) / 2
                    
                    # Yön vektörü
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = np.sqrt(dx**2 + dy**2)
                    
                    if length > 0:
                        dx_norm = dx / length
                        dy_norm = dy / length
                        # Ok uzunluğu ve başlık ayarlanır
                        ax.arrow(mid_x, mid_y, dx_norm * 3, dy_norm * 3,
                               head_width=1.5, head_length=2, fc=color, ec=color)
                               
    def _add_legend(self, ax, has_routes: bool = False):
        """Harita üzerindeki renk ve işaretlerin ne anlama geldiğini gösteren legend oluşturur"""
        legend_elements = []
        
        # Drone konum simgesi (üçgen)
        legend_elements.append(plt.Line2D([0], [0], marker='^', color='w', 
                                        markerfacecolor='gray', markersize=10,
                                        label='Drone Konumu'))
        
         # Teslimat öncelik renkleri için legend öğeleri
        priority_colors = {1: 'lightblue', 2: 'yellow', 3: 'orange', 4: 'red', 5: 'darkred'}
        for priority in range(1, 6):
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                            markerfacecolor=priority_colors[priority],
                                            markersize=8, label=f'Öncelik {priority}'))
        
         # No-fly zone aktif/pasif renkleri
        legend_elements.append(patches.Patch(color='red', alpha=0.6, label='Aktif No-Fly Zone'))
        legend_elements.append(patches.Patch(color='lightcoral', alpha=0.3, label='Pasif No-Fly Zone'))
        # Rota çizimi varsa legend'e ekle
        if has_routes:
            legend_elements.append(plt.Line2D([0], [0], color='gray', linewidth=2,
                                            label='Drone Rotası'))
        
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
        
    def plot_performance_comparison(self, results: Dict, save_path: str = None):
        """Algoritma performans karşılaştırması"""
        algorithms = list(results.keys())
        metrics = ['delivery_rate', 'energy_efficiency', 'execution_time']
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5)) # 3 farklı metrik için subplot
        
        for i, metric in enumerate(metrics):
            values = [results[alg].get(metric, 0) for alg in algorithms] # Her algoritmanın metriği
            
            bars = axes[i].bar(algorithms, values, color=['skyblue', 'lightgreen', 'lightcoral'])
            axes[i].set_title(f'{metric.replace("_", " ").title()}') # Grafik başlığı
            axes[i].set_ylabel('Değer')
            
            # Değerleri çubukların üstüne yaz
            for bar, value in zip(bars, values):
                height = bar.get_height()
                axes[i].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{value:.2f}', ha='center', va='bottom')
                           
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show(block=True)
        plt.pause(2)
            
    def plot_fitness_evolution(self, fitness_history: List[float], save_path: str = None):
        """Genetik algoritmanın fitness değerlerinin nesiller boyunca değişimini grafikle gösterir"""
        plt.figure(figsize=(10, 6))
        
        generations = range(1, len(fitness_history) + 1) # Nesil sayıları
        plt.plot(generations, fitness_history, 'b-', linewidth=2, markersize=4) # Fitness çizgisi
        plt.fill_between(generations, fitness_history, alpha=0.3) # Altını renklendir
        
        plt.title('Genetic Algorithm Fitness Evrimi', fontsize=14, fontweight='bold')
        plt.xlabel('Nesil')
        plt.ylabel('Fitness Skoru')
        plt.grid(True, alpha=0.3)
        
        # En iyi fitness değerini kırmızı ile işaretle
        best_gen = fitness_history.index(max(fitness_history)) + 1
        best_fitness = max(fitness_history)
        plt.plot(best_gen, best_fitness, 'ro', markersize=8)
        plt.annotate(f'En İyi: {best_fitness:.1f}\nNesil: {best_gen}',
                    xy=(best_gen, best_fitness), xytext=(10, 10),
                    textcoords='offset points', ha='left',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show(block=True)
        plt.pause(2)
            
    def plot_drone_utilization(self, solution: Dict, drones: List[Drone], save_path: str = None):
        """Dronların kapasite kullanım oranları ve teslimat sayısını çubuk grafiklerle analiz eder"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6)) # İki yanyana grafik
         
        # Kapasite kullanımı
        drone_ids = [] 
        capacity_usage = []
        delivery_counts = []
        
        for drone in drones:
            drone_ids.append(f"D{drone.id}") # Drone ID label
            
            if hasattr(solution, 'chromosome'):  # Genetik algoritma çözümü
                assigned_deliveries = solution.chromosome.get(drone.id, [])
            else:  # CSP çözümü gibi diğer yapılar
                assigned_deliveries = solution.get(drone.id, set())
                
            total_weight = 0
            if assigned_deliveries:
                # Ortalama paket ağırlığı tahmini (örnek: 2 kg)
                total_weight = len(assigned_deliveries) * 2  # Ortalama tahmin
                
            capacity_usage.append((total_weight / drone.max_weight) * 100)  # Yüzde kapasite kullanımı
            delivery_counts.append(len(assigned_deliveries) if assigned_deliveries else 0)  # Yüzde kapasite kullanımı
            
         # Kapasite kullanım grafiği
        bars1 = ax1.bar(drone_ids, capacity_usage, color='lightblue', edgecolor='navy')
        ax1.set_title('Drone Kapasite Kullanımı')
        ax1.set_ylabel('Kapasite Kullanım Oranı (%)')
        ax1.set_ylim(0, 100) # Yüzde 0-100 aralığında
        ax1.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='Maksimum Kapasite')   # Maks kapasite çizgisi
        
        # Her barın üstüne yüzde değeri yaz
        for bar, value in zip(bars1, capacity_usage):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom')
                    
        # Teslimat sayısı grafiği
        bars2 = ax2.bar(drone_ids, delivery_counts, color='lightgreen', edgecolor='darkgreen')
        ax2.set_title('Drone Başına Teslimat Sayısı')
        ax2.set_ylabel('Teslimat Sayısı')
         # Barların üstüne teslimat sayısını yaz
        for bar, value in zip(bars2, delivery_counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show(block=True)
        plt.pause(2)
