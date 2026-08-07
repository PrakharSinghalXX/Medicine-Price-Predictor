from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
import sqlite3


# FastAPI App
app = FastAPI(title="Medicine Price Predictor API",description="Backend for Medicine Price Prediction using FastAPI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
model = joblib.load("medicine_price_model.pkl")

# SQLite Connection
conn = sqlite3.connect("medicine.db",check_same_thread=False)

# 99th percentile threshold
threshold = 2899.32

# Home
@app.get("/")
def home():
    return {"message": "Medicine Price Prediction API","status": "Running"}


# Predict Price
@app.get("/predict-price")
def predict_medicine_price(brand_name: str):

    try:

        if not brand_name.strip():
            raise HTTPException(status_code=400,detail="Medicine name cannot be empty.")

        medicine = pd.read_sql_query(
            """
            SELECT *
            FROM medicines
            WHERE brand_name LIKE ?
            ORDER BY price_inr ASC, rowid ASC
            LIMIT 1
            """,
            conn,
            params=[f"%{brand_name}%"]
        )

        if medicine.empty:
            raise HTTPException(status_code=404,detail=f"{brand_name} not found.")

        if medicine["price_inr"].iloc[0] > threshold:
            raise HTTPException(status_code=400,detail="This medicine belongs to the top 1% price range and is not supported by the prediction model.")

        X = medicine.drop(columns=["price_inr","brand_name"])

        predicted_price = np.expm1(model.predict(X)[0]).round(2)

        return {"brand_name": str(medicine["brand_name"].iloc[0]),"predicted_price": float(predicted_price)}

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500,detail="Prediction Failed.")


# Alternatives
@app.get("/alternatives")
def alternatives(brand_name: str):

    try:

        if not brand_name.strip():
            raise HTTPException(status_code=400,detail="Medicine name cannot be empty.")

        medicine = pd.read_sql_query(
            """
            SELECT *
            FROM medicines
            WHERE brand_name LIKE ?
            ORDER BY rowid ASC
            LIMIT 1
            """,
            conn,
            params=[f"%{brand_name}%"]
        )

        if medicine.empty:
            raise HTTPException(status_code=404,detail=f"{brand_name} not found.")

        composition = int(medicine["cleaned_composition"].iloc[0])
        current_brand = str(medicine["brand_name"].iloc[0])

        alternatives_df = pd.read_sql_query(
            """
            SELECT brand_name, price_inr
            FROM medicines
            WHERE cleaned_composition = ?
              AND brand_name != ?
            ORDER BY price_inr ASC
            LIMIT 5
            """,
            conn,
            params=[composition, current_brand]
        )

        return {"alternatives": alternatives_df.to_dict(orient="records")}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
