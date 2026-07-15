# -*- coding: utf-8 -*-
"""
Updated Data Generator for Ibb MPLS Network Monitor
Description: Real-world simulation based on Ibb terrain, aerial cables, wireless towers, and actual peak hours.
Author: AI Solutions Architect
Date: 2026
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_ibb_real_network_data(num_records=600, output_filename="assets/network_data.csv"):
    np.random.seed(42)
    
    # 1. قائمة بجميع مديريات محافظة إب الـ 18 (لإظهار الشمولية الكاملة)
    districts = [
        'المركز (المشنة والظهار)', 'جبلة', 'السدة', 'النادرة', 'العدين', 'حبيش', 'بعدان',
        'السياني', 'ذي السفال', 'يريم', 'الرضمة', 'القفر', 'المخادر', 'حزم العدين', 
        'فرع العدين', 'الشعر', 'السبرة', 'المخادر'
    ]
    
    # 2. توليد التواريخ لآخر 7 أيام مع التركيز على فترة قريبة وفترات أعياد افتراضية
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    timestamps = [start_time + timedelta(seconds=int(np.random.randint(0, int((end_time - start_time).total_seconds())))) 
                  for _ in range(num_records)]
    timestamps.sort()
    
    data = []
    
    for dt in timestamps:
        district = np.random.choice(districts)
        hour = dt.hour
        day_of_week = dt.weekday()
        
        # ضبط ساعات الذروة الحقيقية التي ذكرتها (من 6 مساءً إلى 1 صباحاً)
        # 6 PM (18) to 1 AM (1)
        is_real_peak = (hour >= 18) or (hour <= 1)
        
        # محاكاة الطقس الحقيقي في إب (أعلى درجة 32 وأقلها 15)
        if hour in [12, 13, 14, 15]: # فترة الظهيرة
            temperature = np.random.uniform(26, 32)
        else:
            temperature = np.random.uniform(15, 25)
            
        # بناء المؤشرات بناءً على طبيعة الشبكة (MPLS وكابلات هوائية وأبراج لاسلكية)
        if is_real_peak:
            # ضغط هائل على الأبراج ولواقط هواوي للمشتركين
            mpls_bandwidth_usage_percent = np.random.uniform(85, 99) # استهلاك قريب من الامتلاء
            latency = np.random.uniform(90, 190)                     # زمن استجابة مرتفع (بطء الشبكة)
            packet_loss = np.random.uniform(1.0, 4.5)                # فقدان حزم بسبب الازدحام اللاسلكي
        else:
            # أوقات خارج الذروة (الفجر والظهر)
            mpls_bandwidth_usage_percent = np.random.uniform(20, 60)
            latency = np.random.uniform(15, 50)
            packet_loss = np.random.uniform(0.0, 1.2)
            
        # محاكاة مشكلة الكابلات الممتدة على الأعمدة (تأثر بالرياح أو التضاريس الجبلية)
        # سنضع احتمال عشوائي 2% لحدوث قطع مادي مفاجئ في كابل يربط مديرية بعيدة
        physical_cut = np.random.choice([False, True], p=[0.98, 0.02])
        if physical_cut:
            latency = np.random.uniform(250, 400)
            packet_loss = np.random.uniform(8.0, 25.0) # فقدان حزم كارثي بسبب قطع الكابل
            
        # تطبيق الشروط الذكية لتحديد حالة الشبكة بناءً على المعطيات الجديدة
        if packet_loss > 5.0 or physical_cut:
            status = 'عطل (قطع كابل/برج منفصل)'
        elif mpls_bandwidth_usage_percent > 85.0:
            status = 'ازدحام (ذروة المساء)'
        else:
            status = 'طبيعي'
            
        data.append({
            'Timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'District': district,
            'Hour': hour,
            'DayOfWeek': day_of_week,
            'Latency_ms': round(latency, 2),
            'PacketLoss_Percent': round(packet_loss, 2),
            'MPLS_Bandwidth_Usage_Percent': round(mpls_bandwidth_usage_percent, 2),
            'Temperature_C': round(temperature, 1),
            'Status': status
        })
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"✅ تم تحديث المحاكي الذكي ليعكس واقع شبكة إب الـ 18 مديرية وبروتوكول MPLS!")
    return df

if __name__ == "__main__":
    generate_ibb_real_network_data()