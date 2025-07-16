"""
Test Senaryo 2: 10 drone, 50 teslimat, 5 dinamik no-fly zone
PDF'de belirtilen ikinci test senaryosu
Bu dosya, gerçekçi ve büyük bir teslimat senaryosu üzerinde algoritmaların verimliliğini ölçmek, kıyaslamak ve sonuçları hem görsel hem de yazılı olarak raporlamak için kullanılır.
"""
import sys
import os
import time

# Proje dizinini path'e ekle (modüllerin bulunabilmesi için)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
# Gerekli modülleri projeden içe aktar
from src.data_loader import DataLoader # Verileri yüklemek için
from src.graph_builder import DeliveryGraph # Teslimat grafını oluşturmak için
from src.astar import AStarPathfinder  # A* algoritması için
from src.csp_solver import CSPSolver # CSP çözümleyici
from src.genetic_algorithm import GeneticAlgorithm # Genetik algoritma çözümleyici
from src.visualizer import Visualizer # Görselleştirme işlemleri için
from src.data_generator import DataGenerator # Test verilerini üretmek için

def test_scenario_2():
    """Senaryo 2 testini çalıştır - Büyük ölçekli test"""
    print("🚁 Test Senaryo 2: 10 drone, 50 teslimat, 5 dinamik no-fly zone")
    print("=" * 70)
    
    # Dengeli senaryo oluştur (daha gerçekçi)
    generator = DataGenerator(map_size=(150, 150))  # Daha büyük harita
    scenario = generator.create_balanced_scenario(10, 50, 5)
    
    # Üretilen verileri uygun Python nesnelerine dönüştür
    loader = DataLoader()
    drones, deliveries, no_fly_zones = loader.load_python_data(
        scenario["drones"], scenario["deliveries"], scenario["no_fly_zones"]
    )
    
    # Senaryo özetini yazdır (kaç drone, teslimat, yasak bölge var)
    loader.print_data_summary(drones, deliveries, no_fly_zones)
    
    # Graf oluştur
    print("\n📊 Graf oluşturuluyor...")
    graph = DeliveryGraph(drones, deliveries, no_fly_zones)
    graph.print_graph_stats()
    
    results = {}
    
    # Performans hedefi: < 1 dakika (60 saniye)
    MAX_TIME_LIMIT = 60.0  # Performans hedefi: maksimum 60 saniyede tamamlansın
    
    # 1. A* Algoritması Testi (Greedy yaklaşım - büyük ölçek için)
    print("\n🎯 A* Algoritması (Greedy) çalıştırılıyor...")
    start_time = time.time()
    
    astar = AStarPathfinder(graph) # A* nesnesi oluşturuluyor
    astar_routes = {}
    total_deliveries_astar = 0
    total_cost_astar = 0
    
    # Öncelik sırasına göre teslimatları sırala
    sorted_deliveries = sorted(deliveries, key=lambda x: x.priority, reverse=True)
    available_deliveries = [str(d.id) for d in sorted_deliveries]
    # Her drone için uygun teslimat rotaları bulunur
    for drone in drones:
        if available_deliveries and (time.time() - start_time) < MAX_TIME_LIMIT:
            # Greedy: en yakın teslimatları al
            route = astar.find_multi_delivery_route(drone, available_deliveries[:5])
            if route and len(route) > 1:
                astar_routes[drone.id] = route
                delivered = [r for r in route if r.startswith('delivery_')]
                total_deliveries_astar += len(delivered)
                
                 # Tamamlanan teslimatlar listeden çıkarılır
                used_deliveries = [r.split('_')[1] for r in delivered]
                available_deliveries = [d for d in available_deliveries if d not in used_deliveries]
                
                # Rota maliyetini hesapla
                total_cost_astar += astar.calculate_route_cost(route)
    
    astar_time = time.time() - start_time
     # A* sonuçları kaydedilir
    results['A*'] = {
        'delivery_count': total_deliveries_astar,
        'delivery_rate': total_deliveries_astar / len(deliveries),
        'total_cost': total_cost_astar,
        'execution_time': astar_time,
        'routes': astar_routes,
        'time_limit_exceeded': astar_time > MAX_TIME_LIMIT
    }
    # A* Sonuçlarını ekrana yazdır
    print(f"A* Sonuçları:")
    print(f"  - Tamamlanan teslimat: {total_deliveries_astar}/{len(deliveries)}")
    print(f"  - Teslimat oranı: %{(total_deliveries_astar/len(deliveries)*100):.1f}")
    print(f"  - Toplam maliyet: {total_cost_astar:.2f}")
    print(f"  - Çalışma süresi: {astar_time:.3f} saniye")
    if astar_time > MAX_TIME_LIMIT:
        print("  ⚠️ Zaman limiti aşıldı!")
    
    # 2. CSP Çözümü Testi (Basitleştirilmiş)
    print("\n🧩 CSP Çözücü (Basit) çalıştırılıyor...")
    start_time = time.time()
    
    # Büyük veri seti için CSP küçültülmüş veri ile çalıştırılıyor
    csp_solver = CSPSolver(drones[:8], deliveries[:30], no_fly_zones, graph)  # Küçült
    csp_solution = csp_solver.backtrack_search()  # Basit backtracking
    
    csp_time = time.time() - start_time
    # CSP çözümü bulunduysa sonuçlar yazdırılır
    if csp_solution and csp_time < MAX_TIME_LIMIT:
        csp_quality = csp_solver.get_solution_quality(csp_solution)
        
        results['CSP'] = {
            'delivery_count': csp_quality['covered_deliveries'],
            'delivery_rate': csp_quality['covered_deliveries'] / len(deliveries[:30]),  # Küçültülmüş veri seti
            'execution_time': csp_time,
            'drone_utilization': csp_quality['drone_utilization'],
            'solution': csp_solution,
            'time_limit_exceeded': csp_time > MAX_TIME_LIMIT
        }
        
        print(f"CSP Sonuçları:")
        print(f"  - Tamamlanan teslimat: {csp_quality['covered_deliveries']}/30 (küçültülmüş set)")
        print(f"  - Drone kullanım oranı: %{csp_quality['drone_utilization']*100:.1f}")
    else:
        print("CSP çözümü bulunamadı veya zaman aşımı!")
        results['CSP'] = {
            'delivery_count': 0,
            'delivery_rate': 0,
            'execution_time': csp_time,
            'drone_utilization': 0,
            'time_limit_exceeded': csp_time > MAX_TIME_LIMIT
        }
    
    print(f"CSP Çalışma süresi: {csp_time:.3f} saniye")
    
    # 3. Genetic Algorithm Testi (Optimize edilmiş)
    print("\n🧬 Genetic Algorithm (Optimize) çalıştırılıyor...")
    start_time = time.time()
    
    ga = GeneticAlgorithm(drones, deliveries, no_fly_zones, graph)
    # Büyük ölçek için GA parametrelerini optimize et
    ga.population_size = 40
    ga.generations = 80
    ga.mutation_rate = 0.15
    ga.elite_size = 8
    
    best_individual = ga.evolve()
    
    ga_time = time.time() - start_time
    # En iyi bireyin çözümü alınır
    ga_routes = ga.get_solution_routes(best_individual)
    ga_delivery_count = sum(len(delivery_list) for delivery_list in best_individual.chromosome.values())
    
    results['GA'] = {
        'delivery_count': ga_delivery_count,
        'delivery_rate': ga_delivery_count / len(deliveries),
        'fitness_score': best_individual.fitness,
        'execution_time': ga_time,
        'routes': ga_routes,
        'fitness_history': ga.fitness_history,
        'time_limit_exceeded': ga_time > MAX_TIME_LIMIT
    }
    # GA sonuçları yazdırılır
    print(f"GA Sonuçları:")
    print(f"  - Tamamlanan teslimat: {ga_delivery_count}/{len(deliveries)}")
    print(f"  - Teslimat oranı: %{(ga_delivery_count/len(deliveries)*100):.1f}")
    print(f"  - Fitness skoru: {best_individual.fitness:.2f}")
    print(f"  - Çalışma süresi: {ga_time:.3f} saniye")
    if ga_time > MAX_TIME_LIMIT:
        print("  ⚠️ Zaman limiti aşıldı!")
    
    # 4. Performans Analizi
    print("\n📊 Performans analizi...")
    
    # Verimlilik metrikleri
    for alg_name, alg_results in results.items():
        efficiency = alg_results['delivery_count'] / alg_results['execution_time'] if alg_results['execution_time'] > 0 else 0
        print(f"{alg_name} verimliliği: {efficiency:.2f} teslimat/saniye")
    
     # En iyi algoritmaları seç (teslimat oranı ve çalışma süresine göre)
    best_rate = max(results.values(), key=lambda x: x['delivery_rate'])
    fastest = min(results.values(), key=lambda x: x['execution_time'])
    
    print(f"En yüksek teslimat oranı: %{best_rate['delivery_rate']*100:.1f}")
    print(f"En hızlı algoritma: {fastest['execution_time']:.3f} saniye")
    
    # 5. Görselleştirme (seçmeli - büyük veri setleri için)
    print("\n📈 Sonuçlar görselleştiriliyor...")
    visualizer = Visualizer(map_size=(150, 150))
    
    # Sadece en iyi sonucu görselleştir (performans için)
    best_alg = max(results.keys(), key=lambda x: results[x]['delivery_rate'])
    best_routes = results[best_alg].get('routes', {})
    
    if best_routes:
        visualizer.plot_scenario(drones, deliveries, no_fly_zones, best_routes,
                                save_path=f"results/scenario2_{best_alg.lower()}_routes.png")
     
    # GA fitness evrimi grafiği
    if 'fitness_history' in results['GA']:
        visualizer.plot_fitness_evolution(results['GA']['fitness_history'],
                                         save_path="results/scenario2_fitness_evolution.png")
    
    # Tüm algoritmaların karşılaştırmalı performansı
    comparison_data = {}
    for alg_name, alg_results in results.items():
        comparison_data[alg_name] = {
            'delivery_rate': alg_results['delivery_rate'] * 100,
            'energy_efficiency': alg_results['delivery_count'] / (alg_results['execution_time'] + 1) * 10,
            'execution_time': alg_results['execution_time']
        }
    
    visualizer.plot_performance_comparison(comparison_data,
                                         save_path="results/scenario2_performance_comparison.png")
    
    # 6. Detaylı rapor oluştur
    print("\n📝 Detaylı test raporu oluşturuluyor...")
    create_detailed_report(results, "results/scenario2_detailed_report.txt", 
                          len(drones), len(deliveries), len(no_fly_zones))
    
    # Senaryo verilerini txt dosyasına kaydet
    loader.save_to_txt(drones, deliveries, no_fly_zones, "data/scenario2_data.txt")
    
    print("\n✅ Test Senaryo 2 tamamlandı!")
    print("Sonuçlar 'results/' klasöründe kaydedildi.")
    
    return results

