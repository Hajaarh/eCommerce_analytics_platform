import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

COLORS = {
    '0': '#87CEFA',
    '1': '#90EE90',
    '2': '#FFA500'
}

CLUSTER_NAMES = {
    '0': "Champions",
    '1': "Clients récents",
    '2': "Clients à risque"
}

def create_metric_chart(data, metric_name, title):
    df = pd.DataFrame(data['averages'][metric_name].items(), columns=['Cluster', 'Value'])
    df['Segment'] = df['Cluster'].astype(str).map(CLUSTER_NAMES)
    fig = px.bar(
        df,
        x='Cluster',
        y='Value',
        title=title,
        color='Cluster',
        color_discrete_map=COLORS,
        labels={'Value': title, 'Cluster': 'Segment'}
    )
    return fig

def plot_elbow_chart(inertia):
    fig = px.line(
        x=list(range(1, len(inertia) + 1)),
        y=inertia,
        markers=True,
        labels={"x": "Nombre de clusters (k)", "y": "Inertie intra-cluster"},
        title="Méthode du coude"
    )
    fig.update_traces(mode='lines+markers')
    return fig

st.set_page_config(page_title="Tableau de bord eCommerce", layout="wide")
st.title("📊 Tableau de bord eCommerce")

page = st.sidebar.selectbox(
    "Sélectionner une page :",
    [
        "Ventes",
        "Profits",
        "Clients",
        "Produits"
    ]
)

if page == "Ventes":
    st.header("📈 Analyse des Ventes")

    response = requests.get("http://127.0.0.1:8000/kpi/total-sales")
    if response.status_code == 200:
        data = response.json()["data"]
        st.metric(label="💰 Total des ventes", value=f"{data['total_sales']:.2f} €")

    response = requests.get("http://127.0.0.1:8000/kpi/average-basket")
    if response.status_code == 200:
        data = response.json()["data"]
        avg_basket = data["average_basket"]
        st.metric(label="🛒 Panier moyen global", value=f"{avg_basket:.2f} €")

    response = requests.get("http://127.0.0.1:8000/kpi/sales-per-dates")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)
        df["_id"] = pd.to_datetime(df["_id"])
        fig = px.line(df, x="_id", y="total_ventes", title="📈 Croissance des ventes par date")
        st.plotly_chart(fig)

    response = requests.get("http://127.0.0.1:8000/kpi/sales-by-state")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data).nlargest(10, 'total_sales')
        fig = px.bar(df, x='total_sales', y='_id', title="🏛️ Top 10 Ventes par État", color='_id',
                     color_discrete_sequence=px.colors.sequential.Bluered)
        st.plotly_chart(fig)

    response = requests.get("http://127.0.0.1:8000/kpi/sales-by-category")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)
        fig = px.pie(df, names="_id", values="total_sales", title="📂 Ventes par catégorie")
        st.plotly_chart(fig, use_container_width=True, key="sales_by_category")
    else:
        st.warning("Impossible de récupérer les données pour les ventes par catégorie de produits.")

    st.header("📊 Prévisions des Ventes")
    response3 = requests.get("http://127.0.0.1:8000/kpi/sales-per-dates")
    if response3.status_code == 200:
        forecast_data = response3.json()["data"]
        df1 = pd.DataFrame(forecast_data)
        df1 = df1.rename(columns={'_id': 'ds', 'total_ventes': 'y'})

        with st.spinner('Calcul des prévisions en cours...'):
            m = Prophet()
            m.fit(df1)
            future = m.make_future_dataframe(periods=365)
            forecast = m.predict(future)

            fig1 = plot_plotly(m, forecast)
            fig2 = plot_components_plotly(m, forecast)

            fig1.update_traces(marker=dict(color='#ff7f0e'))
            fig2.update_traces(line=dict(color='#1f77b4'))

            st.plotly_chart(fig1)
            st.plotly_chart(fig2)
    else:
        st.error("Erreur lors du chargement des données pour les prévisions")

