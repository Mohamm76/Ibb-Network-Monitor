# -*- coding: utf-8 -*-
"""
Main Streamlit Application with Secure Environment Variables
Description: Full dynamic dashboard fetching/saving logs via pgAdmin with hidden credentials.
Author: AI Solutions Architect
Date: 2026
"""

import streamlit as tf
import pandas as pd
import numpy as np
import plotly.express as px
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة السرية من ملف .env
load_dotenv()

# 1. إعدادات الصفحة والهوية البصرية لفرع إب
tf.set_page_config(
    page_title="نظام مراقبة شبكة إب الذكي",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# جلب الإعدادات بأمان (إذا لم يجد الملف سيضع قيم افتراضية)
DB_PARAMS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "ibb_telecom_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "root") # القيمة الافتراضية "root" في حال عدم وجود الملف
}

from data_generator import generate_ibb_real_network_data
from predictor import NetworkPredictor

# توليد البيانات الأولية في قاعدة البيانات إذا كانت فارغة عند أول تشغيل
try:
    generate_ibb_real_network_data()
except Exception as e:
    pass

# دالة ذكية لسحب البيانات بشكل لحظي ومباشر من الـ SQL
def fetch_data_from_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        df = pd.read_sql_query("SELECT * FROM network_logs ORDER BY timestamp ASC;", conn)
        conn.close()
        return df
    except Exception as e:
        tf.error(f"❌ فشل الاتصال بقاعدة البيانات PostgreSQL: {e}")
        return pd.DataFrame()

df = fetch_data_from_db()

# تنسيق الواجهة الاحترافي ودعم اللغة العربية (RTL) وتنعيم الحواف
tf.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
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

# تدريب نموذج الذكاء الاصطناعي على البيانات الحالية المستخرجة من الـ SQL
predictor = NetworkPredictor()
r2_score = predictor.train()

# --- الشريط الجانبي للإدخال المباشر في الـ SQL ---
tf.sidebar.markdown("<h3 style='text-align: center; color: #3b82f6;'>⚙️ إدخال القراءات الميدانية (SQL)</h3>", unsafe_allow_html=True)
tf.sidebar.write("---")

input_district = tf.sidebar.selectbox("📍 حدد المديرية النشطة:", list(ibb_coordinates.keys()))
input_hour = tf.sidebar.slider("⏰ ساعة رصد البلاغ:", 0, 23, int(datetime.now().hour))

tf.sidebar.write("📝 **أدخل المؤشرات الحالية (بالأرقام الإنجليزية):**")

raw_mpls = tf.sidebar.text_input("📊 ممر MPLS (%):", value="60.0", help="مثال: 85.5")
raw_loss = tf.sidebar.text_input("⚠️ فقد الحزم (%):", value="0.8", help="مثال: 1.2")
raw_latency = tf.sidebar.text_input("⏱️ الاستجابة (ms):", value="35.0", help="مثال: 120.0")
raw_temp = tf.sidebar.text_input("🌡️ حرارة الموقع (°C):", value="22.0", help="مثال: 28.0")

