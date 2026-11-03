import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "Go to /generate-nomogram"}

@app.get("/generate-nomogram")
def generate_nomogram():
    # ==========================================
    # اینجا کل کد رسم نمودار شما قرار می‌گیرد
    # (همان کدی که در main.py فعلی دارید)
    # ==========================================
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.set_xlim(-2, 17)
    ax.set_ylim(0, 22)
    ax.axis("off")
    # ... تمام کدهای رسم محورها، مثال، کادرها ...
    # ... تا انتهای بخش رسم ...

    plt.savefig("propofol_z_nomogram.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return FileResponse("propofol_z_nomogram.png", media_type="image/png")
