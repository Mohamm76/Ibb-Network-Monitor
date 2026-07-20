# -*- coding: utf-8 -*-
"""
Database Data Generator Module with Hidden Credentials
Description: Generates and populates initial telecom data into PostgreSQL securely.
Author: AI Solutions Architect
Date: 2026
"""

import os
import psycopg2
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعدادات الاتصال الآمنة والمستدامة من ملف البيئة
DB_PARAMS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "ibb_telecom_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "root")  # "root" هي القيمة الافتراضية لحماية الكود من الانهيار
}

def generate_ibb_real_network_data():
    """توليد قراءات شبكة افتراضية لمديريات إب وحفظها في قاعدة البيانات إذا كانت فارغة"""
    districts = [
        'المركز (المشنة والظهار)', 'جبلة', 'السدة', 'النادرة',
        'العدين', 'حبيش', 'بعدان', 'السياني', 'ذي السفال', 'يريم',
        'الرضمة', 'القفر', 'المخادر', 'حزم العدين', 'فرع العدين',
        'الشعر', 'السبرة'
    ]
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. إنشاء الجدول الخاص بفرع إب إذا لم يكن موجوداً من قبل
        cur.execute("""
            CREATE TABLE IF NOT EXISTS network_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                district VARCHAR(100) NOT NULL,
                hour INT NOT NULL,
                day_of_week INT NOT NULL,
                latency_ms FLOAT NOT NULL,
                packet_loss_percent FLOAT NOT NULL,
                mpls_bandwidth_usage_percent FLOAT NOT NULL,
                temperature_c FLOAT NOT NULL,
                status VARCHAR(50) NOT NULL
            );
        """)
        conn.commit()
        
        # 2. التحقق مما إذا كانت قاعدة البيانات تحتوي على بيانات مسبقة أم لا
        cur.execute("SELECT COUNT(*) FROM network_logs;")
        count = cur.fetchone()[0]
        
        if count > 0:
            cur.close()
            conn.close()
            return  # قاعدة البيانات تحتوي على بيانات بالفعل، لا حاجة للتكرار
            
        # 3. توليد قراءات تاريخية مكثفة (أرشيف لـ 7 أيام مضت لتغذية الـ Machine Learning)
        base_time = datetime.now() - timedelta(days=7)
        logs_to_insert = []
        
        for day in range(7):
            for hour in range(24):
                current_time = base_time + timedelta(days=day, hours=hour)
                weekday = current_time.weekday()
                
                for dist in districts:
                    # محاكاة واقعية لوقت الذروة في اليمن (من 7 مساءً وحتى 11 مساءً)
                    is_peak = 18 <= hour <= 23
                    
                    if is_peak:
                        mpls_usage = round(random.uniform(75.0, 96.0), 2)
                        latency = round(random.uniform(90.0, 180.0), 2)
                        packet_loss = round(random.uniform(0.5, 4.5), 2)
                    else:
                        mpls_usage = round(random.uniform(30.0, 70.0), 2)
                        latency = round(random.uniform(20.0, 60.0), 2)
                        packet_loss = round(random.uniform(0.0, 0.9), 2)
                    
                    # محاكاة الأعطال المفاجئة (مثل انقطاع الألياف الضوئية الميدانية بنسبة 2%)
                    if random.random() < 0.02:
                        packet_loss = round(random.uniform(8.0, 25.0), 2)
                        status = 'عطل (قطع كابل/برج منفصل)'
                    elif mpls_usage > 85.0:
                        status = 'ازدحام (ذروة المساء)'
                    else:
                        status = 'طبيعي'
                        
                    temp = round(random.uniform(16.0, 32.0), 1)
                    
                    logs_to_insert.append((
                        current_time, dist, hour, weekday, latency, packet_loss, mpls_usage, temp, status
                    ))
        
        # إدخال البيانات دفعة واحدة لضمان السرعة والكفاءة الأكاديمية
        insert_query = """
            INSERT INTO network_logs (timestamp, district, hour, day_of_week, latency_ms, packet_loss_percent, mpls_bandwidth_usage_percent, temperature_c, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.executemany(insert_query, logs_to_insert)
        conn.commit()
        
        cur.close()
        conn.close()
        print("✅ Base network data has been successfully generated inside pgAdmin.")
        
    except Exception as e:
        print(f"❌ Error during initial data deployment: {e}")

if __name__ == "__main__":
    generate_ibb_real_network_data()