"""
Drone Filo Optimizasyonu - Ana Program
Çok Kısıtlı Ortamlarda Dinamik Teslimat Planlaması

Bu program A*, CSP ve Genetic Algorithm yaklaşımlarını kullanarak
drone teslimat rotalarını optimize eder.
"""
# Gerekli sistem ve kütüphaneleri import et
import sys # Programı sonlandırmak gibi sistem işlevleri için
import os # Dosya/dizin işlemleri için
import argparse # Komut satırından parametre almak için
import time  # Zaman ölçmek için (süre, zaman damgası)
from typing import Dict, Any  # Tip ipuçları (sözlükler vb.)

# Proje içi modül import'ları – src klasöründeki bileşenler
from src.data_loader import DataLoader # Veri okuma / yazma
from src.graph_builder import DeliveryGraph # Noktalar arası mesafe grafı
from src.astar import AStarPathfinder  # A* algoritması
from src.csp_solver import CSPSolver  # CSP çözücü
from src.genetic_algorithm import GeneticAlgorithm  # Genetik algoritma
from src.multi_trip_planner import MultiTripPlanner  # Çok turlu planlayıcı
from src.detailed_reporter import DetailedReporter # Ayrıntılı rapor üretici
from src.visualizer import Visualizer # Grafik & harita çizimi
from src.data_generator import DataGenerator # Rastgele senaryo üretici

# Yardımcı: Başlık çıktısı
def print_header():
    """Program başlığını yazdır"""
    print("🚁" + "=" * 70 + "🚁")
    print("   DRONE FİLO OPTİMİZASYONU: DİNAMİK TESLİMAT PLANLAMASI")
    print("   Kocaeli Üniversitesi - TBL331 Yazılım Geliştirme Lab II")
    print("🚁" + "=" * 70 + "🚁")
    print()

# A* ile optimizasyon
def run_astar_optimization(graph, drones, deliveries, visualize=True):
    """A* algoritması ile optimizasyon"""
    print("🎯 A* Algoritması çalıştırılıyor...")
    start_time = time.time() # Başlangıç zamanı
    
    astar = AStarPathfinder(graph)  # A* nesnesi oluşturuluyor
    routes = {} # Drone'lara ait rotalar burada tutulacak
    total_deliveries = 0 # Yapılan toplam teslimat sayısı
    total_cost = 0 # Rotaların toplam maliyeti
    
    # Teslimatları öncelik sırasına göre sırala
    sorted_deliveries = sorted(deliveries, key=lambda x: x.priority, reverse=True) # Önceliğe göre sırala
    available_deliveries = [str(d.id) for d in sorted_deliveries] # İşlenmemiş teslimatlar
    
    # Her drone için optimal rota bul
    for drone in drones: # Her bir drone için rota hesapla
        if available_deliveries:
            # Multi-delivery route bulma.
            route = astar.find_multi_delivery_route(drone, available_deliveries[:5]) # İlk 5 teslimat için rota bul
            
            if route and len(route) > 1: # Geçerli rota bulunduysa
                routes[drone.id] = route # Rota kaydedilir
                delivered = [r for r in route if r.startswith('delivery_')] # Teslim edilen noktalar
                total_deliveries += len(delivered) # Teslimat sayısı güncellenir
                total_cost += astar.calculate_route_cost(route) # Rota maliyeti toplanır
                
                # Kullanılan teslimatları listeden çıkar
                used_deliveries = [r.split('_')[1] for r in delivered] # Kullanılan teslimatlar
                available_deliveries = [d for d in available_deliveries if d not in used_deliveries] # Kalanlar
    
    execution_time = time.time() - start_time # Süreyi hesapla
    
    # Sonuçları yazdır
    print(f"✅ A* Tamamlandı!")
    print(f"   - Teslimat sayısı: {total_deliveries}/{len(deliveries)}")
    print(f"   - Teslimat oranı: %{(total_deliveries/len(deliveries)*100):.1f}")
    print(f"   - Toplam maliyet: {total_cost:.2f}")
    print(f"   - Çalışma süresi: {execution_time:.3f} saniye")
    
    # Sonuç döndürülür
    return {
        'routes': routes,
        'delivery_count': total_deliveries,
        'delivery_rate': total_deliveries / len(deliveries),
        'total_cost': total_cost,
        'execution_time': execution_time
    }

