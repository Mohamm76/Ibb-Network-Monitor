# -*- coding: utf-8 -*-
"""
Updated Predictor Module for Ibb MPLS Network
Description: Trains a model based on MPLS bandwidth utilization and real peak hours.
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
        self.data_path = data_path
        self.model = LinearRegression()
        self.r2_score = 0
        self.is_trained = False
        
        if not os.path.exists(self.data_path):
            if os.path.exists("../assets/network_data.csv"):
                self.data_path = "../assets/network_data.csv"

    def train(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError("يرجى تشغيل ملف data_generator.py أولاً لتوليد البيانات الحقيقية.")
            
        df = pd.read_csv(self.data_path)
        
        # الميزات الجديدة المتوافقة مع الواقع
        X = df[['Hour', 'MPLS_Bandwidth_Usage_Percent', 'Temperature_C', 'DayOfWeek']]
        y = df['Latency_ms']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        self.r2_score = r2_score(y_test, y_pred)
        self.is_trained = True
        
        print(f"🚀 تم إعادة تدريب نموذج الـ MPLS بنجاح! R² Score: {self.r2_score:.4f}")
        return self.r2_score

    def predict_custom(self, hour, mpls_usage, temperature, day_of_week):
        if not self.is_trained:
            self.train()
        input_data = np.array([[hour, mpls_usage, temperature, day_of_week]])
        predicted_latency = max(15.0, round(self.model.predict(input_data)[0], 2))
        
        # تحديد الحالة بناءً على المعايير الميدانية المحدثة
        if mpls_usage > 85.0:
            status = 'ازدحام (ذروة المساء)'
        else:
            status = 'طبيعي'
            
        return predicted_latency, status

if __name__ == "__main__":
    predictor = NetworkPredictor()
    predictor.train()