if page == "Profits":
    st.header("💹 Analyse des Profits")

    response = requests.get("http://127.0.0.1:8000/kpi/total-profit")
    if response.status_code == 200:
        data = response.json()["data"]
        st.metric(label="💰 Total des profits", value=f"{data['total_profit']:.2f} €")

    response = requests.get("http://127.0.0.1:8000/kpi/profit-by-category")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)
        fig = px.pie(df, names="_id", values="total_profit", title="🏷️ Profit par catégorie")
        st.plotly_chart(fig)

    response = requests.get("http://127.0.0.1:8000/kpi/profit-by-product")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data).nlargest(5, 'total_profit')
        fig = px.bar(df, x="_id", y="total_profit", title="Top 5 Produits les plus rentables")
        st.plotly_chart(fig)

    response = requests.get("http://127.0.0.1:8000/kpi/profit-by-product")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)

        if not df.empty:
            fig = px.bar(df, x="_id", y="total_profit", title="💹 Profits par produit")
            st.plotly_chart(fig, use_container_width=True, key="profit_by_product")
        else:
            st.warning("Aucune donnée disponible pour les profits par produit.")
    else:
        st.error("Erreur lors de la récupération des données pour les profits par produit.")

if page == "Clients":
    st.header("👥 Analyse des Clients")

    st.subheader("Méthode du coude")
    max_k = st.slider("Nombre maximal de clusters", min_value=2, max_value=10, value=7)

    elbow_response = requests.get(f"http://localhost:8000/api/elbow?max_k={max_k}")
    if elbow_response.status_code == 200:
        elbow_data = elbow_response.json()
        if "inertia" in elbow_data:
            elbow_chart = plot_elbow_chart(elbow_data["inertia"])
            st.plotly_chart(elbow_chart)
        else:
            st.error("Erreur lors du calcul de la méthode du coude.")

    st.subheader("📈 Analyse RFM")
    response = requests.get("http://localhost:8000/api/rfm")
    if response.status_code == 200:
        data = response.json()

        st.markdown("### 📊 Moyennes par Cluster")
        col1, col2, col3 = st.columns(3)

        metrics = [
            ('recency', 'Récence moyenne', col1),
            ('frequency', 'Fréquence moyenne', col2),
            ('monetary', 'Valeur monétaire moyenne', col3)
        ]

        for metric, title, col in metrics:
            fig = create_metric_chart(data, metric, title)
            col.plotly_chart(fig, use_container_width=True)

        st.markdown("### Distribution des Segments")
        dist_df = pd.DataFrame(data['distribution'].items(), columns=['Cluster', 'Percentage'])
        dist_df['Segment'] = dist_df['Cluster'].map(CLUSTER_NAMES)

        fig_pie = px.pie(
            dist_df,
            values='Percentage',
            names='Segment',
            title='Répartition des Clients',
            color='Segment',
            color_discrete_map={name: COLORS[str(i)] for i, name in CLUSTER_NAMES.items()}
        )
        st.plotly_chart(fig_pie)

        with st.expander("Voir les détails des segments"):
            st.write("### 📋 Description des segments")

            for cluster, name in CLUSTER_NAMES.items():

                st.markdown(f"**{name}** (Cluster {cluster}):")
                st.write(f"- Fréquence moyenne: {data['averages']['frequency'][cluster]:.2f} achats")
                st.write(f"- Valeur moyenne: {data['averages']['monetary'][cluster]:.2f} €")
                st.write(f"- Pourcentage des clients: {data['distribution'][cluster] * 100:.1f}%")
                st.write("---")
    else:
        st.error("Erreur lors de la récupération des données RFM")

if page == "Produits":
    st.header("📦 Analyse des Produits")

    response = requests.get("http://127.0.0.1:8000/kpi/sales-by-product")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data).nlargest(5, 'total_sales')
        fig = px.bar(df, x="_id", y="total_sales", title="Top Produits vendus")
        st.plotly_chart(fig)

    response = requests.get("http://127.0.0.1:8000/kpi/top-products-by-quantity?limit=5")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)
        if not df.empty:
            fig = px.bar(
                df,
                x="_id",
                y="total_quantity",
                title=":Top produits par quantité",
                color="total_quantity",
                color_continuous_scale=px.colors.sequential.Sunset
            )
            st.plotly_chart(fig, use_container_width=True, key="top_products_by_quantity")
        else:
            st.warning("Aucune donnée disponible pour les top produits par quantité.")
    else:
        st.error("Erreur lors de la récupération des données pour les top produits par quantité.")

    response = requests.get("http://127.0.0.1:8000/kpi/top-categories?limit=5")
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data)

        if not df.empty:
            fig = px.bar(df, x="_id", y="total_quantity", title="🏷️ Top catégories vendues")
            st.plotly_chart(fig, use_container_width=True, key="top_categories")
        else:
            st.warning("Aucune donnée disponible pour les top catégories vendues.")
    else:
        st.error("Erreur lors de la récupération des données pour les top catégories vendues.")