# CSP ile optimizasyon
def run_csp_optimization(drones, deliveries, no_fly_zones, graph):
    """CSP çözücü ile optimizasyon"""
    print("🧩 CSP Çözücü çalıştırılıyor...") # Kullanıcıya bilgi ver
    start_time = time.time() # Başlangıç zamanı kaydedilir
    
    # Büyük problemler için veri setini küçült
    max_deliveries = min(30, len(deliveries)) # Maksimum 30 teslimatla sınırlama
    max_drones = min(8, len(drones)) # Maksimum 8 drone ile çözümleme yap
    
    csp_solver = CSPSolver(drones[:max_drones], deliveries[:max_deliveries], 
                          no_fly_zones, graph)
    
    # Forward checking ile CSP çözümü başlatılır
    solution = csp_solver.solve_with_forward_checking()
    execution_time = time.time() - start_time # Çalışma süresi hesaplanır
    
    if solution: # Eğer geçerli bir çözüm bulunduysa
        quality = csp_solver.get_solution_quality(solution) # Çözüm kalitesi ölçülür

         # Kullanıcıya çıktı verilir
        print(f"✅ CSP Tamamlandı!")
        print(f"   - Teslimat sayısı: {quality['covered_deliveries']}/{max_deliveries}")
        print(f"   - Teslimat oranı: %{quality['coverage_rate']*100:.1f}")
        print(f"   - Drone kullanım oranı: %{quality['drone_utilization']*100:.1f}")
        print(f"   - Çalışma süresi: {execution_time:.3f} saniye")
        
        return { # Başarılı çözüm sonuçları döndürülür
            'solution': solution,
            'delivery_count': quality['covered_deliveries'],
            'delivery_rate': quality['coverage_rate'],
            'drone_utilization': quality['drone_utilization'],
            'execution_time': execution_time,
            'success': True
        }
    else:
        # Eğer geçerli çözüm yoksa
        print("❌ CSP çözümü bulunamadı!")
        return {
            'solution': None, # Çözüm mevcut değil
            'delivery_count': 0, # Teslimat yapılmadı
            'delivery_rate': 0, # Teslimat oranı 0
            'execution_time': execution_time,
            'success': False # Başarısız işaretle
        }
    
    # Genetik Algoritma ile optimizasyon
def run_genetic_algorithm(drones, deliveries, no_fly_zones, graph, generations=100):
    print("🧬 Genetic Algorithm çalıştırılıyor...") # Kullanıcıya bilgi ver
    start_time = time.time() # Algoritmanın çalışma süresini ölçmek için başlangıç zamanı alınır
    
    ga = GeneticAlgorithm(drones, deliveries, no_fly_zones, graph) # Genetik algoritma nesnesi oluşturulur
    
   # Teslimat sayısı fazlaysa popülasyon büyüklüğü artırılır ve mutasyon oranı yükseltilir
    if len(deliveries) > 30:
        ga.population_size = 50 # Daha büyük popülasyon
        ga.generations = generations # Kullanıcının belirttiği kadar jenerasyon
        ga.mutation_rate = 0.15 # Daha yüksek mutasyon oranı
    else:
        ga.population_size = 30 # Küçük veri seti için daha az birey
        ga.generations = max(50, generations) # En az 50 jenerasyon çalıştır
        ga.mutation_rate = 0.1 # Daha düşük mutasyon oranı
    
    best_individual = ga.evolve() # Evrim süreci # Genetik algoritma çalıştırılır ve en iyi birey (çözüm) elde edilir
    execution_time = time.time() - start_time # Süre hesaplanır
    
    # Toplam teslimat sayısı hesaplanır
    delivery_count = sum(len(dl) for dl in best_individual.chromosome.values())
    # En iyi bireyin rotaları çıkarılır
    routes = ga.get_solution_routes(best_individual)
     # Sonuçlar ekrana yazdırılır
    print(f"✅ GA Tamamlandı!")
    print(f"   - Teslimat sayısı: {delivery_count}/{len(deliveries)}")
    print(f"   - Teslimat oranı: %{(delivery_count/len(deliveries)*100):.1f}")
    print(f"   - Fitness skoru: {best_individual.fitness:.2f}")
    print(f"   - Çalışma süresi: {execution_time:.3f} saniye")
    # Sonuç döndürülür
    return {
        'individual': best_individual, # En iyi çözüm
        'routes': routes, # Drone bazlı rotalar
        'delivery_count': delivery_count, # Kaç teslimat yapıldı
        'delivery_rate': delivery_count / len(deliveries),  # Teslimat yüzdesi
        'fitness_score': best_individual.fitness, # Fitness değeri (başarı puanı)
        'fitness_history': ga.fitness_history, # Her jenerasyondaki fitness değerleri
        'execution_time': execution_time # Algoritmanın çalışma süresi
    }

 #Multi-Trip sistemi ile optimizasyon
