# Propofol Infusion Rate Nomogram

This project generates a corrected Z-nomogram for propofol infusion rate based on patient weight and desired dose.

## Features

- Logarithmic scales for patient weight and pump rate
- Diagonal propofol dose scale
- Example line for:
  - Weight = 70 kg
  - Dose = 6 mg/kg/h
  - Pump rate = 42 mL/h
- Formula box, usage guide, and educational disclaimer

## Formula

```text
Pump rate (mL/h) = (Dose (mg/kg/h) × Weight (kg)) / 10