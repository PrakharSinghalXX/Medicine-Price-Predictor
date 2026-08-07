# Medicine Price Predictor

An app that predicts the "fair price" of a medicine using a trained ML model (Random Forest Regressor), and suggests cheaper alternatives with the same composition.
- **Top 1% exclusion:** the model does not predict prices for the highest-priced 1% of medicines in the dataset, as these outliers reduce model accuracy.

## Approach

- **Data Cleanining/Preprocessing:**  Fixed null values and made a new uniform column for composition--'cleaned_composition'.
- **Outliers:** The mean of price of medicines was Rs 270.5, however there were outliers whose price was capped at Rs 4,36,000.
- **Model Training:** Used a Random Forest Regressor on the whole dataset while using appropriate hyperparameters however the r2_score was too low and then reduced the model training and testing data to the 99 percentile dataset.

## R2_Score and MAE
- **Model 1(Whole Dataset):** r2_score = 0.15, mae = 135.59
- **Model 2(99 percentile dataset)(Used in app):** r2_score = 0.69, mae = 37.92

## Live Demo

- **Frontend:** (https://medicine-price-predictor.onrender.com)
- **Backend API:** (https://medicine-price-backend.onrender.com)
 

## Features

- **Price Prediction** — enter a medicine's brand name and get a predicted fair price based on a trained regression model
- **Cheaper Alternatives** — find the 5 cheapest medicines with the same active composition
- **Interactive visualization** — alternatives are shown in a sortable table and bar chart
- **Outlier protection** — predictions exclude the top 1% highest-priced medicines in the dataset, where model accuracy is unreliable

## Tech Stack

**Frontend**
- [Streamlit](https://streamlit.io/) — UI
- [Plotly](https://plotly.com/python/) — charts
- [Pandas](https://pandas.pydata.org/) — data handling
- [Requests](https://docs.python-requests.org/) — API calls

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [SQLite](https://www.sqlite.org/) — medicine dataset storage
- [scikit-learn](https://scikit-learn.org/) + [joblib](https://joblib.readthedocs.io/) — trained price prediction model
- [Pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — data processing

**Deployment**
- Backend: [Render](https://render.com/) (free tier)
- Frontend: [Render](https://render.com/) (free tier)


## API Endpoints

### `GET /`
Health check.

**Response:**
```json
{ "message": "Medicine Price Prediction API", "status": "Running" }
```

### `GET /predict-price?brand_name={name}`
Predicts the fair price of the cheapest matching medicine for the given brand name.

**Response (200):**
```json
{ "brand_name": "Augmentin 625 Duo Tablet", "predicted_price": 223.42 }
```

**Errors:**
- `400` — empty brand name, or medicine falls in the top 1% price range (unsupported)
- `404` — medicine not found
- `500` — internal prediction error

### `GET /alternatives?brand_name={name}`
Finds up to 5 cheaper medicines with the same cleaned composition.

**Response (200):**
```json
{
  "alternatives": [
    { "brand_name": "Apcil Tablet", "price_inr": 6.98 },
    { "brand_name": "Clavmox 500mg/125mg Tablet", "price_inr": 13.65 }
  ]
}
```

**Errors:**
- `400` — empty brand name
- `404` — medicine not found
- `500` — internal error

## Data Pipeline

In the backend I have directly used the dataset (`medicine_price.csv`) which contains encoded features except the brand_name since I haven't taken it as a feature.
The original dataset was stored as a single CSV file (~250k rows) and loaded entirely into memory using pandas at API startup. This worked locally, but caused problems on Render's free-tier hosting.
The dataset (`medicine_price.csv`) was converted to SQLite to reduce memory footprint on the free-tier host:

```python
import pandas as pd
import sqlite3

df = pd.read_csv("medicine_price.csv")

conn = sqlite3.connect("medicine.db")
df.to_sql("medicines", conn, if_exists="replace", index=False)

cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_brand_name ON medicines(brand_name)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_composition ON medicines(cleaned_composition)")
conn.commit()
conn.close()
```

`index=False` is used to avoid adding an unnecessary extra index column to the table.

## Local Setup

**1. Clone the repo and install dependencies**
```bash
pip install -r requirements.txt
```

**2. Run the backend**
```bash
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000`

**3. Run the frontend**

Update the `url` variable in `app.py` to point to your local backend (`http://127.0.0.1:8000`), then:
```bash
streamlit run app.py
```