def run_multi_trip_optimization(drones, deliveries, no_fly_zones, graph):
    print("🔄 Multi-Trip Planner çalıştırılıyor...") # Kullanıcıya bilgi ver
    
    planner = MultiTripPlanner(drones, deliveries, no_fly_zones, graph)  # MultiTripPlanner nesnesi oluşturulur
    results = planner.plan_multi_trip_delivery() # Çok turlu teslimat planlaması yapılır
    
    # Detaylı raporu yazdır
    planner.print_detailed_report()
    
    return results # Sonuçlar geri döndürülür

def compare_algorithms(results):
    """Algoritmaları karşılaştır ve en iyisini bul"""
    print("\n📊 Algoritma Karşılaştırması:")
    print("-" * 50) # Konsolda görsel ayraç çiz
    
    comparison = {} # Algoritma adına karşı metrikleri tutacak sözlük
     
    for alg_name, result in results.items(): # CSP sonucunda 'success' anahtarı olabilir; başarısız sonuçlar dahil edilmez
        if result.get('success', True):  # CSP için success kontrolü
            delivery_rate = result['delivery_rate']  # Teslimat yüzdesi (0‒1 arası)
            exec_time = result['execution_time'] # Çalışma süresi (saniye)
            efficiency = result['delivery_count'] / exec_time if exec_time > 0 else 0 # Saniyede tamamlanan teslimat
            # Karşılaştırma verilerini sakla
            comparison[alg_name] = {
                'delivery_rate': delivery_rate,
                'execution_time': exec_time,
                'efficiency': efficiency
            }
            # Tablo benzeri satır yazdır
            print(f"{alg_name:12} | Teslimat: %{delivery_rate*100:5.1f} | "
                  f"Süre: {exec_time:6.3f}s | Verimlilik: {efficiency:5.2f}")
    
    if comparison:
        # En iyi algoritmaları bul
        best_delivery = max(comparison.keys(), key=lambda x: comparison[x]['delivery_rate'])  #Teslimat oranına göre en yüksek
        fastest = min(comparison.keys(), key=lambda x: comparison[x]['execution_time'])  #Çalışma süresine göre en hızlı
        most_efficient = max(comparison.keys(), key=lambda x: comparison[x]['efficiency']) #Saniye başı teslimata göre en verimli
        
        print(f"\n🏆 En İyi Performanslar:")
        print(f"   - En yüksek teslimat oranı: {best_delivery}")
        print(f"   - En hızlı: {fastest}")
        print(f"   - En verimli: {most_efficient}")
        
        return best_delivery # Görece en başarılı algoritma ismi döndürülür
    
    return None # Karşılaştırılacak veri yoksa

def visualize_results(drones, deliveries, no_fly_zones, results, output_dir="results"):
    """Sonuçları görselleştir"""
    print("\n📈 Görselleştirme oluşturuluyor...")
    print("💡 Her grafik ekranda gösterilecek - kapatmak için pencereyi kapatın!")
    
    os.makedirs(output_dir, exist_ok=True) # Çıktı klasörü yoksa oluştur
    visualizer = Visualizer() # Görselleştirme sınıfı
    
    # Her algoritma için rota haritası
    for alg_name, result in results.items():
        if 'routes' in result and result['routes']: # Rota verisi varsa
            save_path = f"{output_dir}/{alg_name.lower().replace('*', 'star')}_routes.png" # Kaydedilecek dosya adı
            print(f"\n🗺️  {alg_name} rota haritası gösteriliyor...")
            visualizer.plot_scenario(drones, deliveries, no_fly_zones,  # Haritayı çiz
                                   result['routes'], save_path=save_path)
            print(f"   ✅ Kaydedildi: {save_path}")
    
    # GA fitness eğrisi
    if 'GA' in results and 'fitness_history' in results['GA']:
        fitness_path = f"{output_dir}/ga_fitness_evolution.png"
        print(f"\n📊 GA fitness evrimi gösteriliyor...")
        visualizer.plot_fitness_evolution(results['GA']['fitness_history'], 
                                         save_path=fitness_path)
        print(f"   ✅ Kaydedildi: {fitness_path}")
    
    # Genel performans karşılaştırma grafiği
    comparison_data = {}
    for alg_name, result in results.items():
        if result.get('success', True): # Başarısız CSP dâhil edilmez
            comparison_data[alg_name] = {
                'delivery_rate': result['delivery_rate'] * 100,  # % cinsinden
                'energy_efficiency': result['delivery_count'] / (result['execution_time'] + 1) * 10,
                'execution_time': result['execution_time']
            }
    
    if comparison_data:
        comparison_path = f"{output_dir}/performance_comparison.png"
        print(f"\n📈 Performans karşılaştırması gösteriliyor...")
        visualizer.plot_performance_comparison(comparison_data, save_path=comparison_path)
        print(f"   ✅ Kaydedildi: {comparison_path}")

