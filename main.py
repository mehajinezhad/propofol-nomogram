import matplotlib
matplotlib.use("Agg")  # بسیار مهم: باید قبل از import pyplot باشد

import matplotlib.pyplot as plt
import numpy as np
import io
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "Go to /generate-nomogram"}

@app.get("/generate-nomogram")
def generate_nomogram():
    # ==========================================
    # تنظیمات اولیه نمودار
    # ==========================================
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.set_xlim(-2, 17)
    ax.set_ylim(0, 22)
    ax.axis('off')  # حذف محورهای پیش‌فرض

    # مشخصات هندسی
    L = 15  # فاصله افقی بین محور چپ و راست
    y_min = 2
    y_max = 18
    height = y_max - y_min

    # توابع تبدیل مقیاس لگاریتمی
    def get_y_weight(w):
        log_w = np.log10(w)
        log_min = np.log10(0.5)
        log_max = np.log10(200)
        return y_min + (log_w - log_min) / (log_max - log_min) * height

    def get_y_pump(p):
        log_p = np.log10(p)
        log_min = np.log10(0.5)
        log_max = np.log10(400)
        return y_min + (log_p - log_min) / (log_max - log_min) * height

    # ==========================================
    # ۱. رسم محور چپ (وزن)
    # ==========================================
    ax.plot([0, 0], [y_min, y_max], color='#1f4e79', linewidth=4)
    weights = [0.5, 1, 2, 5, 10, 20, 30, 50, 70, 100, 150, 200]
    for w in weights:
        y = get_y_weight(w)
        ax.plot([0, -0.3], [y, y], color='#1f4e79', linewidth=2)
        ax.text(-0.5, y, str(w), ha='right', va='center', fontsize=11, color='#1f4e79', fontweight='bold')

    ax.text(0, y_max + 1, "Patient Weight\n(kg)", ha='center', va='bottom', fontsize=12, color='#1f4e79', fontweight='bold', bbox=dict(facecolor='#e6f0fa', edgecolor='#1f4e79', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۲. رسم محور راست (سرعت پمپ)
    # ==========================================
    ax.plot([L, L], [y_min, y_max], color='#7030a0', linewidth=4)
    pumps = [0.5, 1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400]
    for p in pumps:
        y = get_y_pump(p)
        ax.plot([L, L + 0.3], [y, y], color='#7030a0', linewidth=2)
        ax.text(L + 0.5, y, str(p), ha='left', va='center', fontsize=11, color='#7030a0', fontweight='bold')

    ax.text(L, y_max + 1, "Pump Rate\n(mL/h)", ha='center', va='bottom', fontsize=12, color='#7030a0', fontweight='bold', bbox=dict(facecolor='#f3e6fa', edgecolor='#7030a0', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۳. رسم محور مورب (دوز)
    # ==========================================
    y_W_max = get_y_weight(200)
    y_P_min = get_y_pump(0.5)
    y_W_10 = get_y_weight(10)

    ax.plot([0, L], [y_W_max, y_P_min], color='#2e7d32', linewidth=3)
    doses = [0.1, 0.2, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12]
    dose_coords = {}

    for d in doses:
        y_P_d = get_y_pump(d)
        m1 = (y_P_min - y_W_max) / L
        m2 = (y_P_d - y_W_10) / L
        x_int = (y_W_10 - y_W_max) / (m1 - m2)
        y_int = m1 * x_int + y_W_max
        dose_coords[d] = (x_int, y_int)
        
        ax.plot(x_int, y_int, 'o', color='#2e7d32', markersize=6)
        ha = 'right' if d < 1 else 'left'
        offset = -0.3 if d < 1 else 0.3
        ax.text(x_int + offset, y_int, str(d), ha=ha, va='center', fontsize=11, color='#2e7d32', fontweight='bold')

    ax.text(L/2, y_max + 1, "Propofol Dose\n(mg/kg/h)", ha='center', va='bottom', fontsize=12, color='#2e7d32', fontweight='bold', bbox=dict(facecolor='#e8f5e9', edgecolor='#2e7d32', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۴. رسم مثال
    # ==========================================
    w_ex = 70
    d_ex = 6
    p_ex = 42
    y_w_ex = get_y_weight(w_ex)
    y_p_ex = get_y_pump(p_ex)
    x_d_ex, y_d_ex = dose_coords[d_ex]

    ax.plot([0, x_d_ex], [y_w_ex, y_d_ex], color='red', linestyle='--', linewidth=2)
    ax.plot([x_d_ex, L], [y_d_ex, y_p_ex], color='red', linestyle='--', linewidth=2)
    ax.plot(0, y_w_ex, 'o', color='red', markersize=8)
    ax.plot(x_d_ex, y_d_ex, 'o', color='red', markersize=8)
    ax.plot(L, y_p_ex, 'o', color='red', markersize=8)

    ax.text(L/2, y_min - 1.5, "Example: Weight = 70 kg, Dose = 6 mg/kg/h  →  Pump rate = 42 mL/h", 
            ha='center', va='top', fontsize=14, color='red', fontweight='bold', 
            bbox=dict(facecolor='#ffe6e6', edgecolor='red', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۵. کادرهای توضیحات
    # ==========================================
    formula_text = "Calculation Formula\n\nPump rate (mL/h) = (Dose (mg/kg/h) × Weight (kg)) / 10\n\n(Propofol 1% = 10 mg/mL)"
    ax.text(1, 0.5, formula_text, ha='left', va='bottom', fontsize=10, color='#1f4e79',
            bbox=dict(facecolor='#e6f0fa', edgecolor='#1f4e79', boxstyle='round,pad=0.8'))

    guide_text = "How to Use the Z-Nomogram\n\n1. Find the patient's weight on the left scale.\n2. Find the desired pump rate on the right scale.\n3. Draw a straight line connecting the two points.\n4. Read the corresponding dose on the diagonal scale."
    ax.text(L-1, 0.5, guide_text, ha='right', va='bottom', fontsize=10, color='#7030a0',
            bbox=dict(facecolor='#f3e6fa', edgecolor='#7030a0', boxstyle='round,pad=0.8'))

    disclaimer = "Disclaimer: This chart is for educational purposes only and does not replace clinical judgment or patient monitoring."
    ax.text(L/2, -0.5, disclaimer, ha='center', va='top', fontsize=9, color='#555555', style='italic')

    ax.text(L/2, 21.5, "Propofol Infusion Rate Nomogram (Corrected Z-Nomogram)", 
            ha='center', va='center', fontsize=16, color='#1f4e79', fontweight='bold')
    ax.text(L/2, 20.8, "Propofol 1% (10 mg/mL)  |  General Anesthesia", 
            ha='center', va='center', fontsize=12, color='#555555')

    # ==========================================
    # ذخیره در حافظه و ارسال به عنوان پاسخ
    # ==========================================
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    img_buf.seek(0)
    return Response(content=img_buf.getvalue(), media_type="image/png")
