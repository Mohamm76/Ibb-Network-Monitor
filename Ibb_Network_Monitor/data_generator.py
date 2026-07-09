# -*- coding: utf-8 -*-
"""
Data Generator for Ibb Virtual Network Monitor
Description: Generates realistic, smart network performance metrics for 7 districts in Ibb, Yemen.
Author: AI Solutions Architect
Date: 2026
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_smart_network_data(num_records=500, output_filename="assets/network_data.csv"):
    """
    توليد بيانات شبكة افتراضية ذكية لمديريات محافظة إب بناءً على شروط منطقية وساعات الذروة.
    """
    np.random.seed(42)  # لضمان ثبات البيانات عند كل تشغيل
    
    # 1. المديريات السبعة المحددة في إب
    districts = ['المركز', 'جبلة', 'السدة', 'النادرة', 'العدين', 'حبيش', 'بعدان']
    
    # 2. توليد التواريخ والأوقات لآخر 7 أيام
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    # توليد طابع زمني عشوائي بين البداية والنهاية
    timestamps = [start_time + timedelta(seconds=int(np.random.randint(0, int((end_time - start_time).total_seconds())))) 
                  for _ in range(num_records)]
    # فرز التواريخ تصاعدياً لجعل الجدول منطقياً
    timestamps.sort()
    
    data = []
    
    for dt in timestamps:
        district = np.random.choice(districts)
        hour = dt.hour
        day_of_week = dt.weekday() # 0 = الإثنين، 6 = الأحد
        
        # 3. محاكاة أوقات الذروة (10 صباحاً و 6 مساءً) والطقس في إب
        # في أوقات الذروة يرتفع الحمل وتزيد الحرارة طردياً مع استهلاك الأجهزة
        is_peak = hour in [10, 11, 18, 19]
        
        if is_peak:
            load = np.random.uniform(400, 600)          # حمل عالٍ بالـ Mbps
            temperature = np.random.uniform(32, 42)    # حرارة مرتفعة بسبب الضغط
            latency = np.random.uniform(80, 150)       # زمن استجابة أعلى
            packet_loss = np.random.uniform(1.5, 5.0)  # فقدان حزم أعلى
        else:
            load = np.random.uniform(50, 400)          # حمل طبيعي ليل خارجي أو فجر
            temperature = np.random.uniform(25, 33)    # أجواء إب المعتدلة
            latency = np.random.uniform(20, 80)
            packet_loss = np.random.uniform(0.0, 2.5)
            
        # 4. تطبيق الشروط الذكية لتحديد حالة الشبكة (القواعد البرمجية المستهدفة)
        # قاعدة 1: إذا كان فقدان الحزم > 3% -> عطل مباشر (بسبب انقطاع مادي أو مشكلة بالخطوط)
        if packet_loss > 3.0:
            status = 'عطل'
        # قاعدة 2: إذا كان الحمل > 450 والحرارة > 35 -> ازدحام ناتج عن الضغط العالي
        elif load > 450 and temperature > 35:
            status = 'ازدحام'
        # خلاف ذلك الحالة مستقرة وطبيعية
        else:
            status = 'طبيعي'
            
        data.append({
            'Timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'District': district,
            'Hour': hour,
            'DayOfWeek': day_of_week,
            'Latency_ms': round(latency, 2),
            'PacketLoss_Percent': round(packet_loss, 2),
            'Load_Mbps': round(load, 2),
            'Temperature_C': round(temperature, 1),
            'Status': status
        })
        
    # تحويل البيانات إلى DataFrame وحفظها
    df = pd.DataFrame(data)
    
    # التأكد من وجود مجلد assets قبل الحفظ
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"✅ تم توليد {num_records} سجل ذكي بنجاح وحفظهم في {output_filename}")
    return df

if __name__ == "__main__":
    # تشغيل الملف منفصلاً لاختبار التوليد
    generate_smart_network_data()