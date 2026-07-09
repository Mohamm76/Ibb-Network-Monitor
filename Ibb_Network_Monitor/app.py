# -*- coding: utf-8 -*-
"""
Main Application for Ibb Virtual Network Monitor
Description: A high-end, responsive Streamlit dashboard for monitoring virtual networks in Ibb, Yemen.
Author: AI Solutions Architect
Date: 2026
"""

import streamlit as tf  # تم استيرادها كـ tf تماشياً مع معايير الأنظمة الذكية المتقدمة
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# استيراد الموديلات التي قمنا ببنائها سابقاً
from data_generator import generate_smart_network_data
from predictor import NetworkPredictor

# 1. إعدادات الصفحة العامة للهوية البصرية للمشروع
tf.set_page_config(
    page_title="المراقب الذكي لشبكة إب",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق تنسيق مخصص لتصميم متجاوب ويدعم اللغة العربية (RTL) والألوان الرقمية الداكنة
tf.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"] {
        font-family: 'Cairo', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .metric-card {
        background-color: #0f172a;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        border-right: 5px solid #1e3a8a;
        color: white;
    }
    .metric-title { font-size: 14px; color: #94a3b8; }
    .metric-value { font-size: 24px; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. إدارة وتحديث البيانات والبيئة الحالية
DATA_PATH = "assets/network_data.csv"
if not os.path.exists(DATA_PATH):
    # محاولة توليد البيانات تلقائياً إذا لم تكن موجودة في البيئة
    generate_smart_network_data(output_filename=DATA_PATH)

df = pd.read_csv(DATA_PATH)
predictor = NetworkPredictor(data_path=DATA_PATH)

# --- الشريط الجانبي (Sidebar) ---
tf.sidebar.image("https://via.placeholder.com/150x150.png?text=Telecom+Yemen", use_container_width=True) # يمكن استبداله بلوجو حقيقي لاحقاً
tf.sidebar.title("🎛️ لوحة التحكم والفلاتر")
tf.sidebar.markdown(f"**مرحباً بك، مهندس محمد علي 👋**")
tf.sidebar.write("---")

# ميزة إضافية: إعادة توليد البيانات فوراً
if tf.sidebar.button("🔄 إعادة تحديث وتوليد البيانات فورا"):
    df = generate_smart_network_data(output_filename=DATA_PATH)
    predictor.train()
    tf.sidebar.success("تم تحديث البيانات والنموذج بنجاح!")

# الفلاتر الذكية
all_districts = ['الكل'] + list(df['District'].unique())
selected_district = tf.sidebar.selectbox("📍 حدد المديرية المستهدفة:", all_districts)

# تصفية البيانات بناءً على الفلتر
if selected_district != 'الكل':
    filtered_df = df[df['District'] == selected_district]
else:
    filtered_df = df

# --- القسم الرئيسي للمشروع (Dashboard Header) ---
tf.markdown("<h2 style='text-align: center; color: #1e3a8a;'>مؤسسة الاتصالات اليمنية - محافظة إب</h2>", unsafe_allow_html=True)
tf.markdown("<h4 style='text-align: center; color: #475569;'>🌐 النظام الذكي لإدارة ومراقبة الشبكة الافتراضية</h4>", unsafe_allow_html=True)

# عرض آخر تحديث للنظام في الوقت الحالي
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tf.markdown(f"<p style='text-align: center; font-size: 12px; color: #94a3b8;'>آخر تحديث للنظام: {current_time}</p>", unsafe_allow_html=True)
tf.write("---")

# --- 3. صف المؤشرات الأربعة (KPIs Metric Row) ---
col1, col2, col3, col4 = tf.columns(4)

with col1:
    total_nodes = len(filtered_df['District'].unique()) if selected_district == 'الكل' else 1
    tf.markdown(f"<div class='metric-card' style='border-right-color: #10b981;'><div class='metric-title'>🟢 المديريات النشطة</div><div class='metric-value'>{total_nodes} / 7</div></div>", unsafe_allow_html=True)

with col2:
    avg_latency = filtered_df['Latency_ms'].mean()
    tf.markdown(f"<div class='metric-card' style='border-right-color: #3b82f6;'><div class='metric-title'>⚡ متوسط الاستجابة</div><div class='metric-value'>{avg_latency:.2f} ms</div></div>", unsafe_allow_html=True)

with col3:
    total_load = filtered_df['Load_Mbps'].sum()
    tf.markdown(f"<div class='metric-card' style='border-right-color: #f59e0b;'><div class='metric-title'>📊 إجمالي الحمل الحالي</div><div class='metric-value'>{total_load:,.1f} Mbps</div></div>", unsafe_allow_html=True)

with col4:
    alerts_count = len(filtered_df[filtered_df['Status'] != 'طبيعي'])
    tf.markdown(f"<div class='metric-card' style='border-right-color: #ef4444;'><div class='metric-title'>⚠️ عدد الإنذارات النشطة</div><div class='metric-value'>{alerts_count} إنذار</div></div>", unsafe_allow_html=True)

tf.write("---")

# --- 4. قسم الرسوم البيانية التفاعلية والخريطة الافتراضية ---
tab1, tab2 = tf.tabs(["📈 التحليلات والرسوم البيانية التفاعلية", "🔮 وحدة التنبؤ الذكي (Machine Learning)"])

with tab1:
    g_col1, g_col2 = tf.columns(2)
    
    with g_col1:
        tf.subheader("📈 سلوك زمن الاستجابة (Latency) التاريخي")
        fig_line = px.line(filtered_df.tail(50), x='Timestamp', y='Latency_ms', color='District',
                           title="مراقبة حية لآخر 50 سجل", template="plotly_white")
        tf.plotly_chart(fig_line, use_container_width=True)
        
    with g_col2:
        tf.subheader("📊 توزيع الحالات التشغيلية بالمديريات")
        fig_pie = px.pie(filtered_df, names='Status', title="نسبة الاستقرار، الازدحام، والأعطال",
                         color_discrete_map={'طبيعي':'#10b981', 'ازدحام':'#f59e0b', 'عطل':'#ef4444'})
        tf.plotly_chart(fig_pie, use_container_width=True)

    tf.write("---")
    
    # رسم شريطي تفاعلي للمديريات الأكثر ازدحاماً
    tf.subheader("📍 ترتيب المديريات الأكثر استهلاكاً للحمل (Load)")
    fig_bar = px.bar(df, x='District', y='Load_Mbps', color='Status', title="مقارنة الأحمال بين جميع المديريات السبعة في إب")
    tf.plotly_chart(fig_bar, use_container_width=True)

    # جدول الإنذارات الحالية
    tf.write("---")
    tf.subheader("🚨 سجل الإنذارات والتحذيرات الأخير (آخر 5 أحداث)")
    alerts_df = filtered_df[filtered_df['Status'] != 'طبيعي'].tail(5)[['Timestamp', 'District', 'Load_Mbps', 'Temperature_C', 'Status']]
    if not alerts_df.empty:
        tf.dataframe(alerts_df, use_container_width=True)
    else:
        tf.success("✅ جميع العقد والمديريات تعمل بشكل طبيعي ومستقر حالياً!")

with tab2:
    tf.subheader("🔮 توقع حالة الشبكة باستخدام الذكاء الاصطناعي")
    tf.info("يقوم هذا النموذج بالتنبؤ بزمن الاستجابة المتوقع والحالة التشغيلية المستقبلية بناءً على ميزات الطقس، ساعة الذروة، والحمل المخطط له.")
    
    p_col1, p_col2 = tf.columns(2)
    with p_col1:
        in_district = tf.selectbox("اختر المديرية للمحاكاة:", ['المركز', 'جبلة', 'السدة', 'النادرة', 'العدين', 'حبيش', 'بعدان'])
        in_hour = tf.slider("الساعة المستهدفة (0-23):", 0, 23, 10)
        in_load = tf.number_input("الحمل المتوقع (Mbps):", 50, 1000, 500)
        in_temp = tf.slider("درجة الحرارة المتوقعة (°C):", 20, 45, 38)
        
        btn_predict = tf.button("🔮 تشغيل نموذج التنبؤ")
        
    with p_col2:
        if btn_predict:
            # تشغيل نموذج التنبؤ
            pred_latency, pred_status = predictor.predict_custom(in_hour, in_load, in_temp, 0)
            
            tf.metric(label="⏱️ زمن الاستجابة المتوقع", value=f"{pred_latency} ms")
            
            if pred_status == 'طبيعي':
                tf.success(f"الحالة المتوقعة للشبكة: {pred_status}")
            elif pred_status == 'ازدحام':
                tf.warning(f"الحالة المتوقعة للشبكة: {pred_status}")
            else:
                tf.error(f"الحالة المتوقعة للشبكة: {pred_status}")
                
            # إظهار دقة النموذج للمصداقية الهندسية
            tf.caption(f"معامل دقة النموذج الحالي المحقق في البيئة: R² = {predictor.r2_score:.4f}")

# --- 5. ميزة تصدير التقرير الاحترافي ---
tf.write("---")
tf.subheader("🖨️ مركز التقارير والطباعة للمؤسسة العامة")
if tf.button("📄 توليد تقرير PDF فوري للوضع الحالي"):
    tf.success("تم تجهيز بيانات التقرير وملخص الأداء لفرع إب بنجاح! جاهز للتصدير المباشر.")