import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import io
from fastapi import FastAPI, Response

app = FastAPI()

# کش کردن تصویر برای سرعت بالاتر
cached_image = None

def create_nomogram_image():
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.set_xlim(-2, 17)
    ax.set_ylim(0, 22)
    ax.axis('off')

    L = 15
    y_min, y_max = 2, 18

    # توابع ریاضی دقیق برای ترسیم مقیاس‌ها
    def get_y_weight(w):
        return 6.148 * np.log10(w) + 3.85

    def get_y_dose(d):
        return 6.148 * np.log10(d) + 8.148

    def get_y_pump(p):
        return 3.074 * np.log10(10 * p) + 5.999

    # ==========================================
    # ۱. محور چپ: وزن (Weight)
    # ==========================================
    ax.plot([0, 0], [y_min, y_max], color='#1f4e79', linewidth=4)
    weights = [0.5, 1, 2, 5, 10, 20, 30, 50, 70, 100, 150, 200]
    for w in weights:
        y = get_y_weight(w)
        ax.plot([0, -0.3], [y, y], color='#1f4e79', linewidth=2)
        ax.text(-0.5, y, str(w), ha='right', va='center', fontsize=11, color='#1f4e79', fontweight='bold')
    
    ax.text(0, y_max + 1, "Patient Weight\n(kg)", ha='center', va='bottom', fontsize=12, color='#1f4e79', fontweight='bold', bbox=dict(facecolor='#e6f0fa', edgecolor='#1f4e79', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۲. محور راست: دوز (Dose)
    # ==========================================
    ax.plot([L, L], [y_min, y_max], color='#2e7d32', linewidth=4)
    doses = [0.1, 0.2, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12]
    for d in doses:
        y = get_y_dose(d)
        ax.plot([L, L + 0.3], [y, y], color='#2e7d32', linewidth=2)
        ax.text(L + 0.5, y, str(d), ha='left', va='center', fontsize=11, color='#2e7d32', fontweight='bold')
    
    ax.text(L, y_max + 1, "Propofol Dose\n(mg/kg/h)", ha='center', va='bottom', fontsize=12, color='#2e7d32', fontweight='bold', bbox=dict(facecolor='#e8f5e9', edgecolor='#2e7d32', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۳. محور وسط: سرعت پمپ (Pump Rate)
    # ==========================================
    ax.plot([L/2, L/2], [y_min, y_max], color='#7030a0', linewidth=4)
    pumps = [0.5, 1, 2, 5, 10, 15, 20, 30, 40, 42, 50, 60, 80, 100, 150, 200, 300, 400]
    for p in pumps:
        y = get_y_pump(p)
        ax.plot([L/2, L/2 + 0.3], [y, y], color='#7030a0', linewidth=2)
        ax.text(L/2 + 0.5, y, str(p), ha='left', va='center', fontsize=11, color='#7030a0', fontweight='bold')
    
    ax.text(L/2, y_max + 1, "Pump Rate\n(mL/h)", ha='center', va='bottom', fontsize=12, color='#7030a0', fontweight='bold', bbox=dict(facecolor='#f3e6fa', edgecolor='#7030a0', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۴. خط مثال (قرمز)
    # ==========================================
    w_ex = 70
    d_ex = 6
    p_ex = 42
    
    y_w_ex = get_y_weight(w_ex)
    y_d_ex = get_y_dose(d_ex)
    y_p_ex = get_y_pump(p_ex)

    # خطی که از وزن ۷۰ به دوز ۶ کشیده شده و دقیقاً از سرعت ۴۲ عبور می‌کند
    ax.plot([0, L], [y_w_ex, y_d_ex], color='red', linestyle='--', linewidth=2)
    
    # نقاط قرمز روی هر سه محور
    ax.plot(0, y_w_ex, 'o', color='red', markersize=8)
    ax.plot(L/2, y_p_ex, 'o', color='red', markersize=8)
    ax.plot(L, y_d_ex, 'o', color='red', markersize=8)

    ax.text(L/2, y_min - 1.5, "Example: Weight = 70 kg, Dose = 6 mg/kg/h  →  Pump rate = 42 mL/h", 
            ha='center', va='top', fontsize=14, color='red', fontweight='bold', 
            bbox=dict(facecolor='#ffe6e6', edgecolor='red', boxstyle='round,pad=0.5'))

    # ==========================================
    # ۵. کادرهای توضیحات
    # ==========================================
    formula_text = "Calculation Formula\n\nPump rate (mL/h) = (Dose (mg/kg/h) × Weight (kg)) / 10\n\n(Propofol 1% = 10 mg/mL)"
    ax.text(1, 0.5, formula_text, ha='left', va='bottom', fontsize=10, color='#1f4e79',
            bbox=dict(facecolor='#e6f0fa', edgecolor='#1f4e79', boxstyle='round,pad=0.8'))

    guide_text = "How to Use the Nomogram\n\n1. Find the patient's weight on the left scale.\n2. Find the desired dose on the right scale.\n3. Draw a straight line connecting the two points.\n4. Read the corresponding pump rate on the middle scale."
    ax.text(L-1, 0.5, guide_text, ha='right', va='bottom', fontsize=10, color='#7030a0',
            bbox=dict(facecolor='#f3e6fa', edgecolor='#7030a0', boxstyle='round,pad=0.8'))

    disclaimer = "Disclaimer: This chart is for educational purposes only and does not replace clinical judgment or patient monitoring."
    ax.text(L/2, -0.5, disclaimer, ha='center', va='top', fontsize=9, color='#555555', style='italic')

    # عنوان
    ax.text(L/2, 21.5, "Propofol Infusion Rate Nomogram", ha='center', va='center', fontsize=16, color='#1f4e79', fontweight='bold')
    ax.text(L/2, 20.8, "Propofol 1% (10 mg/mL)  |  General Anesthesia", ha='center', va='center', fontsize=12, color='#555555')

    # تولید تصویر در حافظه
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png", dpi=200, bbox_inches='tight')
    plt.close(fig)
    return img_buf.getvalue()

@app.get("/")
def home():
    return {"status": "ok", "message": "Go to /generate-nomogram"}

@app.get("/generate-nomogram")
def generate_nomogram():
    global cached_image
    if cached_image is None:
        cached_image = create_nomogram_image()
    return Response(content=cached_image, media_type="image/png")