def create_detailed_report(results, filename, drone_count, delivery_count, zone_count):
    """Detaylı test raporu oluştur- metin dosyasına yaz"""
    with open(filename, 'w', encoding='utf-8') as f: # Belirtilen dosyaya yazmak için açılır
        f.write("TEST SENARYO 2 DETAYLI RAPORU\n")
        f.write("=" * 60 + "\n\n")
        # Testin genel parametreleri yazılır
        f.write("Test Parametreleri:\n") 
        f.write(f"- Drone sayısı: {drone_count}\n")  # Drone sayısı
        f.write(f"- Teslimat sayısı: {delivery_count}\n")  # Teslimat sayısı
        f.write(f"- No-fly zone sayısı: {zone_count}\n") # Yasak bölge sayısı
        f.write("- Performans hedefi: < 60 saniye\n")  # Zaman hedefi
        f.write("- Harita boyutu: 150x150m\n\n") # Harita ölçüsü
         # Her algoritmanın detaylı metrikleri yazılır
        f.write("Algoritma Detayları:\n")
        f.write("-" * 40 + "\n")
        
        for alg_name, alg_results in results.items(): # Her algoritma için teker teker:
            f.write(f"\n{alg_name} Algoritması:\n")
            f.write(f"  Performans Metrikleri:\n")
            f.write(f"    - Tamamlanan teslimat: {alg_results['delivery_count']}\n") # Kaç teslimat yapıldı
            f.write(f"    - Teslimat oranı: %{alg_results['delivery_rate']*100:.1f}\n") # Yüzde olarak
            f.write(f"    - Çalışma süresi: {alg_results['execution_time']:.3f} saniye\n") # Süre
            
            # Verimlilik hesaplanır (teslimat/saniye)
            efficiency = alg_results['delivery_count'] / alg_results['execution_time'] if alg_results['execution_time'] > 0 else 0
            f.write(f"    - Verimlilik: {efficiency:.2f} teslimat/saniye\n")
            
            # Zaman limitinin aşılıp aşılmadığı kontrol edilir
            if alg_results.get('time_limit_exceeded', False):
                f.write(f"    - ⚠️ Zaman limiti aşıldı!\n")
            else:
                f.write(f"    - ✅ Zaman limiti içinde tamamlandı\n")
            # Eğer fitness skoru varsa yazılır (sadece GA için)
            if 'fitness_score' in alg_results:
                f.write(f"    - Fitness skoru: {alg_results['fitness_score']:.2f}\n")
            if 'total_cost' in alg_results:
                f.write(f"    - Toplam maliyet: {alg_results['total_cost']:.2f}\n")
                # Eğer drone kullanım oranı varsa yazılır (CSP için)
            if 'drone_utilization' in alg_results:
                f.write(f"    - Drone kullanım oranı: %{alg_results['drone_utilization']*100:.1f}\n")
        
        # Algoritmaların karşılaştırmalı analizi
        f.write(f"\nKarşılaştırmalı Analiz:\n")
        f.write("-" * 30 + "\n")
        
         # En yüksek teslimat oranına sahip algoritma bulunur
        best_delivery_rate = max(results.values(), key=lambda x: x['delivery_rate'])
        fastest_alg = min(results.values(), key=lambda x: x['execution_time'])
        # Bu algoritmaların isimleri alınır
        best_rate_alg = [alg for alg, res in results.items() if res['delivery_rate'] == best_delivery_rate['delivery_rate']][0]
        fastest_alg_name = [alg for alg, res in results.items() if res['execution_time'] == fastest_alg['execution_time']][0]
         # Karşılaştırma bilgileri yazılır
        f.write(f"En yüksek teslimat oranı: {best_rate_alg} (%{best_delivery_rate['delivery_rate']*100:.1f})\n")
        f.write(f"En hızlı algoritma: {fastest_alg_name} ({fastest_alg['execution_time']:.3f}s)\n")
        
        # Ölçeklenebilirlik değerlendirmesi (kaç algoritma zaman limitine uymuş)
        f.write(f"\nÖlçeklenebilirlik Değerlendirmesi:\n")
        f.write("Bu büyük ölçekli test senaryosu şunları göstermiştir:\n")
        
        time_efficient_count = sum(1 for res in results.values() if not res.get('time_limit_exceeded', False))
        f.write(f"- {time_efficient_count}/{len(results)} algoritma zaman limiti içinde tamamlandı\n")
         # Ortalama teslimat oranı hesaplanır
        avg_delivery_rate = sum(res['delivery_rate'] for res in results.values()) / len(results)
        f.write(f"- Ortalama teslimat oranı: %{avg_delivery_rate*100:.1f}\n")
        
         # Öneriler kısmı
        f.write(f"\nÖneriler:\n")
        if best_delivery_rate['delivery_rate'] > 0.8:
            f.write("✅ Yüksek teslimat oranı başarıyla elde edildi\n")
        else:
            f.write("⚠️ Teslimat oranı optimize edilebilir\n")
            
        if fastest_alg['execution_time'] < 60:
            f.write("✅ Performans hedefi başarıyla karşılandı\n")
        else:
            f.write("⚠️ Algoritma optimizasyonu gerekli\n")

if __name__ == "__main__":
    # Results dizinini oluştur
    os.makedirs("results", exist_ok=True)
    
    # Test senaryosunu çalıştır
    test_scenario_2()
