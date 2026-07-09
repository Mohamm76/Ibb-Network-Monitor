# -*- coding: utf-8 -*-
"""
Predictor Module for Ibb Virtual Network Monitor
Description: Trains a Machine Learning model and explores data before training.
Author: AI Solutions Architect
Date: 2026
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import os

class NetworkPredictor:
    def __init__(self, data_path="assets/network_data.csv"):
        """
        تهيئة كلاس التنبؤ مع فحص تلقائي للمسارات في البيئة الحالية.
        """
        self.data_path = data_path
        self.model = LinearRegression()
        self.r2_score = 0
        self.is_trained = False
        
        # التأكد ديناميكياً من المسار الصحيح حسب مكان التشغيل الحالي
        if not os.path.exists(self.data_path):
            if os.path.exists("../assets/network_data.csv"):
                self.data_path = "../assets/network_data.csv"
            elif os.path.exists("Ibb_Network_Monitor/assets/network_data.csv"):
                self.data_path = "Ibb_Network_Monitor/assets/network_data.csv"

    def explore_data(self):
        """
        ميزة احترافية: استكشاف واطلاع على البيانات قبل بدء التدريب
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف البيانات. يرجى تشغيل data_generator.py أولاً.")
            
        df = pd.read_csv(self.data_path)
        
        print("\n" + "="*50)
        print("📊 [خطوة الاستكشاف] نظرة عامة على أول 5 سجلات في البيانات:")
        print("="*50)
        print(df.head())
        
        print("\n" + "="*50)
        print("📈 [خطوة الإحصاء] التحليل الإحصائي للمؤشرات (KPIs):")
        print("="*50)
        print(df[['Latency_ms', 'PacketLoss_Percent', 'Load_Mbps', 'Temperature_C']].describe())
        
        print("\n" + "="*50)
        print("🔄 [توزيع الحالات] عدد السجلات لكل حالة شبكة في إب:")
        print("="*50)
        print(df['Status'].value_counts())
        print("="*50 + "\n")
        
        return df

    def train(self):
        """
        تدريب النموذج بناءً على الميزات الحالية.
        """
        # استدعاء دالة الاطلاع على البيانات أولاً
        df = self.explore_data()
        
        # تحديد الميزات (X) والهدف (y)
        X = df[['Hour', 'Load_Mbps', 'Temperature_C', 'DayOfWeek']]
        y = df['Latency_ms']
        
        # تقسيم البيانات إلى تدريب واختبار
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # تدريب النموذج
        self.model.fit(X_train, y_train)
        
        # حساب معامل الدقة R² Score
        y_pred = self.model.predict(X_test)
        self.r2_score = r2_score(y_test, y_pred)
        self.is_trained = True
        
        print(f"🚀 تم تدريب النموذج بنجاح في البيئة الحالية!")
        print(f"🎯 معامل الدقة المحقق (R² Score): {self.r2_score:.4f}\n")
        return self.r2_score

    def predict_custom(self, hour, load, temperature, day_of_week):
        if not self.is_trained:
            self.train()
        input_data = np.array([[hour, load, temperature, day_of_week]])
        predicted_latency = max(20.0, round(self.model.predict(input_data)[0], 2))
        
        # تحديد الحالة منطقياً
        if load > 450 and temperature > 35:
            status = 'ازدحام'
        else:
            status = 'طبيعي'
            
        return predicted_latency, status

if __name__ == "__main__":
    # تشغيل الفحص والتدريب مباشرة
    predictor = NetworkPredictor()
    predictor.train()