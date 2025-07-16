"""
Test Senaryo 1: 5 drone, 20 teslimat, 2 no-fly zone
PDF'de belirtilen ilk test senaryosu

Bu dosya, drone teslimat sistemi için oluşturulmuş bir test senaryosunu çalıştırır ve farklı algoritmaların (A*, CSP, Genetik Algoritma) performansını karşılaştırır.
"""
import sys
import os
import time

# Proje dizinini python path'ine ekle (modüllerin bulunması için)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
# Projedeki farklı modülleri import et
from src.data_loader import DataLoader  # Veri yükleme sınıfı
from src.graph_builder import DeliveryGraph # Teslimat grafiği oluşturma
from src.astar import AStarPathfinder # A* algoritması için sınıf
from src.csp_solver import CSPSolver # CSP algoritması için sınıf
from src.genetic_algorithm import GeneticAlgorithm # Genetik algoritma sınıfı
from src.visualizer import Visualizer # Sonuçları görselleştirme
from src.data_generator import DataGenerator # Test senaryosu için veri üretici

def test_scenario_1():
    """Senaryo 1 testini çalıştır"""
    print("🚁 Test Senaryo 1: 5 drone, 20 teslimat, 2 no-fly zone")
    print("=" * 60)
    
   # Senaryo için harita boyutunda veri üretir (dronelar, teslimatlar, no-fly zone'lar)
    generator = DataGenerator(map_size=(100, 100))
    scenario = generator.generate_scenario(5, 20, 2, "Test_Scenario_1")
    
     # Üretilen JSON benzeri veriyi nesnelere dönüştürür
    loader = DataLoader()
    drones, deliveries, no_fly_zones = loader.load_python_data(
        scenario["drones"], scenario["deliveries"], scenario["no_fly_zones"]
    )
    
    # Veri özetini yazdır
    loader.print_data_summary(drones, deliveries, no_fly_zones)
    
   # Teslimat noktaları ve drone konumlarını içeren graf yapısını oluşturur
    print("\n📊 Graf oluşturuluyor...")
    graph = DeliveryGraph(drones, deliveries, no_fly_zones)
    graph.print_graph_stats() # Graf ile ilgili özet bilgileri gösterir
    
    results = {} # Algoritma sonuçlarının saklanacağı sözlük
    
    # 1. A* Algoritması Testi
    print("\n🎯 A* Algoritması çalıştırılıyor...")
    start_time = time.time()
    
    astar = AStarPathfinder(graph)
    astar_routes = {}
    total_deliveries_astar = 0
    total_cost_astar = 0
    
     # Drone başına maksimum 3 teslimat olacak şekilde A* rotası hesaplanır
    available_deliveries = [str(d.id) for d in deliveries]
    
    for drone in drones:
        if available_deliveries:
            # En iyi rota ve maliyet bulunur
            route, cost = astar.find_optimal_delivery_route(drone, available_deliveries[:3])  # İlk 3 teslimat
            if route:
                astar_routes[drone.id] = route
                 # Rota içindeki teslimat sayısı toplanır
                total_deliveries_astar += len([r for r in route if r.startswith('delivery_')])
                total_cost_astar += cost
                # Kullanılan teslimatlar listeden çıkarılır
                used_deliveries = [r.split('_')[1] for r in route if r.startswith('delivery_')]
                available_deliveries = [d for d in available_deliveries if d not in used_deliveries]
    
    astar_time = time.time() - start_time # A* algoritması çalışma süresi
    
    results['A*'] = { # A* sonuçları dictionary'ye kaydedilir
        'delivery_count': total_deliveries_astar,
        'delivery_rate': total_deliveries_astar / len(deliveries),
        'total_cost': total_cost_astar,
        'execution_time': astar_time,
        'routes': astar_routes
    }
    # A* algoritması sonuçları konsola yazdırılır
    print(f"A* Sonuçları:")
    print(f"  - Tamamlanan teslimat: {total_deliveries_astar}/{len(deliveries)}")
    print(f"  - Teslimat oranı: %{(total_deliveries_astar/len(deliveries)*100):.1f}")
    print(f"  - Toplam maliyet: {total_cost_astar:.2f}")
    print(f"  - Çalışma süresi: {astar_time:.3f} saniye")
    
    # 2. CSP Çözümü Testi  CSP algoritması testi başlatılır, çalışma süresi ölçülür
    print("\n🧩 CSP Çözücü çalıştırılıyor...")
    start_time = time.time()
    
    csp_solver = CSPSolver(drones, deliveries, no_fly_zones, graph)
    csp_solution = csp_solver.solve_with_forward_checking() # Çözümü bulmaya çalış
    
    csp_time = time.time() - start_time
    
    if csp_solution:
        # Çözüm kalitesi hesaplanır ve yazdırılır
        csp_quality = csp_solver.get_solution_quality(csp_solution)
        csp_solver.print_solution(csp_solution)
        # CSP sonuçları kaydedilir
        results['CSP'] = {
            'delivery_count': csp_quality['covered_deliveries'],
            'delivery_rate': csp_quality['coverage_rate'],
            'execution_time': csp_time,
            'drone_utilization': csp_quality['drone_utilization'],
            'solution': csp_solution
        }
    else:
        print("CSP çözümü bulunamadı!")
        # Çözüm yoksa sıfır değerler kaydedilir
        results['CSP'] = {
            'delivery_count': 0,
            'delivery_rate': 0,
            'execution_time': csp_time,
            'drone_utilization': 0
        }
    
    print(f"CSP Çalışma süresi: {csp_time:.3f} saniye")
    
    # 3. Genetic Algorithm Testi
    print("\n🧬 Genetic Algorithm çalıştırılıyor...")
    start_time = time.time()
    
    ga = GeneticAlgorithm(drones, deliveries, no_fly_zones, graph)
    ga.population_size = 30  # Daha hızlı test için küçük popülasyon
    ga.generations = 50 # Nesil sayısı
    
    best_individual = ga.evolve() # Evrimsel süreci çalıştır
    
    ga_time = time.time() - start_time
     # En iyi çözümden rota ve teslimat sayısı alınır
    ga_routes = ga.get_solution_routes(best_individual)
    ga_delivery_count = sum(len(delivery_list) for delivery_list in best_individual.chromosome.values())
    # GA sonuçları kaydedilir
    results['GA'] = {
        'delivery_count': ga_delivery_count,
        'delivery_rate': ga_delivery_count / len(deliveries),
        'fitness_score': best_individual.fitness,
        'execution_time': ga_time,
        'routes': ga_routes,
        'fitness_history': ga.fitness_history
    }
    
    ga.print_solution(best_individual) # Çözüm detaylarını yazdır
    print(f"GA Çalışma süresi: {ga_time:.3f} saniye")
    
    # 4. Görselleştirme
    print("\n📈 Sonuçlar görselleştiriliyor...")
    visualizer = Visualizer(map_size=(100, 100))
    
    print("\n📌 Görselleştirme için ENTER'a basın (veya Ctrl+C ile atlayın)...")
    try:
        input()
        
        # A* rotalarını görselleştir
        if astar_routes:
            print("🗺️ A* rota haritası gösteriliyor...")
            visualizer.plot_scenario(drones, deliveries, no_fly_zones, astar_routes,
                                    save_path="results/scenario1_astar_routes.png")
        
        # GA rotalarını görselleştir
        if ga_routes:
            print("🗺️ GA rota haritası gösteriliyor...")
            visualizer.plot_scenario(drones, deliveries, no_fly_zones, ga_routes,
                                    save_path="results/scenario1_ga_routes.png")
        
        # GA fitness evrimini görselleştir
        if 'fitness_history' in results['GA']:
            print("📊 GA fitness evrimi gösteriliyor...")
            visualizer.plot_fitness_evolution(results['GA']['fitness_history'],
                                             save_path="results/scenario1_fitness_evolution.png")
        
       # Algoritmaların performans karşılaştırmasını yap ve göster
        comparison_data = {}
        for alg_name, alg_results in results.items():
            comparison_data[alg_name] = {
                'delivery_rate': alg_results['delivery_rate'] * 100,
                'energy_efficiency': 100 / (alg_results.get('total_cost', alg_results.get('fitness_score', 1)) / 1000 + 1),
                'execution_time': alg_results['execution_time']
            }
        
        print("📈 Performans karşılaştırması gösteriliyor...")
        visualizer.plot_performance_comparison(comparison_data,
                                             save_path="results/scenario1_performance_comparison.png")
        
        print("✅ Tüm grafikler gösterildi ve kaydedildi!")
        
    except KeyboardInterrupt:
        print("\n⏭️ Görselleştirme atlandı.")
    
    # 5. Test sonuçlarını rapor olarak dosyaya yazar
    print("\n📝 Test raporu oluşturuluyor...")
    create_test_report(results, "results/scenario1_report.txt")
    
    print("\n✅ Test Senaryo 1 tamamlandı!")
    print("Sonuçlar 'results/' klasöründe kaydedildi.")
    
    return results

