#!/usr/bin/env python3
"""
Hızlı Test Scripti - Projeyi test etmek için
Bu script basit bir test yapar ve görselleştirme seçeneği sunar

Bu dosya, örnek bir veri seti üzerinde genetik algoritmayı hızlı şekilde test eden ve istenirse sonuçları görselleştiren bir betiktir. Tam test senaryolarına girmeden, sistemin genel çalışmasını ve optimizasyonun işlevini hızlıca görmek için kullanılır.
"""

import sys
import os

# Proje dizinini path'e ekle
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root) # Ana dizini Python path'e ekle
# Gerekli modülleri içe aktar
from src.data_loader import DataLoader # Ana dizini Python path'e ekle
from src.graph_builder import DeliveryGraph # Teslimat grafiğini oluşturan sınıf
from src.genetic_algorithm import GeneticAlgorithm # Genetik algoritma çözümleyicisi
from src.visualizer import Visualizer  # Grafik çizimi ve görselleştirme

def quick_test():
    """Hızlı test fonksiyonu"""
    print("🚁" + "=" * 50 + "🚁")
    print("   HIZLI TEST - DRONE FILO OPTIMIZASYONU")
    print("🚁" + "=" * 50 + "🚁")
    
    try:
        # 1. Veri yükleme
        print("\n📂 Örnek veri yükleniyor...")
        loader = DataLoader() # Veri yükleyici nesnesi oluştur
        drones, deliveries, no_fly_zones = loader.load_from_txt("data/sample_data.txt") # Veriyi dosyadan al
        
        print(f"✅ {len(drones)} drone, {len(deliveries)} teslimat, {len(no_fly_zones)} no-fly zone yüklendi")
        
        # 2. Graf oluşturma
        print("\n🕸️ Graf oluşturuluyor...")
        graph = DeliveryGraph(drones, deliveries, no_fly_zones) # Harita ve engellerle grafik yapısı kur
        print("✅ Graf oluşturuldu")
        
        # 3. Genetic Algorithm ile hızlı optimizasyon
        print("\n🧬 Genetic Algorithm (hızlı mod) çalıştırılıyor...")
        ga = GeneticAlgorithm(drones, deliveries, no_fly_zones, graph) # GA nesnesi
        
        # Hızlı test için küçük parametreler kullan
        ga.population_size = 20 # Popülasyon büyüklüğü
        ga.generations = 30 # Jenerasyon sayısı
        
        best_individual = ga.evolve() # Evrim süreci başlat
        
        # 4. Sonuçları göster
        delivery_count = sum(len(dl) for dl in best_individual.chromosome.values()) # Toplam teslimat sayısı
        print(f"\n🎉 Optimizasyon tamamlandı!")
        print(f"   - Teslimat sayısı: {delivery_count}/{len(deliveries)}")
        print(f"   - Teslimat oranı: %{(delivery_count/len(deliveries)*100):.1f}")
        print(f"   - Fitness skoru: {best_individual.fitness:.2f}")
        
        # 5. Görselleştirme seçeneği
        show_viz = input("\n🎨 Görselleştirme yapmak ister misiniz? (y/N): ").lower().strip() # Kullanıcıdan görselleştirme onayı al

        
        if show_viz in ['y', 'yes', 'e', 'evet']:
            print("\n📊 Görselleştirme oluşturuluyor...")
            print("💡 İpucu: Grafik penceresini kapatarak devam edin.")
            
            visualizer = Visualizer() # Görselleştirici oluştur
            routes = ga.get_solution_routes(best_individual) # Drone rotalarını al
            
            # Rota haritasını göster
            print("\n🗺️ Drone rota haritası gösteriliyor...")
            visualizer.plot_scenario(drones, deliveries, no_fly_zones, routes, 
                                    save_path="results/quick_test_routes.png") # Rota grafiğini kaydet
            
            # Fitness evrimini göster
            print("\n📈 GA fitness evrimi gösteriliyor...")
            visualizer.plot_fitness_evolution(ga.fitness_history,
                                             save_path="results/quick_test_fitness.png") # Fitness grafiğini kaydet
            
            print("✅ Grafikler gösterildi ve 'results/' klasörüne kaydedildi!")
        
        print(f"\n🎯 Hızlı test başarılı!")
        print("📁 Daha detaylı testler için:")
        print("   python main.py --visualize")
        print("   python tests/test_scenario1.py")
        
    except FileNotFoundError as e:
        print(f"❌ Dosya bulunamadı: {e}")
        print("💡 'data/sample_data.txt' dosyasının mevcut olduğundan emin olun.")# Dosya yoksa uyar
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        print("💡 'python check_setup.py' ile kurulumu kontrol edin.") # Genel hata yakalama

if __name__ == "__main__":
    # Results dizinini oluştur
    os.makedirs("results", exist_ok=True) # Sonuçların kaydedileceği klasörü oluştur
    
    # Hızlı testi çalıştır
    quick_test() # Test fonksiyonunu başlat
