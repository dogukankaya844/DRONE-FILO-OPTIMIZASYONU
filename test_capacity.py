#!/usr/bin/env python3
"""
Düzeltilmiş Multi-Trip Test - Kapasiteyi doğru kullanıp kullanmadığını test eder
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import DataLoader
from src.graph_builder import DeliveryGraph
from src.multi_trip_planner import MultiTripPlanner

def test_capacity_usage():
    """Kapasite kullanımını test et"""
    print("🧪 KAPASİTE KULLANIMI TESTİ")
    print("="*60)
    
    # Veri yükle
    loader = DataLoader()
    drones, deliveries, no_fly_zones = loader.load_from_txt("data/sample_data.txt")
    
    # Analiz
    total_capacity = sum(d.max_weight for d in drones)
    total_weight = sum(d.weight for d in deliveries)
    
    print(f"📊 PROBLEMİN BOYUTU:")
    print(f"   - Drone sayısı: {len(drones)}")
    print(f"   - Teslimat sayısı: {len(deliveries)}")
    print(f"   - Toplam drone kapasitesi: {total_capacity:.1f}kg")
    print(f"   - Toplam teslimat ağırlığı: {total_weight:.1f}kg")
    print(f"   - Kapasite açığı: {total_weight - total_capacity:.1f}kg ({((total_weight/total_capacity)-1)*100:.1f}% fazla)")
    
    print(f"\n🚁 DRONE DETAYLARI:")
    for drone in drones:
        print(f"   Drone {drone.id}: {drone.max_weight:.1f}kg kapasite, {drone.battery}mAh batarya")
    
    print(f"\n📦 TESLİMAT DETAYLARI:")
    deliveries_by_priority = {}
    for delivery in deliveries:
        if delivery.priority not in deliveries_by_priority:
            deliveries_by_priority[delivery.priority] = []
        deliveries_by_priority[delivery.priority].append(delivery)
    
    for priority in sorted(deliveries_by_priority.keys(), reverse=True):
        dlist = deliveries_by_priority[priority]
        total_weight_p = sum(d.weight for d in dlist)
        print(f"   Öncelik {priority}: {len(dlist)} paket, {total_weight_p:.1f}kg")
    
    # Graf oluştur ve test et
    graph = DeliveryGraph(drones, deliveries, no_fly_zones)
    
    print(f"\n🔄 MULTI-TRIP SİMÜLASYONU BAŞLIYOR...")
    print("="*60)
    
    # Multi-trip planner
    planner = MultiTripPlanner(drones, deliveries, no_fly_zones, graph)
    results = planner.plan_multi_trip_delivery()
    
    print("\n" + "="*60)
    print("🎯 TEST SONUÇLARI")
    print("="*60)
    
    print(f"📈 GENEL PERFORMANS:")
    print(f"   - Tamamlanan teslimat: {results['delivery_count']}/{len(deliveries)} (%{results['delivery_rate']*100:.1f})")
    print(f"   - Toplam tur sayısı: {results['total_trips']}")
    print(f"   - Çalışma süresi: {results['execution_time']:.3f} saniye")
    
    # Detaylı drone analizi
    if 'drone_reports' in results:
        print(f"\n🚁 DRONE PERFORMANS ANALİZİ:")
        print(f"{'Drone':<6} {'Tur':<4} {'Teslimat':<9} {'Kapasite%':<10} {'Verimlilik':<10}")
        print("-"*50)
        
        total_utilization = 0
        for drone_id, report in results['drone_reports'].items():
            drone = next(d for d in drones if d.id == drone_id)
            
            # Ortalama kapasite kullanımı hesapla
            if report['trips_detail']:
                avg_capacity = sum(trip['total_weight'] for trip in report['trips_detail']) / len(report['trips_detail'])
                capacity_pct = (avg_capacity / drone.max_weight) * 100
            else:
                capacity_pct = 0
                
            efficiency = report['total_deliveries'] / max(1, report['total_trips'])
            total_utilization += capacity_pct
            
            print(f"{drone_id:<6} {report['total_trips']:<4} {report['total_deliveries']:<9} "
                  f"{capacity_pct:<10.1f} {efficiency:<10.2f}")
        
        avg_utilization = total_utilization / len(results['drone_reports'])
        print(f"\nOrtalama kapasite kullanımı: %{avg_utilization:.1f}")
        
        # Başarı değerlendirmesi
        print(f"\n🏆 BAŞARI DEĞERLENDİRMESİ:")
        if results['delivery_rate'] > 0.85:
            print("   ✅ MÜKEMMEL: %85+ teslimat oranı")
        elif results['delivery_rate'] > 0.7:
            print("   ✅ İYİ: %70+ teslimat oranı") 
        elif results['delivery_rate'] > 0.5:
            print("   ⚠️ ORTA: %50+ teslimat oranı")
        else:
            print("   ❌ DÜŞÜK: %50 altı teslimat oranı")
            
        if avg_utilization > 80:
            print("   ✅ Kapasite kullanımı çok iyi")
        elif avg_utilization > 60:
            print("   ⚠️ Kapasite kullanımı orta")
        else:
            print("   ❌ Kapasite kullanımı düşük")
            
        # Teorik maksimum hesapla
        theoretical_max_trips = 0
        for drone in drones:
            possible_trips = int(total_weight / drone.max_weight) + 1
            theoretical_max_trips += possible_trips
            
        print(f"\n📊 KAPASİTE ANALİZİ:")
        print(f"   - Gerçek tur sayısı: {results['total_trips']}")
        print(f"   - Teorik minimum tur: {int(total_weight / total_capacity) + len(drones)}")
        print(f"   - Tur verimliliği: {results['total_trips'] / theoretical_max_trips * 100:.1f}%")

if __name__ == "__main__":
    test_capacity_usage()
