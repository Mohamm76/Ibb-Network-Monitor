# -*- coding: utf-8 -*-
"""
Network Predictive Analytics Module using Hidden Environment Credentials
Description: Connects to PostgreSQL, extracts telemetry logs, trains a Random Forest Model.
Author: AI Solutions Architect
Date: 2026
"""

import os
import pandas as pd
import numpy as np
import psycopg2
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class NetworkPredictor:
    def __init__(self):
        # مصفوفة الاتصال الآمنة والمنفصلة تماماً عن الأكواد الظاهرة
        self.db_params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "ibb_telecom_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "root")
        }
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def train(self):
        """سحب البيانات التاريخية من pgAdmin وتدريب نموذج الذكاء الاصطناعي برمجياً"""
        try:
            conn = psycopg2.connect(**self.db_params)
            # جلب الأعمدة الرقمية الهامة لعمليات التحليل الرياضي والتنبؤ
            df = pd.read_sql_query("SELECT hour, day_of_week, mpls_bandwidth_usage_percent, temperature_c, latency_ms FROM network_logs;", conn)
            conn.close()
            
            if df.empty or len(df) < 10:
                return 0.0
                
            # فصل المتغيرات المستقلة (X) عن الهدف المراد التنبؤ به وهو زمن الاستجابة (y)
            X = df[['hour', 'day_of_week', 'mpls_bandwidth_usage_percent', 'temperature_c']]
            y = df['latency_ms']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_test_split=0.2, random_state=42)
            
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # حساب دقة النموذج الرياضية للتأكد من جودة اتخاذ القرار
            r2_score = self.model.score(X_test, y_test)
            return float(r2_score)
            
        except Exception as e:
            print(f"⚠️ Prediction pipeline warning: {e}")
            return 0.0
            
    def predict_custom(self, hour, mpls_usage, temp, day_of_week):
        """التنبؤ اللحظي والذكي بناءً على مدخلات لوحة التحكم الحالية"""
        if not self.is_trained:
            # معايير افتراضية في حال عدم اكتمال تدريب النموذج التنبؤي
            fallback_lat = round(30.0 + (mpls_usage * 0.95), 2)
            status = 'ازدحام (ذروة المساء)' if mpls_usage > 85.0 else 'طبيعي'
            return fallback_lat, status
            
        # تجهيز المصفوفة المدخلة وتمريرها للمشغل الإحصائي
        input_data = np.array([[hour, day_of_week, mpls_usage, temp]])
        predicted_latency = round(float(self.model.predict(input_data)[0]), 2)
        
        # تصنيف الحالة المتوقعة بناءً على حسابات الاحتمالات
        if mpls_usage > 85.0:
            status = 'ازدحام (ذروة المساء)'
        elif predicted_latency > 130.0:
            status = 'عطل (قطع كابل/برج منفصل)'
        else:
            status = 'طبيعي'
            
        return predicted_latency, status