def create_report(results, drones, deliveries, no_fly_zones, output_dir="results"):
    """Detaylı rapor oluştur"""
    report_path = f"{output_dir}/optimization_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("DRONE FİLO OPTİMİZASYONU RAPORU\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("Problem Tanımı:\n")
        f.write(f"- Drone sayısı: {len(drones)}\n")
        f.write(f"- Teslimat noktası sayısı: {len(deliveries)}\n")
        f.write(f"- No-fly zone sayısı: {len(no_fly_zones)}\n\n")
        
        # Drone detayları
        f.write("Drone Detayları:\n")
        total_capacity = 0
        for drone in drones:
            f.write(f"  Drone {drone.id}: {drone.max_weight}kg, {drone.battery}mAh, {drone.speed}m/s\n")
            total_capacity += drone.max_weight
        f.write(f"Toplam kapasite: {total_capacity:.1f}kg\n\n")
        
        # Teslimat detayları
        total_weight = sum(d.weight for d in deliveries)
        priority_dist = {}
        for d in deliveries:
            priority_dist[d.priority] = priority_dist.get(d.priority, 0) + 1
            
        f.write("Teslimat Detayları:\n")
        f.write(f"  Toplam ağırlık: {total_weight:.1f}kg\n")
        f.write(f"  Öncelik dağılımı: {priority_dist}\n\n")
        
        # Algoritma sonuçları
        f.write("Algoritma Sonuçları:\n")
        f.write("-" * 40 + "\n")
        
        for alg_name, result in results.items():
            f.write(f"\n{alg_name}:\n")
            if result.get('success', True): # Başarılıysa ayrıntı yaz
                f.write(f"  - Teslimat sayısı: {result['delivery_count']}/{len(deliveries)}\n")
                f.write(f"  - Teslimat oranı: %{result['delivery_rate']*100:.1f}\n")
                f.write(f"  - Çalışma süresi: {result['execution_time']:.3f} saniye\n")
                
                if 'total_cost' in result:
                    f.write(f"  - Toplam maliyet: {result['total_cost']:.2f}\n")
                if 'fitness_score' in result:
                    f.write(f"  - Fitness skoru: {result['fitness_score']:.2f}\n")
            else: # Başarısız algoritma
                f.write("  - Çözüm bulunamadı\n")
        
        # Öneriler
        f.write(f"\nÖneriler ve Değerlendirme:\n")
        best_rate = max([r['delivery_rate'] for r in results.values() if r.get('success', True)], default=0)
        
        if best_rate > 0.8:
            f.write("✅ Yüksek teslimat oranı elde edildi\n")
        elif best_rate > 0.6:
            f.write("⚠️ Orta düzey teslimat oranı - iyileştirme mümkün\n")
        else:
            f.write("❌ Düşük teslimat oranı - sistem optimizasyonu gerekli\n")
            
        capacity_util = (total_weight / total_capacity) * 100 if total_capacity > 0 else 0
        if capacity_util > 90:
            f.write("⚠️ Kapasite sınırında - ek drone gerekebilir\n")
        
    print(f"📝 Detaylı rapor oluşturuldu: {report_path}")

