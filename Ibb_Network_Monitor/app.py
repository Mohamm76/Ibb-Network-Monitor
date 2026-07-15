# -*- coding: utf-8 -*-
"""
Main Application for Ibb MPLS & Wireless Network Monitor
Description: Ultra-flexible UI with dynamic district selection and enhanced Mapbox styling.
Author: AI Solutions Architect
Date: 2026
"""

import streamlit as tf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import os

# استيراد الموديلات
from data_generator import generate_ibb_real_network_data
from predictor import NetworkPredictor

# 1. إعدادات الصفحة والهوية البصرية لفرع إب
tf.set_page_config(
    page_title="نظام مراقبة شبكة إب الذكي",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق التنسيق الاحترافي المتجاوب (RTL) وتنعيم الحواف
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
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-right: 5px solid #1e3a8a;
        color: white;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 13px; color: #94a3b8; font-weight: bold; }
    .metric-value { font-size: 22px; font-weight: bold; margin-top: 5px; color: #f8fafc; }
    
    .prediction-box {
        background-color: #1e293b;
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 18px;
        margin-top: 10px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

DATA_PATH = "assets/network_data.csv"
if not os.path.exists(DATA_PATH):
    generate_ibb_real_network_data(output_filename=DATA_PATH)

@tf.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# إحداثيات المديريات الـ 18 بمحافظة إب
ibb_coordinates = {
    'المركز (المشنة والظهار)': [13.9734, 44.1724], 'جبلة': [13.9219, 44.1481],
    'السدة': [14.1803, 44.3312], 'النادرة': [14.1311, 44.4015],
    'العدين': [13.9625, 43.9614], 'حبيش': [14.1221, 44.1205],
    'بعدان': [13.9912, 44.2721], 'السياني': [13.8214, 44.2012],
    'ذي السفال': [13.7823, 44.1314], 'يريم': [14.2985, 44.3776],
    'الرضمة': [14.2215, 44.5312], 'القفر': [14.2512, 44.1014],
    'المخادر': [14.1114, 44.2125], 'حزم العدين': [14.0512, 43.8912],
    'فرع العدين': [13.9125, 43.7814], 'الشعر': [14.0514, 44.3812],
    'السبرة': [13.8912, 44.3314]
}

# تدريب النموذج
predictor = NetworkPredictor(data_path=DATA_PATH)
r2_score = predictor.train()

# --- 2. الشريط الجانبي المطور مع التحديد التفاعلي لأي مديرية ---
tf.sidebar.markdown("<h3 style='text-align: center; color: #3b82f6;'>⚙️ إدخال القراءات الميدانية</h3>", unsafe_allow_html=True)
tf.sidebar.write("---")

# اختيار المديرية المستهدفة (التحكم ديناميكي بالكامل)
input_district = tf.sidebar.selectbox("📍 حدد المديرية النشطة:", list(ibb_coordinates.keys()), index=0)
input_hour = tf.sidebar.slider("⏰ ساعة رصد البلاغ (0-23):", 0, 23, int(datetime.now().hour))

col_side1, col_side2 = tf.sidebar.columns(2)
with col_side1:
    input_mpls = tf.number_input("📊 ممر MPLS (%):", 0.0, 100.0, 60.0, step=5.0)
    input_temp = tf.number_input("🌡️ حرارة الموقع (°C):", 15.0, 32.0, 22.0, step=1.0)
with col_side2:
    input_loss = tf.number_input("⚠️ فقد الحزم (%):", 0.0, 50.0, 0.8, step=0.1)
    input_latency = tf.number_input("⏱️ الاستجابة (ms):", 10.0, 500.0, 35.0, step=5.0)

# حفظ وإعادة تشغيل فوري
if tf.sidebar.button("💾 تحديث وحفظ البيانات فوراً", use_container_width=True):
    if input_loss > 5.0:
        calculated_status = 'عطل (قطع كابل/برج منفصل)'
    elif input_mpls > 85.0:
        calculated_status = 'ازدحام (ذروة المساء)'
    else:
        calculated_status = 'طبيعي'
        
    new_row = {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'District': input_district,
        'Hour': input_hour,
        'DayOfWeek': datetime.now().weekday(),
        'Latency_ms': round(input_latency, 2),
        'PacketLoss_Percent': round(input_loss, 2),
        'MPLS_Bandwidth_Usage_Percent': round(input_mpls, 2),
        'Temperature_C': round(input_temp, 1),
        'Status': calculated_status
    }
    
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    updated_df.to_csv(DATA_PATH, index=False, encoding='utf-8-sig')
    
    tf.cache_data.clear()
    tf.success(f"✅ تم تحديث بيانات مديرية {input_district} بنجاح!")
    tf.rerun()

# زري التوليد السريع
if tf.sidebar.button("🔄 إعادة بناء المحاكاة بالكامل", use_container_width=True):
    generate_ibb_real_network_data(output_filename=DATA_PATH)
    tf.cache_data.clear()
    tf.rerun()

# --- 3. الواجهة الرسومية ومؤشرات الأداء ---
tf.markdown("<h2 style='text-align: center; color: #1e3a8a;'>مؤسسة الاتصالات اليمنية - فرع محافظة إب</h2>", unsafe_allow_html=True)
tf.markdown("<h4 style='text-align: center; color: #475569;'>🌐 النظام المطور لإدارة ومراقبة شبكات الـ MPLS والبث اللاسلكي الفوق أرضي</h4>", unsafe_allow_html=True)
tf.write("---")

col1, col2, col3, col4 = tf.columns(4)
with col1:
    tf.markdown(f"<div class='metric-card' style='border-right-color: #10b981;'><div class='metric-title'>🟢 مديريات تحت التغطية</div><div class='metric-value'>{len(df['District'].unique())} مديرية</div></div>", unsafe_allow_html=True)
with col2:
    tf.markdown(f"<div class='metric-card' style='border-right-color: #3b82f6;'><div class='metric-title'>⚡ متوسط الاستجابة العام</div><div class='metric-value'>{df['Latency_ms'].mean():.2f} ms</div></div>", unsafe_allow_html=True)
with col3:
    tf.markdown(f"<div class='metric-card' style='border-right-color: #f59e0b;'><div class='metric-title'>📊 متوسط استهلاك حزمة MPLS</div><div class='metric-value'>{df['MPLS_Bandwidth_Usage_Percent'].mean():.1f} %</div></div>", unsafe_allow_html=True)
with col4:
    active_alerts = len(df[df['Status'] != 'طبيعي'])
    tf.markdown(f"<div class='metric-card' style='border-right-color: #ef4444;'><div class='metric-title'>🚨 إنذارات الأبراج النشطة</div><div class='metric-value'>{active_alerts} إنذار</div></div>", unsafe_allow_html=True)

# --- 4. ترقية الخريطة التفاعلية الجغرافية لمحافظة إب ---
tf.subheader("📍 خريطة الحالة الجغرافية التفاعلية (أبراج ومسارات إب)")

map_data = []
for d, coords in ibb_coordinates.items():
    district_data = df[df['District'] == d]
    if not district_data.empty:
        latest = district_data.iloc[-1]
        status = latest['Status']
        latency = latest['Latency_ms']
        mpls_usage = latest['MPLS_Bandwidth_Usage_Percent']
        loss = latest['PacketLoss_Percent']
        temp = latest['Temperature_C']
    else:
        status = 'طبيعي'
        latency = 25.0
        mpls_usage = 40.0
        loss = 0.5
        temp = 22.0
        
    map_data.append({
        'المديرية': d,
        'Latitude': coords[0],
        'Longitude': coords[1],
        'الحالة': status,
        'زمن الاستجابة': f"{latency} ms",
        'استهلاك MPLS': f"{mpls_usage}%",
        'فقدان الحزم': f"{loss}%",
        'درجة الحرارة': f"{temp}°C",
        'حجم العقدة': mpls_usage + 20 # جعل الحجم مرئي حتى مع الاستهلاك المنخفض
    })

map_df = pd.DataFrame(map_data)

# بناء الخريطة بنمط Carto Positron الجذاب والاحترافي
fig_map = px.scatter_mapbox(
    map_df,
    lat="Latitude",
    lon="Longitude",
    color="الحالة",
    size="حجم العقدة",
    hover_name="المديرية",
    hover_data={
        "زمن الاستجابة": True,
        "استهلاك MPLS": True,
        "فقدان الحزم": True,
        "درجة الحرارة": True,
        "حجم العقدة": False,
        "Latitude": False,
        "Longitude": False
    },
    color_discrete_map={
        'طبيعي': '#10b981', 
        'ازدحام (ذروة المساء)': '#f59e0b', 
        'عطل (قطع كابل/برج منفصل)': '#ef4444'
    },
    zoom=9.3,
    height=450
)

# تحديث المظهر الخارجي وتنسيق التفاصيل البصرية للخريطة
fig_map.update_layout(
    mapbox_style="carto-positron", 
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(
        title_text="دليل حالة المواقع",
        yanchor="top",
        y=0.98,
        xanchor="right",
        x=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)"
    )
)
tf.plotly_chart(fig_map, use_container_width=True)

tf.write("---")

# --- 5. قسم التنبؤ الفوري والمؤتمت لأي مديرية مستهدفة ---
tf.markdown(f"<h3 style='color: #1e3a8a;'>🔮 التنبؤ الذكي وتحليل جودة الخدمة لمديرية: ({input_district})</h3>", unsafe_allow_html=True)
tf.write(f"يقوم النموذج الآن بتحليل البيانات التاريخية واليدوية المسجلة لمديرية **{input_district}** ليتوقع سلوك الشبكة:")

# استخدام نموذج الـ Machine Learning للتنبؤ بالقيم
pred_lat, pred_status = predictor.predict_custom(input_hour, input_mpls, input_temp, datetime.now().weekday())

p_col1, p_col2 = tf.columns(2)
with p_col1:
    tf.markdown(f"""
    <div class='prediction-box'>
        <h4>📊 مؤشرات البرج المتوقعة في {input_district}:</h4>
        <p>⏱️ <b>زمن الاستجابة المتوقع (Latency):</b> {pred_lat} ms</p>
        <p>🌡️ <b>درجة الحرارة المحددة:</b> {input_temp} °C</p>
        <p>📡 <b>نسبة استهلاك حزمة MPLS:</b> {input_mpls} %</p>
    </div>
    """, unsafe_allow_html=True)

with p_col2:
    tf.markdown(f"<h4>🚨 الحالة المتوقعة لشبكة {input_district}:</h4>", unsafe_allow_html=True)
    if 'طبيعي' in pred_status:
        tf.success(f"🟢 الحالة المتوقعة: طبيعي - الأداء مستقر وممتاز على مستوى المديرية بالكامل.")
    elif 'ازدحام' in pred_status:
        tf.warning(f"🟡 الحالة المتوقعة: ازدحام (ذروة المساء) - يتوقع تأثر سرعة المشتركين محلياً.")
    else:
        tf.error(f"🔴 الحالة المتوقعة: عطل / إنذار حرج - هناك اشتباه عالي بحدوث انقطاع للكابل الهوائي.")

tf.caption(f"🎯 دقة تدريب النموذج اللحظي بعد تضمين قراءات {input_district} الحالية: R² = {r2_score:.4f}")