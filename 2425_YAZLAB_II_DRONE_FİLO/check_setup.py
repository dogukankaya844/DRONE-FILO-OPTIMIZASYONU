#!/usr/bin/env python3
"""
Proje Kurulum ve Test Scripti
Bu script projenin doğru çalışıp çalışmadığını test eder
"""

import sys
import os
import importlib.util

def check_python_version():
    """Python sürümünü kontrol et"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 veya üzeri gerekli!")
        print(f"   Mevcut sürüm: {sys.version}")
        return False
    else:
        print(f"✅ Python sürümü uygun: {sys.version.split()[0]}")
        return True

def check_required_modules():
    """Gerekli modüllerin yüklenip yüklenmediğini kontrol et"""
    required_modules = [
        'numpy', 'matplotlib', 'scipy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} modülü yüklü")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} modülü eksik")
    
    if missing_modules:
        print(f"\n🔧 Eksik modülleri yüklemek için:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    return True

def check_project_structure():
    """Proje yapısını kontrol et"""
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/drone.py',
        'src/delivery_point.py',
        'src/no_fly_zone.py',
        'src/graph_builder.py',
        'src/astar.py',
        'src/csp_solver.py',
        'src/genetic_algorithm.py',
        'src/data_loader.py',
        'src/data_generator.py',
        'src/visualizer.py',
        'data/sample_data.txt',
        'tests/test_scenario1.py',
        'tests/test_scenario2.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file} eksik")
    
    return len(missing_files) == 0

def test_basic_functionality():
    """Temel fonksiyonaliteyi test et"""
    try:
        # Modülleri import et
        sys.path.insert(0, '.')
        from src.drone import Drone
        from src.delivery_point import DeliveryPoint
        from src.no_fly_zone import NoFlyZone
        from src.data_loader import DataLoader
        
        # Temel nesneler oluştur
        drone = Drone(1, 5.0, 15000, 8.0, (10, 10))
        delivery = DeliveryPoint(1, (25, 30), 2.0, 3, (0, 60))
        no_fly = NoFlyZone(1, [(20, 20), (30, 20), (30, 30), (20, 30)], (10, 50))
        
        # Basit testler
        assert drone.can_carry(3.0) == True
        assert drone.can_carry(7.0) == False
        assert delivery.is_within_time_window(30) == True
        assert no_fly.is_active(25) == True
        
        print("✅ Temel fonksiyonalite testi başarılı")
        return True
        
    except Exception as e:
        print(f"❌ Temel fonksiyonalite testi başarısız: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚁 Drone Filo Optimizasyonu - Proje Kurulum Kontrolü")
    print("=" * 60)
    
    all_good = True
    
    # Python sürümü
    if not check_python_version():
        all_good = False
    
    print()
    
    # Proje yapısı
    print("📁 Proje yapısı kontrol ediliyor...")
    if not check_project_structure():
        all_good = False
    
    print()
    
    # Gerekli modüller
    print("📦 Gerekli modüller kontrol ediliyor...")
    modules_ok = check_required_modules()
    
    print()
    
    # Temel fonksiyonalite (sadece modüller varsa)
    if modules_ok:
        print("🧪 Temel fonksiyonalite test ediliyor...")
        if not test_basic_functionality():
            all_good = False
    else:
        all_good = False
    
    print()
    print("=" * 60)
    
    if all_good:
        print("🎉 Proje kurulumu başarılı!")
        print("\n📋 Projeyi çalıştırmak için:")
        print("   python main.py --visualize")
        print("\n🧪 Test senaryolarını çalıştırmak için:")
        print("   python tests/test_scenario1.py")
        print("   python tests/test_scenario2.py")
    else:
        print("❌ Proje kurulumunda sorunlar var!")
        print("\n🔧 Sorunları çözmek için:")
        print("1. Python 3.8+ yüklü olduğundan emin olun")
        print("2. Gerekli kütüphaneleri yükleyin: pip install -r requirements.txt")
        print("3. Eksik dosyaları kontrol edin")
        
    return 0 if all_good else 1

if __name__ == "__main__":
    exit(main())
