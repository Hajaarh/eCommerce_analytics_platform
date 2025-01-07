from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import pandas as pd
import uvicorn
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Optional
from pipelines import *
import pickle
import os

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client['ecommerce']
MODEL_PATH = "model_rfm.pkl"

@app.get("/api/rfm-data")
async def get_rfm_data():
    try:
        orders = list(db.Orders.aggregate(get_rfm_pipeline()))
        df = pd.DataFrame(orders)
        df = df.rename(columns={
            '_id': 'Customer ID',
            'last_purchase': 'Order Date',
            'total_sales': 'Monetary',
            'frequency': 'Frequency'
        })
        return {"data": df.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rfm")
async def get_rfm_analysis():
    try:

        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                cluster_stats = pickle.load(f)
        else:
            orders = list(db.Orders.aggregate(get_rfm_pipeline()))
            df = pd.DataFrame(orders)
            df = df.rename(columns={
                '_id': 'Customer ID',
                'last_purchase': 'Order Date',
                'total_sales': 'Monetary',
                'frequency': 'Frequency'
            })

            df['Order Date'] = pd.to_datetime(df['Order Date'], format='%Y-%m-%dT%H:%M:%S')

            last_date = df['Order Date'].max()

            df['Recency'] = (last_date - df['Order Date']).dt.days
            df['Recency'] = df['Recency'].max() - df['Recency']

            scaler = StandardScaler()
            rfm_normalized = scaler.fit_transform(df[['Recency', 'Frequency', 'Monetary']])

            kmeans = KMeans(n_clusters=3, random_state=42)
            df['Cluster'] = kmeans.fit_predict(rfm_normalized)

            cluster_stats = {
                'averages': {
                    'recency': df.groupby('Cluster')['Recency'].mean().to_dict(),
                    'frequency': df.groupby('Cluster')['Frequency'].mean().to_dict(),
                    'monetary': df.groupby('Cluster')['Monetary'].mean().to_dict()
                },
                'distribution': df['Cluster'].value_counts(normalize=True).to_dict()
            }

            with open(MODEL_PATH, "wb") as f:
                pickle.dump(cluster_stats, f)

        return cluster_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/elbow")
async def elbow_method(max_k: int = 10):
    try:
        orders = list(db.Orders.aggregate(get_rfm_pipeline()))
        df = pd.DataFrame(orders)
        df = df.rename(columns={
            '_id': 'Customer ID',
            'last_purchase': 'Order Date',
            'total_sales': 'Monetary',
            'frequency': 'Frequency'
        })

        date_max = pd.to_datetime(df['Order Date']).max()
        df['Recency'] = (date_max - pd.to_datetime(df['Order Date'])).dt.days
        df['Recency'] = df['Recency'].max() - df['Recency']

        scaler = StandardScaler()
        rfm_normalized = scaler.fit_transform(df[['Recency', 'Frequency', 'Monetary']])

        inertia = []
        for k in range(1, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(rfm_normalized)
            inertia.append(kmeans.inertia_)

        return {"inertia": inertia}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kpi/sales-per-dates")
async def orders_per_dates():
    try:
        result = list(db.Orders.aggregate(get_sales_by_date_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kpi/total-sales")
async def get_total_sales():
    try:
        result = list(db.Orders.aggregate(get_total_sales_pipeline()))
        return {"data": result[0] if result else {"total_sales": 0}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/sales-by-state")
async def get_sales_by_state():
    try:
        result = list(db.Orders.aggregate(get_sales_by_state_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/sales-by-category")
async def get_sales_by_category():
    try:
        result = list(db.Orders.aggregate(get_sales_by_category_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/sales-by-product")
async def get_sales_by_product():
    try:
        result = list(db.Orders.aggregate(get_sales_by_product_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kpi/total-profit")
async def get_total_profit():
    try:
        result = list(db.Orders.aggregate(get_total_profit_pipeline()))
        return {"data": result[0] if result else {"total_profit": 0}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/profit-by-category")
async def get_profit_by_category():
    try:
        result = list(db.Orders.aggregate(get_profit_by_category_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/profit-by-product")
async def get_profit_by_product():
    try:
        result = list(db.Orders.aggregate(get_profit_by_product_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/top-profitable-products")

async def get_top_profitable_products(limit: Optional[int] = 5):
    try:
        result = list(db.Orders.aggregate(get_top_profitable_products_pipeline(limit)))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/average-basket")
async def get_average_basket():
    try:
        result = list(db.Orders.aggregate(get_average_basket_pipeline()))
        return {"data": result[0] if result else {"average_basket": 0}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/average-basket-by-state")
async def get_average_basket_by_state():
    try:
        result = list(db.Orders.aggregate(get_average_basket_by_state_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/average-basket-by-category")
async def get_average_basket_by_category():
    try:
        result = list(db.Orders.aggregate(get_average_basket_by_category_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kpi/sales-by-location")
async def get_sales_by_location():
    try:
        result = list(db.Orders.aggregate(get_sales_by_location_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/sales-by-region")
async def get_sales_by_region():
    try:
        result = list(db.Orders.aggregate(get_sales_by_region_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/average-basket-by-region")
async def get_average_basket_by_region():
    try:
        result = list(db.Orders.aggregate(get_average_basket_by_region_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/top-categories")
async def get_top_categories(limit: Optional[int] = 5):
    try:
        result = list(db.Orders.aggregate(get_top_categories_pipeline(limit)))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/top-products-by-quantity")
async def get_top_products_by_quantity(limit: Optional[int] = 5):
    try:
        result = list(db.Orders.aggregate(get_top_products_by_quantity_pipeline(limit)))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/sales-matrix")
async def get_sales_matrix():
    try:
        result = list(db.Orders.aggregate(get_sales_matrix_pipeline()))
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)