def create_test_report(results, filename):
    """Algoritma sonuçlarını rapor dosyasına yazar"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("TEST SENARYO 1 RAPORU\n")
        f.write("=" * 50 + "\n\n")
        f.write("Test Parametreleri:\n")
        f.write("- Drone sayısı: 5\n")
        f.write("- Teslimat sayısı: 20\n")
        f.write("- No-fly zone sayısı: 2\n\n")
        
        f.write("Algoritma Karşılaştırması:\n")
        f.write("-" * 30 + "\n")
        
        for alg_name, alg_results in results.items():
            f.write(f"\n{alg_name} Algoritması:\n")
            f.write(f"  - Tamamlanan teslimat: {alg_results['delivery_count']}\n")
            f.write(f"  - Teslimat oranı: %{alg_results['delivery_rate']*100:.1f}\n")
            f.write(f"  - Çalışma süresi: {alg_results['execution_time']:.3f} saniye\n")
            
            if 'fitness_score' in alg_results:
                f.write(f"  - Fitness skoru: {alg_results['fitness_score']:.2f}\n")
            if 'total_cost' in alg_results:
                f.write(f"  - Toplam maliyet: {alg_results['total_cost']:.2f}\n")
            if 'drone_utilization' in alg_results:
                f.write(f"  - Drone kullanım oranı: %{alg_results['drone_utilization']*100:.1f}\n")
        
        # En başarılı algoritmayı raporda belirt
        best_alg = max(results.keys(), key=lambda x: results[x]['delivery_rate'])
        f.write(f"\nEn İyi Performans: {best_alg}\n")
        f.write(f"  - En yüksek teslimat oranı: %{results[best_alg]['delivery_rate']*100:.1f}\n")
        
         # Algoritmaların teorik zaman karmaşıklığı hakkında bilgi verir
        f.write(f"\nZaman Karmaşıklığı Analizi:\n")
        f.write("- A*: O(b^d) - b: branching factor, d: depth\n")
        f.write("- CSP: O(d^n) - d: domain size, n: variables\n")
        f.write("- GA: O(g*p*f) - g: generations, p: population, f: fitness evaluation\n")

if __name__ == "__main__":
    # Results dizinini oluştur
    os.makedirs("results", exist_ok=True)
    
    # Test senaryosunu çalıştır
    test_scenario_1()
