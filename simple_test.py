#!/usr/bin/env python3
"""
Basit Multi-Trip Test - Sonsuz döngü olmadan
Bu dosya, örnek veri setini kullanarak çoklu drone teslimat sistemini basit ve zaman sınırlı şekilde test eder.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # Proje dizinini path'e ekler

from src.data_loader import DataLoader # Veri yükleme sınıfı
from src.graph_builder import DeliveryGraph # Teslimat grafını oluşturan sınıf
from src.multi_trip_planner import MultiTripPlanner # Çoklu teslimat turu planlayıcı sınıf

def simple_test():
    """Basit test - sonsuz döngü korumalı"""
    print("🧪 BASİT MULTI-TRIP TESTİ")
    print("="*40)
    
    try:
        # Veri yükle
        loader = DataLoader() # DataLoader sınıfından bir nesne oluşturur
        drones, deliveries, no_fly_zones = loader.load_from_txt("data/sample_data.txt") # Verileri dosyadan alır
        
        print(f"📊 Veri: {len(drones)} drone, {len(deliveries)} teslimat")
        
        # Graf oluştur
        graph = DeliveryGraph(drones, deliveries, no_fly_zones) # Teslimat noktaları ve no-fly alanlarıyla bir graf oluşturur
        
        # Multi-trip planner - ZAMAN LİMİTİ İLE
        planner = MultiTripPlanner(drones, deliveries, no_fly_zones, graph) # Çoklu tur planlayıcı nesnesi
        planner.time_horizon = 120   # 2 saatlik zaman limiti belirlenir (örnek olarak)
        
        print("🔄 Multi-trip başlıyor (2 saat limit)...")
        results = planner.plan_multi_trip_delivery()  # Çoklu teslimat planlamasını çalıştırır
        
        print(f"\n✅ TEST TAMAMLANDI!")
        print(f"   - Teslimat: {results['delivery_count']}/{len(deliveries)} (%{results['delivery_rate']*100:.1f})") # Tamamlanan teslimat sayısı
        print(f"   - Tur sayısı: {results['total_trips']}") # Tamamlanan teslimat sayısı
        print(f"   - Süre: {results['execution_time']:.2f}s") # Çalışma süresi
        
        # Başarı değerlendirmesi
        if results['delivery_rate'] > 0.6:
            print("🎉 BAŞARILI: %60+ teslimat oranı!")
        elif results['delivery_rate'] > 0.3:
            print("⚠️ ORTA: %30+ teslimat oranı")
        else:
            print("❌ DÜŞÜK: %30 altı teslimat oranı")
            
        return results  # Sonuçları döndür
        
    except KeyboardInterrupt:
        print("\n⚠️ Test kullanıcı tarafından durduruldu")
        return None
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    simple_test()  # Ana program olarak çalıştırıldığında test başlatılır