def main():
    """Ana program fonksiyonu"""
    parser = argparse.ArgumentParser(description="Drone Filo Optimizasyonu")
    parser.add_argument("--data", default="data/sample_data.txt", 
                       help="Veri dosyası yolu")
    parser.add_argument("--algorithm", choices=['astar', 'csp', 'ga', 'multitrip', 'all'], 
                       default='all', help="Çalıştırılacak algoritma")
    parser.add_argument("--generations", type=int, default=100, 
                       help="GA için nesil sayısı")
    parser.add_argument("--output", default="results", 
                       help="Çıktı dizini")
    parser.add_argument("--visualize", action="store_true", 
                       help="Görselleştirme oluştur")
    parser.add_argument("--generate", action="store_true", 
                       help="Rastgele veri oluştur")
    
    args = parser.parse_args() # Komut satırı argümanlarını ayrıştır
    
    print_header()  # Kullanıcıya başlık göster
    
    # Çıktı dizinini oluştur
    os.makedirs(args.output, exist_ok=True)
    
    # Veri yükleme
    if args.generate:
        print("📊 Rastgele veri oluşturuluyor...")
        generator = DataGenerator()
        scenario = generator.create_balanced_scenario(5, 20, 3)  # Dengeli senaryo oluştur
        
        loader = DataLoader()
        drones, deliveries, no_fly_zones = loader.load_python_data(
            scenario["drones"], scenario["deliveries"], scenario["no_fly_zones"]
        )
        
        # Üretilen veriyi .txt olarak kaydet
        loader.save_to_txt(drones, deliveries, no_fly_zones, "data/generated_data.txt")
        print("   ✅ Veri oluşturuldu ve kaydedildi: data/generated_data.txt")
    else:
        print(f"📂 Veri yükleniyor: {args.data}")
        loader = DataLoader()
        
        if args.data.endswith('.txt'):
            drones, deliveries, no_fly_zones = loader.load_from_txt(args.data)
        else:
            print("❌ Desteklenmeyen dosya formatı!")
            sys.exit(1)
    
    # # Konsolda özet göster
    loader.print_data_summary(drones, deliveries, no_fly_zones)
    
    # Graf oluşturma
    print("\n🕸️ Graf oluşturuluyor...")
    graph = DeliveryGraph(drones, deliveries, no_fly_zones)
    graph.print_graph_stats() # Graf istatistikleri
    
    # Algoritmaları çalıştır
    results = {}
    
    if args.algorithm in ['astar', 'all']:
        results['A*'] = run_astar_optimization(graph, drones, deliveries)
        
    if args.algorithm in ['csp', 'all']:
        results['CSP'] = run_csp_optimization(drones, deliveries, no_fly_zones, graph)
        
    if args.algorithm in ['ga', 'all']:
        results['GA'] = run_genetic_algorithm(drones, deliveries, no_fly_zones, 
                                            graph, args.generations)
    
    if args.algorithm in ['multitrip', 'all']:
        results['Multi-Trip'] = run_multi_trip_optimization(drones, deliveries, no_fly_zones, graph)
    
    # Karşılaştırma (birden çok algoritma varsa)
    if len(results) > 1:
        best_algorithm = compare_algorithms(results) # En iyiyi bul (opsiyonel)
    
    # Görselleştirme
    if args.visualize and results:
        print("\n" + "="*60)
        print("🎨 GÖRSELLEŞTIRME BAŞLIYOR")
        print("💡 İpucu: Her grafik ayrı pencerede açılacak.")
        print("   Grafikleri inceledikten sonra pencereleri kapatın.")
        print("="*60)
        
        input("📌 Görselleştirme için ENTER'a basın...")
        visualize_results(drones, deliveries, no_fly_zones, results, args.output)
        
        print("\n✅ Tüm grafikler gösterildi ve kaydedildi!")
    
    # Rapor oluştur
    create_report(results, drones, deliveries, no_fly_zones, args.output)
    
    # Detaylı kapsamlı rapor oluştur
    detailed_reporter = DetailedReporter(args.output)
    detailed_reporter.create_comprehensive_report(results, drones, deliveries, no_fly_zones)
    
    print(f"\n🎉 Optimizasyon tamamlandı!")
    print(f"📁 Sonuçlar '{args.output}' dizininde kaydedildi.")
    
    if args.visualize:
        print("🖼️  Grafik dosyalarını görmek için:")
        print(f"   - {args.output}/ klasörünü açın")
        print("   - .png dosyalarını çift tıklayın")

if __name__ == "__main__": # Script doğrudan çalıştırıldığında main() tetiklenir
    main()
