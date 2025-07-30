#!/usr/bin/env python3
"""
LocalDB Bağlantı Test Scripti

Bu script, LocalDB bağlantısını test eder ve veritabanı durumunu kontrol eder.
"""

import pyodbc
import pandas as pd

def test_localdb_connection():
    """LocalDB bağlantısını test et"""
    print("🔍 LocalDB Bağlantı Testi")
    print("=" * 30)
    
    try:
        # LocalDB'ye bağlan
        conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=master;Trusted_Connection=yes;', timeout=5)
        print("✅ LocalDB bağlantısı başarılı")
        
        # Veritabanı listesini kontrol et
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'HistoricalWeatherDB'")
        result = cursor.fetchone()
        
        if result:
            print("✅ HistoricalWeatherDB veritabanı mevcut")
            conn.close()
            return True
        else:
            print("⚠️ HistoricalWeatherDB veritabanı bulunamadı")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ LocalDB bağlantı hatası: {e}")
        return False

def create_localdb_database():
    """LocalDB'de veritabanı oluştur"""
    print("\n🔧 LocalDB Veritabanı Oluşturma")
    print("=" * 35)
    
    try:
        # Master veritabanına bağlan
        master_conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=master;Trusted_Connection=yes;')
        cursor = master_conn.cursor()
        
        # Veritabanını oluştur
        cursor.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HistoricalWeatherDB') BEGIN CREATE DATABASE HistoricalWeatherDB END")
        master_conn.commit()
        master_conn.close()
        
        print("✅ HistoricalWeatherDB veritabanı LocalDB'de oluşturuldu")
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı oluşturma hatası: {e}")
        return False

def test_historical_weather_db():
    """HistoricalWeatherDB veritabanını test et"""
    print("\n🗄️ HistoricalWeatherDB Testi")
    print("=" * 30)
    
    try:
        # Veritabanına bağlan
        conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=HistoricalWeatherDB;Trusted_Connection=yes;')
        
        # Tabloları kontrol et
        cursor = conn.cursor()
        
        # historical_weather tablosu
        cursor.execute("SELECT COUNT(*) FROM historical_weather")
        weather_count = cursor.fetchone()[0]
        print(f"📊 historical_weather tablosu: {weather_count} kayıt")
        
        # daily_probabilities tablosu
        cursor.execute("SELECT COUNT(*) FROM daily_probabilities")
        prob_count = cursor.fetchone()[0]
        print(f"📊 daily_probabilities tablosu: {prob_count} kayıt")
        
        # Örnek veri göster
        if weather_count > 0:
            print("\n📋 Örnek Veriler:")
            df = pd.read_sql_query("SELECT TOP 5 * FROM historical_weather", conn)
            print(df.to_string(index=False))
        
        if prob_count > 0:
            print("\n📋 Olasılık Verileri:")
            df = pd.read_sql_query("SELECT TOP 5 * FROM daily_probabilities", conn)
            print(df.to_string(index=False))
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ HistoricalWeatherDB test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 LocalDB Bağlantı ve Veritabanı Test Sistemi")
    print("=" * 50)
    
    # LocalDB bağlantısını test et
    if not test_localdb_connection():
        print("\n❌ LocalDB bağlantısı çalışmıyor!")
        print("💡 LocalDB'nin yüklü olduğundan emin olun")
        return
    
    # Veritabanını test et
    if not test_historical_weather_db():
        print("\n⚠️ HistoricalWeatherDB bulunamadı, oluşturuluyor...")
        if create_localdb_database():
            print("✅ Veritabanı oluşturuldu")
            print("💡 SQL Server Management Studio'da create_localdb_database.sql çalıştırın")
            print("   Bağlantı: (LocalDB)\\MSSQLLocalDB")
        else:
            print("❌ Veritabanı oluşturulamadı")
    else:
        print("\n🎉 HistoricalWeatherDB LocalDB'de çalışıyor!")
        print("✅ Tarihsel hava durumu servisi kullanılabilir")

if __name__ == "__main__":
    main() 