"""
Bu dosya, proje çalıştıktan sonra ortaya çıkan çıktıları analiz eden ve metin raporu olarak belgeleyen bir "rapor üreticisi"dir.
"""
import os # Dosya ve dizin işlemleri için
from typing import Dict, List # Tip belirtme için
from datetime import datetime # Zaman bilgisi almak için

class DetailedReporter:
    """Detaylı rapor oluşturucu"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True) # Sonuç klasörünü oluşturur, varsa atlar
        
    def create_comprehensive_report(self, all_results: Dict, drones: List, 
                                  deliveries: List, no_fly_zones: List):
        """Kapsamlı rapor oluştur"""
        report_path = f"{self.output_dir}/comprehensive_report.txt" # Rapor dosya yolu
        
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_header(f) # Başlık yazdır 
            self._write_problem_definition(f, drones, deliveries, no_fly_zones)  # Problem bilgileri
            self._write_algorithm_results(f, all_results, deliveries) # Algoritma sonuçları
            self._write_drone_performance_analysis(f, all_results, drones) # Drone performans
            self._write_delivery_analysis(f, deliveries, all_results) # Teslimat analizi
            self._write_time_complexity_analysis(f, all_results) # Zaman karmaşıklığı
            self._write_recommendations(f, all_results, drones, deliveries) # Öneriler
            
        print(f"📝 Kapsamlı rapor oluşturuldu: {report_path}") # Oluştu bildirimi
        return report_path # Rapor yolu döner
    
    def _write_header(self, f):
        """Rapor başlığı"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Zaman damgası
        f.write("="*80 + "\n")
        f.write("   DRONE FİLO OPTİMİZASYONU - KAPSAMLI PERFORMANS RAPORU\n")
        f.write("   Kocaeli Üniversitesi TBL331 - Yazılım Geliştirme Lab II\n")
        f.write(f"   Rapor Tarihi: {timestamp}\n")
        f.write("="*80 + "\n\n")
        
    def _write_problem_definition(self, f, drones, deliveries, no_fly_zones):
        """Problem tanımı bölümü"""
        f.write("📋 PROBLEM TANIMI\n")
        f.write("-"*50 + "\n")
        f.write(f"Drone Sayısı: {len(drones)}\n") # Toplam drone sayısı
        f.write(f"Teslimat Noktası Sayısı: {len(deliveries)}\n")  # Toplam teslimat
        f.write(f"No-Fly Zone Sayısı: {len(no_fly_zones)}\n\n") # Yasak bölge sayısı
        
        # Drone detayları
        f.write("🚁 DRONE DETAYLARI:\n")
        total_capacity = 0
        total_battery = 0
        for drone in drones:
            f.write(f"  Drone {drone.id:2d}: Kapasite={drone.max_weight:4.1f}kg, "
                   f"Batarya={int(drone.battery):5d}mAh, Hız={drone.speed:4.1f}m/s, "
                   f"Konum=({drone.start_pos[0]:3.0f},{drone.start_pos[1]:3.0f})\n")
            total_capacity += drone.max_weight # Toplam kapasite hesapla
            total_battery += drone.battery # Toplam batarya
            
        f.write(f"  Toplam Kapasite: {total_capacity:.1f}kg\n")
        f.write(f"  Toplam Batarya: {total_battery:,}mAh\n\n")
        
        # Teslimat analizi
        f.write("📦 TESLİMAT ANALİZİ:\n")
        total_weight = sum(d.weight for d in deliveries) # Toplam teslimat ağırlığı
        priority_counts = {}
        
        for delivery in deliveries:
            priority_counts[delivery.priority] = priority_counts.get(delivery.priority, 0) + 1 # Öncelik sayısı
            
        f.write(f"  Toplam Ağırlık: {total_weight:.1f}kg\n")
        f.write(f"  Ortalama Ağırlık: {total_weight/len(deliveries):.2f}kg\n")
        f.write(f"  Kapasite Kullanım Oranı: %{(total_weight/total_capacity)*100:.1f}\n")
        f.write(f"  Öncelik Dağılımı: {dict(sorted(priority_counts.items()))}\n\n")
        
        # No-fly zone analizi
        if no_fly_zones:
            f.write("🚫 NO-FLY ZONE ANALİZİ:\n")
            for zone in no_fly_zones:
                f.write(f"  Zone {zone.id}: Aktif {zone.active_time[0]}-{zone.active_time[1]}dk\n")
        f.write("\n")
        
    def _write_algorithm_results(self, f, all_results, deliveries):
        """Algoritma sonuçları bölümü"""
        f.write("🎯 ALGORİTMA SONUÇLARI\n")
        f.write("-"*60 + "\n")
        
        # Performans tablosu
        f.write(f"{'Algoritma':<15} {'Teslimat':<12} {'Oran(%)':<8} {'Süre(s)':<10} {'Verimlilik':<10}\n")
        f.write("-"*60 + "\n")
        # Algoritmaların performans verileri
        for alg_name, result in all_results.items():
            if result.get('success', True):
                delivery_count = result['delivery_count']
                delivery_rate = result['delivery_rate'] * 100
                exec_time = result['execution_time']
                efficiency = delivery_count / (exec_time + 0.001)
                
                f.write(f"{alg_name:<15} {delivery_count:>3}/{len(deliveries):<8} "
                       f"{delivery_rate:>6.1f} {exec_time:>9.3f} {efficiency:>9.2f}\n")
            else:
                f.write(f"{alg_name:<15} {'Başarısız':<12} {'N/A':<8} {'N/A':<10} {'N/A':<10}\n")
                
        f.write("\n")
        
        # Detaylı algoritma analizi
        for alg_name, result in all_results.items():
            f.write(f"📊 {alg_name.upper()} DETAYLI ANALİZ:\n")
            
            if result.get('success', True):
                f.write(f"  ✅ Başarı Durumu: Başarılı\n")
                f.write(f"  📈 Teslimat Sayısı: {result['delivery_count']}/{len(deliveries)}\n")
                f.write(f"  🎯 Teslimat Oranı: %{result['delivery_rate']*100:.1f}\n")
                f.write(f"  ⏱️ Çalışma Süresi: {result['execution_time']:.3f} saniye\n")
                
                if 'total_cost' in result:
                    f.write(f"  💰 Toplam Maliyet: {result['total_cost']:.2f}\n")
                if 'fitness_score' in result:
                    f.write(f"  🧬 Fitness Skoru: {result['fitness_score']:.2f}\n")
                if 'total_trips' in result:
                    f.write(f"  🔄 Toplam Tur Sayısı: {result['total_trips']}\n")
                    
            else:
                f.write(f"  ❌ Başarı Durumu: Başarısız\n")
                f.write(f"  ⚠️ Çözüm bulunamadı\n")
                
            f.write("\n")
    
    def _write_drone_performance_analysis(self, f, all_results, drones):
        """Drone performans analizi"""
        f.write("🚁 DRONE PERFORMANS ANALİZİ\n")
        f.write("-"*60 + "\n")
        
        # Multi-Trip sonuçları varsa detaylı analiz
        if 'Multi-Trip' in all_results and 'drone_reports' in all_results['Multi-Trip']:
            drone_reports = all_results['Multi-Trip']['drone_reports']
            
            f.write("📊 DRONE PERFORMANS TABLOSU:\n")
            f.write(f"{'Drone':<6} {'Tur':<4} {'Teslimat':<9} {'Mesafe(m)':<10} {'Şarj':<5} {'Kullanım(%)':<10}\n")
            f.write("-"*50 + "\n")
            # Her drone için genel özet
            for drone_id, report in drone_reports.items():
                f.write(f"{drone_id:<6} {report['total_trips']:<4} "
                       f"{report['total_deliveries']:<9} "
                       f"{report['total_distance']:<10.0f} "
                       f"{report['charging_cycles']:<5} "
                       f"{report['utilization_rate']:<10.1f}\n")
                   # Drone bazlı detaylı performans 
            f.write("\n")
            
            # Her drone için detaylı performans
            f.write("🔍 DRONE DETAYLI PERFORMANS:\n")
            for drone_id, report in drone_reports.items():
                drone = next((d for d in drones if d.id == drone_id), None)
                if drone:
                    f.write(f"\n🚁 DRONE {drone_id} (Kap: {drone.max_weight}kg, Bat: {drone.max_battery}mAh):\n")
                    f.write(f"   📦 {report['total_deliveries']} teslimat / {report['total_trips']} tur\n")
                    f.write(f"   🗺️ {report['total_distance']:.0f}m mesafe\n")
                    f.write(f"   🔋 {report['charging_cycles']} şarj / %{report['utilization_rate']:.1f} kullanım\n")
                    
                   # İlk birkaç turun teslimat sayısı gösterilir
                    if report['trips_detail']:
                        f.write(f"   📋 İlk Turlar: ")
                        for i, trip in enumerate(report['trips_detail'][:3]):
                            f.write(f"T{trip['trip_number']}({len(trip['deliveries'])}), ")
                        if len(report['trips_detail']) > 3:
                            f.write("...")
                        f.write("\n")
                        
              # En iyi ve en kötü drone belirlenir
            if len(drone_reports) > 1:
                best_drone = max(drone_reports.keys(), 
                               key=lambda x: drone_reports[x]['total_deliveries'])
                worst_drone = min(drone_reports.keys(), 
                                key=lambda x: drone_reports[x]['total_deliveries'])
                                
                f.write(f"\n🏆 PERFORMANS KARŞILAŞTIRMASI:\n")
                f.write(f"   ✅ En İyi: Drone {best_drone} "
                       f"({drone_reports[best_drone]['total_deliveries']} teslimat)\n")
                f.write(f"   ⚠️ En Düşük: Drone {worst_drone} "
                       f"({drone_reports[worst_drone]['total_deliveries']} teslimat)\n")
                       
        else:
            f.write("Multi-Trip analizi mevcut değil.\n")
        
        f.write("\n")
    
    def _write_delivery_analysis(self, f, deliveries, all_results):
        """Teslimat analizi"""
        f.write("📦 TESLİMAT ANALİZİ\n")
        f.write("-"*40 + "\n")
        
        # Önceliklere göre teslimat istatistikleri hazırlanır
        priority_stats = {}
        for delivery in deliveries:
            priority = delivery.priority
            if priority not in priority_stats:
                priority_stats[priority] = {'count': 0, 'total_weight': 0, 'delivered': 0}
            priority_stats[priority]['count'] += 1
            priority_stats[priority]['total_weight'] += delivery.weight
            
         # Başarıyla teslim edilenler sayılır
        if 'Multi-Trip' in all_results and 'completed_deliveries' in all_results['Multi-Trip']:
            completed = all_results['Multi-Trip']['completed_deliveries']
            for delivery in completed:
                priority_stats[delivery.priority]['delivered'] += 1
                
        f.write(f"{'Öncelik':<8} {'Toplam':<7} {'Teslim':<7} {'Oran(%)':<8}\n")
        f.write("-"*32 + "\n")
        # Öncelik sırasına göre yazdırılır
        for priority in sorted(priority_stats.keys(), reverse=True):
            stats = priority_stats[priority]
            rate = (stats['delivered'] / stats['count']) * 100 if stats['count'] > 0 else 0
            f.write(f"{priority:<8} {stats['count']:<7} {stats['delivered']:<7} {rate:<8.1f}\n")
                   
        f.write("\n")
        
    def _write_time_complexity_analysis(self, f, all_results):
        """Zaman karmaşıklığı analizi"""
        f.write("⏱️ ZAMAN KARMAŞIKLIĞI ANALİZİ\n")
        f.write("-"*50 + "\n")
        
        f.write("Big O Notasyonu:\n")
        f.write("🎯 A*: O(b^d) - b:branching (dallanma), d:depth(derinlik) Her drone'un gideceği nokta sayısı arttıkça (d) ve bağlantılı düğüm sayısı büyüdükçe (b), arama ağacı katlanarak büyür. \n")
        f.write("🧩 CSP: O(d^n) - d:domain, n:variables Kısıtların kontrolü nedeniyle çözüm uzayı katlanarak büyür: her bir teslimatın bir drone’a atanma kombinasyonları\n")
        f.write("🧬 GA: O(g*p*f) - g:generations, p:population, f:fitness her nesilde p adet bireyin fitness’ı hesaplanıyor\n")
        f.write("🔄 Multi-Trip: O(t*d*n^2) - t:time, d:drones, n:deliveries Teslimatlar arası mesafeler, her drone için tekrar tekrar değerlendiriliyor\n\n")
        
        # Gerçek zamanlı performans verileri
        f.write("📈 GERÇEK PERFORMANS:\n")
        f.write(f"{'Algoritma':<12} {'Süre(s)':<8} {'Verimlilik':<10}\n")
        f.write("-"*32 + "\n")
        
        for alg_name, result in all_results.items():
            if result.get('success', True):
                exec_time = result['execution_time']
                efficiency = result['delivery_count'] / (exec_time + 0.001)
                f.write(f"{alg_name:<12} {exec_time:<8.3f} {efficiency:<10.2f}\n")
                
        f.write("\n")
        
    def _write_recommendations(self, f, all_results, drones, deliveries):
        """Öneriler ve değerlendirme"""
        f.write("💡 ÖNERİLER VE DEĞERLENDİRME\n")
        f.write("-"*50 + "\n")
        
        # En iyi algoritmayı bulur
        best_algorithm = None
        best_rate = 0
        
        for alg_name, result in all_results.items():
            if result.get('success', True) and result['delivery_rate'] > best_rate:
                best_rate = result['delivery_rate']
                best_algorithm = alg_name
                
        if best_algorithm:
            f.write(f"🏆 EN İYİ ALGORİTMA: {best_algorithm}\n")
            f.write(f"   - Teslimat oranı: %{best_rate*100:.1f}\n\n")
            
         # Sistem kapasite değerlendirmesi
        total_capacity = sum(drone.max_weight for drone in drones)
        total_weight = sum(delivery.weight for delivery in deliveries)
        capacity_util = (total_weight / total_capacity) * 100
        
        f.write("🔍 SİSTEM DEĞERLENDİRMESİ:\n")
        
        if best_rate > 0.8:
            f.write("   ✅ Yüksek teslimat oranı\n")
        elif best_rate > 0.6:
            f.write("   ⚠️ Orta düzey teslimat oranı\n")
        else:
            f.write("   ❌ Düşük teslimat oranı\n")
            
        if capacity_util > 200:
            f.write("   ⚠️ Aşırı kapasite yükü\n")
        elif capacity_util > 100:
            f.write("   🔄 Multi-trip gerekli\n")
        else:
            f.write("   ✅ Dengeli kapasite\n")
            
        f.write("\n")
        
       # Geliştirme önerileri
        f.write("🎯 ÖNERİLER:\n")
        if best_rate < 0.7:
            f.write("   1. 📈 Drone sayısını artırın\n")
            f.write("   2. 🔋 Batarya kapasitelerini optimize edin\n")
        f.write("   3. 📊 Real-time monitoring ekleyin\n")
        f.write("   4. 🔄 Adaptif algoritma seçimi\n")
        f.write("   5. 🎯 Dinamik rota güncelleme\n\n")