if tf.sidebar.button("💾 حفظ في قاعدة البيانات فوراً", use_container_width=True):
    try:
        input_mpls = float(raw_mpls.strip()) if raw_mpls.strip() else 60.0
        input_loss = float(raw_loss.strip()) if raw_loss.strip() else 0.8
        input_latency = float(raw_latency.strip()) if raw_latency.strip() else 35.0
        input_temp = float(raw_temp.strip()) if raw_temp.strip() else 22.0
        
        status = 'عطل (قطع كابل/برج منفصل)' if input_loss > 5.0 else ('ازدحام (ذروة المساء)' if input_mpls > 85.0 else 'طبيعي')
        
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        query = """
            INSERT INTO network_logs (timestamp, district, hour, day_of_week, latency_ms, packet_loss_percent, mpls_bandwidth_usage_percent, temperature_c, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (datetime.now(), input_district, input_hour, datetime.now().weekday(), input_latency, input_loss, input_mpls, input_temp, status))
        conn.commit()
        cur.close()
        conn.close()
        
        tf.sidebar.success(f"✅ تم الحفظ بنجاح في pgAdmin!")
        tf.rerun()
        
    except ValueError:
        tf.sidebar.error("❌ يرجى التأكد من كتابة الأرقام بالصيغة الإنجليزية الصحيحة!")
    except Exception as e:
        tf.sidebar.error(f"❌ خطأ أثناء المحاولة: {e}")

# --- الهيدر الرئيسي المطور ---
header_col_title, header_col_logo = tf.columns([5, 1])

with header_col_title:
    tf.markdown("<h2 style='text-align: right; color: #1e3a8a; margin-bottom: 0px;'>مؤسسة الاتصالات اليمنية - فرع محافظة إب</h2>", unsafe_allow_html=True)
    tf.markdown("<h4 style='text-align: right; color: #475569; margin-top: 5px;'>🌐 نظام المراقبة الذكي المرتبط بقاعدة بيانات PostgreSQL</h4>", unsafe_allow_html=True)

with header_col_logo:
    logo_path = r"D:\Desktop\IBB_Network\Ibb_Network_Monitor\assets\telecom_logo.png"
    if os.path.exists(logo_path):
        tf.image(logo_path, width=110)
    else:
        tf.markdown("<div style='text-align: center; padding-top: 15px; color: #94a3b8;'>[Telecom Logo]</div>", unsafe_allow_html=True)

tf.write("---")

if not df.empty:
    col1, col2, col3, col4 = tf.columns(4)
    with col1: 
        tf.markdown(f"<div class='metric-card'><div class='metric-title'>🟢 إجمالي السجلات في SQL</div><div class='metric-value'>{len(df)} سجل</div></div>", unsafe_allow_html=True)
    with col2: 
        tf.markdown(f"<div class='metric-card' style='border-right-color: #3b82f6;'><div class='metric-title'>⚡ متوسط الاستجابة الحالي</div><div class='metric-value'>{df['latency_ms'].mean():.2f} ms</div></div>", unsafe_allow_html=True)
    with col3: 
        tf.markdown(f"<div class='metric-card' style='border-right-color: #f59e0b;'><div class='metric-title'>📊 متوسط استهلاك MPLS</div><div class='metric-value'>{df['mpls_bandwidth_usage_percent'].mean():.1f} %</div></div>", unsafe_allow_html=True)
    with col4: 
        tf.markdown(f"<div class='metric-card' style='border-right-color: #ef4444;'><div class='metric-title'>🚨 الإنذارات النشطة بـ pgAdmin</div><div class='metric-value'>{len(df[df['status'] != 'طبيعي'])} إنذار</div></div>", unsafe_allow_html=True)

tf.subheader("📍 خريطة الحالة الجغرافية التفاعلية المستمدة من PostgreSQL")

map_data = []
if not df.empty:
    for d, coords in ibb_coordinates.items():
        district_data = df[df['district'] == d]
        if not district_data.empty:
            latest = district_data.iloc[-1]
            map_data.append({
                'المديرية': d, 'Latitude': coords[0], 'Longitude': coords[1],
                'الحالة': latest['status'], 'زمن الاستجابة': f"{latest['latency_ms']} ms",
                'استهلاك MPLS': f"{latest['mpls_bandwidth_usage_percent']}%", 
                'حجم العقدة': latest['mpls_bandwidth_usage_percent'] + 20
            })

if map_data:
    fig_map = px.scatter_mapbox(
        pd.DataFrame(map_data), lat="Latitude", lon="Longitude", color="الحالة", size="حجم العقدة",
        hover_name="المديرية", hover_data={"زمن الاستجابة": True, "استهلاك MPLS": True, "حجم العقدة": False, "Latitude": False, "Longitude": False},
        color_discrete_map={'طبيعي': '#10b981', 'ازدحام (ذروة المساء)': '#f59e0b', 'عطل (قطع كابل/برج منفصل)': '#ef4444'},
        zoom=9.3, height=420
    )
    fig_map.update_layout(
        mapbox_style="carto-positron", 
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(title_text="دليل جودة الخدمة", yanchor="top", y=0.98, xanchor="right", x=0.99)
    )
    tf.plotly_chart(fig_map, use_container_width=True)

tf.write("---")
tf.markdown(f"<h3 style='color: #1e3a8a;'>🔮 التحليل التنبؤي الذكي للمديرية النشطة: ({input_district})</h3>", unsafe_allow_html=True)

try:
    p_hour = int(input_hour)
    p_mpls = float(raw_mpls.strip()) if raw_mpls.strip() else 60.0
    p_temp = float(raw_temp.strip()) if raw_temp.strip() else 22.0
    
    pred_lat, pred_status = predictor.predict_custom(p_hour, p_mpls, p_temp, datetime.now().weekday())
    
    p_col1, p_col2 = tf.columns(2)
    with p_col1:
        tf.markdown(f"""
        <div class='prediction-box'>
            <h4>📊 مؤشرات التنبؤ الرياضية المستهدفة:</h4>
            <p>⏱️ <b>الاستجابة المتوقعة (Latency):</b> {pred_lat} ms</p>
            <p>📡 <b>ضغط حزمة الـ MPLS المفترض:</b> {p_mpls} %</p>
            <p>🌡️ <b>درجة الحرارة المتوقعة بالموقع:</b> {p_temp} °C</p>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        tf.markdown(f"<h4>🚨 الحالة التشغيلية المتوقعة للشبكة:</h4>", unsafe_allow_html=True)
        if 'طبيعي' in pred_status: 
            tf.success(f"🟢 الحالة المستنتجة: {pred_status}")
        elif 'ازدحام' in pred_status: 
            tf.warning(f"🟡 الحالة المستنتجة: {pred_status}")
        else: 
            tf.error(f"🔴 الحالة المستنتجة: {pred_status}")
            
    tf.caption(f"🎯 دقة النموذج الحالي: R² = {r2_score:.4f}")
except Exception as e:
    pass