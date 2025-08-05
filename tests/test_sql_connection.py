#!/usr/bin/env python3
"""
SQL Server Bağlantı Test Scripti

Bu script, SQL Server bağlantısını test eder ve veritabanı durumunu kontrol eder.
"""

import pyodbc
import pandas as pd

def test_sql_server_connection():
    """SQL Server bağlantısını test et"""
    print("🔍 SQL Server Bağlantı Testi")
    print("=" * 40)
    
    # Test edilecek bağlantı string'leri
    connection_strings = [
        {
            "name": "SQL Server (localhost)",
            "string": "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;"
        },
        {
            "name": "SQL Server LocalDB",
            "string": "Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=master;Trusted_Connection=yes;"
        },
        {
            "name": "SQL Server Express",
            "string": "Driver={ODBC Driver 17 for SQL Server};Server=.\\SQLEXPRESS;Database=master;Trusted_Connection=yes;"
        }
    ]
    
    working_connection = None
    
    for conn_info in connection_strings:
        try:
            print(f"\n📡 {conn_info['name']} test ediliyor...")
            conn = pyodbc.connect(conn_info['string'], timeout=5)
            
            # Veritabanı listesini al
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.databases WHERE name = 'HistoricalWeatherDB'")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ {conn_info['name']}: Bağlantı başarılı")
                print(f"   📊 HistoricalWeatherDB veritabanı mevcut")
                working_connection = conn_info #Bağlantı bilgilerini atama
                break
            else:
                print(f"✅ {conn_info['name']}: Bağlantı başarılı")
                print(f"   ⚠️ HistoricalWeatherDB veritabanı bulunamadı")
                working_connection = conn_info 
                break
                
        except Exception as e:
            print(f"❌ {conn_info['name']}: Bağlantı başarısız - {e}")
    
    return working_connection

def test_historical_weather_db():
    """HistoricalWeatherDB veritabanını test et"""
    print("\n🗄️ HistoricalWeatherDB Testi")
    print("=" * 30)
    
    try:
        # Veritabanına bağlan
        conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=HistoricalWeatherDB;Trusted_Connection=yes;')
        
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

def create_database_if_not_exists():
    """Veritabanı yoksa oluştur"""
    print("\n🔧 Veritabanı Oluşturma")
    print("=" * 25)
    
    try:
        # Master veritabanına bağlan
        master_conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;')
        cursor = master_conn.cursor()
        
        # Veritabanını oluştur
        cursor.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HistoricalWeatherDB') BEGIN CREATE DATABASE HistoricalWeatherDB END")
        master_conn.commit()
        master_conn.close()
        
        print("✅ HistoricalWeatherDB veritabanı oluşturuldu")
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı oluşturma hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 SQL Server Bağlantı ve Veritabanı Test Sistemi")
    print("=" * 55)
    
    # SQL Server bağlantısını test et
    working_conn = test_sql_server_connection()
    
    if not working_conn:
        print("\n❌ Hiçbir SQL Server bağlantısı çalışmıyor!")
        print("💡 SQL Server Management Studio ile veritabanı oluşturun:")
        print("   1. SQL Server Management Studio'yu açın")
        print("   2. create_database.sql dosyasını çalıştırın")
        return
    
    print(f"\n✅ Çalışan bağlantı: {working_conn['name']}")
    
    # Veritabanını test et
    if not test_historical_weather_db():
        print("\n⚠️ HistoricalWeatherDB bulunamadı, oluşturuluyor...")
        if create_database_if_not_exists():
            print("✅ Veritabanı oluşturuldu, tabloları manuel olarak oluşturun")
            print("💡 SQL Server Management Studio'da create_database.sql çalıştırın")
        else:
            print("❌ Veritabanı oluşturulamadı")
    else:
        print("\n🎉 HistoricalWeatherDB çalışıyor!")
        print("✅ Tarihsel hava durumu servisi kullanılabilir")

if __name__ == "__main__":
    main() 