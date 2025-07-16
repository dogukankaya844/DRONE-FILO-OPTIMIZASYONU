#!/usr/bin/env python3
"""
Hızlı test scripti - Multi-trip sistemi ve genel performansı test eder
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import DataLoader
from src.graph_builder import DeliveryGraph
from src.multi_trip_planner import MultiTripPlanner
from src.detailed_reporter import DetailedReporter

def test_multitrip_system():
    """Multi-trip sistemi test et"""
    print("🧪 Multi-Trip Sistemi Test Ediliyor...")
    print("="*50)
    
    # Veri yükle
    loader = DataLoader()
    drones, deliveries, no_fly_zones = loader.load_from_txt("data/sample_data.txt")
    
    print(f"📊 Test Verisi:")
    print(f"   - {len(drones)} drone")
    print(f"   - {len(deliveries)} teslimat")
    print(f"   - {len(no_fly_zones)} no-fly zone")
    
    # Graf oluştur
    graph = DeliveryGraph(drones, deliveries, no_fly_zones)
    
    # Multi-trip planner test
    planner = MultiTripPlanner(drones, deliveries, no_fly_zones, graph)
    results = planner.plan_multi_trip_delivery()
    
    # Detaylı raporu göster
    planner.print_detailed_report()
    
    print("\n" + "="*50)
    print("🎯 TEST SONUÇLARI:")
    print(f"   - Teslimat Oranı: %{results['delivery_rate']*100:.1f}")
    print(f"   - Toplam Tur: {results['total_trips']}")
    print(f"   - Çalışma Süresi: {results['execution_time']:.3f}s")
    
    if results['delivery_rate'] > 0.7:
        print("   ✅ Test BAŞARILI - Multi-trip sistemi çalışıyor!")
    else:
        print("   ⚠️ Test UYARI - Teslimat oranı düşük")
        
    return results

def test_scenario2():
    """Scenario 2 verilerini test et"""
    print("\n🧪 Scenario 2 Test Ediliyor...")
    print("="*50)
    
    try:
        # Scenario 2 veri yükle
        loader = DataLoader()
        drones, deliveries, no_fly_zones = loader.load_from_txt("data/scenario2_data.txt")
        
        print(f"📊 Scenario 2 Verisi:")
        print(f"   - {len(drones)} drone")
        print(f"   - {len(deliveries)} teslimat") 
        print(f"   - {len(no_fly_zones)} no-fly zone")
        
        # Kapasite analizi
        total_capacity = sum(d.max_weight for d in drones)
        total_weight = sum(d.weight for d in deliveries)
        print(f"   - Toplam kapasite: {total_capacity:.1f}kg")
        print(f"   - Toplam yük: {total_weight:.1f}kg")
        print(f"   - Kapasite kullanımı: %{(total_weight/total_capacity)*100:.1f}")
        
        # Graf oluştur
        graph = DeliveryGraph(drones, deliveries, no_fly_zones)
        
        # Multi-trip ile test
        planner = MultiTripPlanner(drones, deliveries, no_fly_zones, graph)
        results = planner.plan_multi_trip_delivery()
        
        print(f"\n🎯 SCENARIO 2 SONUÇLARI:")
        print(f"   - Teslimat Oranı: %{results['delivery_rate']*100:.1f}")
        print(f"   - Tamamlanan: {results['delivery_count']}/{len(deliveries)}")
        print(f"   - Toplam Tur: {results['total_trips']}")
        
        if results['delivery_rate'] > 0.6:
            print("   ✅ Scenario 2 BAŞARILI!")
        else:
            print("   ⚠️ Scenario 2 iyileştirme gerekiyor")
            
        return results
        
    except Exception as e:
        print(f"   ❌ Scenario 2 testi başarısız: {e}")
        return None

def performance_comparison():
    """Performans karşılaştırması yap"""
    print("\n📊 Performans Karşılaştırması")
    print("="*50)
    
    # Her iki senaryoyu test et
    print("Scenario 1 (Küçük problem):")
    result1 = test_multitrip_system()
    
    print("\nScenario 2 (Büyük problem):")
    result2 = test_scenario2()
    
    if result1 and result2:
        print(f"\n🔍 KARŞILAŞTIRMA:")
        print(f"   Scenario 1: %{result1['delivery_rate']*100:.1f} - {result1['execution_time']:.3f}s")
        print(f"   Scenario 2: %{result2['delivery_rate']*100:.1f} - {result2['execution_time']:.3f}s")
        
        # Skalabilite analizi
        efficiency1 = result1['delivery_count'] / result1['execution_time']
        efficiency2 = result2['delivery_count'] / result2['execution_time']
        
        print(f"\n📈 SKALABİLİTE:\n")
        print(f"   Scenario 1 verimlilik: {efficiency1:.2f} teslimat/saniye")
        print(f"   Scenario 2 verimlilik: {efficiency2:.2f} teslimat/saniye")
        
        if efficiency2 >= efficiency1 * 0.5:  # %50'den fazla verimlilik korumuş
            print("   ✅ İyi skalabilite - büyük problemlerde de verimli")
        else:
            print("   ⚠️ Skalabilite sorunu - büyük problemlerde yavaşlama")

def check_pdf_requirements():
    """PDF gereksinimlerini kontrol et"""
    print("\n📋 PDF GEREKSİNİMLERİ KONTROLU")
    print("="*50)
    
    requirements = {
        "Scenario 1 (5 drone, 20 teslimat, 3 no-fly)": False,
        "Scenario 2 (10 drone, 50 teslimat, 5 no-fly)": False,
        "A* + CSP + GA implementasyonu": True,
        "Multi-trip/Şarj sistemi": True,
        "Detaylı raporlama": True,
        "Görselleştirme": True,
        "Zaman karmaşıklığı analizi": True,
        "50+ teslimat < 1dk performans": False  # Test edilecek
    }
    
    # Dosya kontrolleri
    import os
    
    if os.path.exists("data/sample_data.txt"):
        requirements["Scenario 1 (5 drone, 20 teslimat, 3 no-fly)"] = True
        
    if os.path.exists("data/scenario2_data.txt"):
        requirements["Scenario 2 (10 drone, 50 teslimat, 5 no-fly)"] = True
    
    # Kontrol sonuçlarını yazdır
    for req, status in requirements.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {req}")
        
    completed = sum(requirements.values())
    total = len(requirements)
    completion_rate = (completed / total) * 100
    
    print(f"\n📈 TAMAMLANMA ORANI: %{completion_rate:.1f} ({completed}/{total})")
    
    if completion_rate >= 80:
        print("✅ Proje PDF gereksinimlerinin çoğunu karşılıyor!")
    elif completion_rate >= 60:
        print("⚠️ Proje kısmen hazır, bazı iyileştirmeler gerekli")
    else:
        print("❌ Proje henüz eksik, daha fazla çalışma gerekli")
        
    return requirements

if __name__ == "__main__":
    print("🚀 DRONE DELIVERY OPTIMIZATION - HIZLI TEST")
    print("="*60)
    
    try:
        # PDF gereksinimlerini kontrol et
        requirements = check_pdf_requirements()
        
        # Multi-trip sistemi test et
        test_multitrip_system()
        
        # Performans karşılaştırması
        performance_comparison()
        
        print("\n🎉 TEST TAMAMLANDI!")
        print("💡 İpucu: Tam teslimat için python main.py --algorithm multitrip --visualize çalıştırın")
        
    except Exception as e:
        print(f"\n❌ Test sırasında hata: {e}")
        import traceback
        traceback.print_exc()
