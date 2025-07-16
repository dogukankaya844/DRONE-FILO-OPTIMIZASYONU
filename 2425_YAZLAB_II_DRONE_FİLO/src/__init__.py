"""
Drone Filo Optimizasyonu Paketi
Çok Kısıtlı Ortamlarda Dinamik Teslimat Planlaması

Bu paket projenin modüler yapısını tek bir giriş noktasıyla (paket olarak) bütünleştirir, kullanıcıların projedeki ana sınıflara ve fonksiyonlara kolayca erişmesini sağlar.
"""

__version__ = "1.0.0"
__author__ = "Dogukan Kaya"
__email__ = "191307009@kocaeli.edu.tr"

# Ana sınıfları import et 
from .drone import Drone # Drone sınıfı
from .delivery_point import DeliveryPoint # Teslimat noktası sınıfı
from .no_fly_zone import NoFlyZone # Uçuşa yasak alan sınıfı
from .graph_builder import DeliveryGraph   # Teslimat grafı oluşturucu
from .astar import AStarPathfinder  # A* algoritması sınıfı
from .csp_solver import CSPSolver # CSP problemi çözücü sınıf
from .genetic_algorithm import GeneticAlgorithm # Genetik algoritma sınıfı
from .data_loader import DataLoader  # Veri yükleme sınıfı
from .data_generator import DataGenerator # Rastgele veri üretici
from .visualizer import Visualizer # Görselleştirme sınıfı

__all__ = [
    'Drone', # Drone sınıfı
    'DeliveryPoint',  # Teslimat noktası
    'NoFlyZone',  # Uçuşa yasak alanlar
    'DeliveryGraph', # Graf yapısı
    'AStarPathfinder',  # A* algoritması
    'CSPSolver', # CSP çözücü
    'GeneticAlgorithm',  # Genetik algoritma
    'DataLoader',  # Veri yükleyici
    'DataGenerator', # Veri oluşturucu
    'Visualizer'  # Grafik çizici
]
