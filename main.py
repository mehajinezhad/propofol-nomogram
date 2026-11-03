import io
import matplotlib
matplotlib.use("Agg")  # حتماً قبل از import pyplot
import matplotlib.pyplot as plt
from fastapi import FastAPI, Response
# ... سایر importها ...

app = FastAPI()

@app.get("/generate-nomogram")
def generate_nomogram():
    # ==========================================
    # اینجا کل کد رسم نمودار شما قرار می‌گیرد
    # (همان کدی که در main.py فعلی دارید)
    # ==========================================
    fig, ax = plt.subplots(figsize=(10, 14))
    # ... تمام کدهای رسم محورها، مثال، کادرها و ...
    # ... تا انتهای بخش رسم ...

    # ==========================================
    # بخش حیاتی: تولید و ارسال تصویر
    # ==========================================
    # ۱. ذخیره نمودار در یک بافر حافظه (نه روی دیسک)
    img_buf = io.BytesIO()
    
    # ۲. ذخیره با فرمت PNG. نکته: هیچ‌جا plt.show() فراخوانی نکنید!
    plt.savefig(img_buf, format="png", dpi=300, bbox_inches="tight")
    
    # ۳. بستن figure برای آزادسازی حافظه
    plt.close(fig)

    # ۴. بازگرداندن بایت‌های تصویر با هدر صحیح
    img_buf.seek(0)  # بازگرداندن نشانگر به ابتدای بافر
    return Response(content=img_buf.getvalue(), media_type="image/png")
