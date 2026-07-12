"""Application Streamlit - Detection de fraude."""

import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Fraud Detection", page_icon="🛡️", layout="wide")


def api_call(endpoint: str, method: str = "get", json=None):
    """Appel API avec gestion d'erreur."""
    try:
        r = getattr(requests, method)(f"{API_URL}/{endpoint}", json=json, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("API non disponible. Lancez: uvicorn api.main:app --reload")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur API: {e.response.text}")
        return None


# === SIDEBAR ===
st.sidebar.title("🛡️ Fraud Detection")
page = st.sidebar.radio("Navigation", ["Prediction", "Upload CSV", "Historique", "Dashboard"])

# Health check
health = api_call("health")
if health:
    status = "✅" if health["model_loaded"] else "⚠️ Modele non charge"
    st.sidebar.info(f"API: {status}")


# === PAGE: PREDICTION ===
if page == "Prediction":
    st.title("🔍 Prediction de fraude")

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Montant (€)", min_value=0.0, value=100.0, step=10.0)
        time_val = st.number_input("Time (sec)", min_value=0.0, value=0.0)
    with col2:
        mode = st.radio("Features V1-V28", ["Aleatoire", "Zeros"])

    v_features = {f"V{i}": float(np.random.randn()) if mode == "Aleatoire" else 0.0 for i in range(1, 29)}

    if st.button("🚀 Analyser", type="primary", use_container_width=True):
        data = {"Time": time_val, "Amount": amount, **v_features}
        result = api_call("predict", method="post", json=data)

        if result:
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                if result["is_fraud"]:
                    st.error("🚨 FRAUDE DETECTEE")
                else:
                    st.success("✅ Transaction legitime")
            with c2:
                st.metric("Probabilite", f"{result['fraud_probability']:.2%}")
            with c3:
                st.metric("Risque", result["risk_level"])

            # Jauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result["fraud_probability"] * 100,
                title={"text": "Score de Risque (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkred"},
                    "steps": [
                        {"range": [0, 30], "color": "#00cc00"},
                        {"range": [30, 60], "color": "#ffaa00"},
                        {"range": [60, 80], "color": "#ff6600"},
                        {"range": [80, 100], "color": "#ff0000"},
                    ],
                },
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)


# === PAGE: UPLOAD CSV ===
elif page == "Upload CSV":
    st.title("📁 Prediction Batch - Upload CSV")
    st.info("Uploadez un CSV avec les colonnes: Time, V1-V28, Amount")

    uploaded = st.file_uploader("Choisir un fichier CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.write(f"**{len(df)} transactions chargees**")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("🚀 Lancer la prediction batch", type="primary"):
            # Envoyer par lots de 100
            all_results = []
            progress = st.progress(0)
            for i in range(0, len(df), 100):
                batch = df.iloc[i:i+100].to_dict(orient="records")
                resp = api_call("batch_predict", method="post", json={"transactions": batch})
                if resp:
                    all_results.extend(resp["predictions"])
                progress.progress(min(1.0, (i + 100) / len(df)))

            if all_results:
                results_df = pd.DataFrame(all_results)
                fraud_count = results_df["is_fraud"].sum()

                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total", len(results_df))
                c2.metric("Fraudes", fraud_count)
                c3.metric("Taux", f"{fraud_count/len(results_df):.2%}")

                st.dataframe(results_df, use_container_width=True)


# === PAGE: HISTORIQUE ===
elif page == "Historique":
    st.title("📜 Historique des predictions")

    history = api_call("predictions/history?limit=100")
    if history:
        if len(history) == 0:
            st.info("Aucune prediction enregistree.")
        else:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Historique non disponible (DB non connectee?)")


# === PAGE: DASHBOARD ===
elif page == "Dashboard":
    st.title("📊 Dashboard Analytique")

    history = api_call("predictions/history?limit=500")
    if not history or len(history) == 0:
        st.info("Pas assez de donnees. Effectuez des predictions d'abord.")
    else:
        df = pd.DataFrame(history)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c2.metric("Fraudes", df["is_fraud"].sum())
        c3.metric("Taux fraude", f"{df['is_fraud'].mean():.1%}")
        c4.metric("Montant moyen", f"{df['amount'].mean():.2f}€")

        col1, col2 = st.columns(2)
        with col1:
            risk_counts = df["risk_level"].value_counts()
            fig = go.Figure(data=[go.Pie(labels=risk_counts.index, values=risk_counts.values)])
            fig.update_layout(title="Repartition des risques")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure(data=[go.Histogram(x=df["fraud_probability"], nbinsx=20)])
            fig.update_layout(title="Distribution des probabilites", xaxis_title="Probabilite")
            st.plotly_chart(fig, use_container_width=True)
