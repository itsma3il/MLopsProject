# pipeline_dashboard.py
"""
Generate a visual dashboard showing pipeline status.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
import duckdb
from datetime import datetime


TABLER_ICON_CSS = "https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css"


def icon(name: str) -> str:
    """Return a Tabler icon HTML snippet."""

    return f'<i class="ti ti-{name}"></i>'


def status_badge(label: str, completed: bool) -> str:
    """Build a compact status badge for the dashboard."""

    state_class = "is-complete" if completed else "is-pending"
    state_icon = icon("circle-check") if completed else icon("clock-hour-3")
    return f'<span class="status-badge {state_class}">{state_icon}<span>{label}</span></span>'


def notice_box(message: str, icon_name: str = "alert-triangle") -> str:
    """Build an inline notice block for empty states."""

    return (
        '<div style="display:flex; align-items:center; gap:0.55rem; padding:0.8rem 0.95rem; '
        'border-radius:14px; background:rgba(59,130,246,0.08); color:#1d4ed8; font-weight:600; '
        'margin-top:0.25rem;">'
        f'{icon(icon_name)}<span>{message}</span></div>'
    )


def create_pipeline_dashboard():
    """Create a Streamlit dashboard for pipeline status."""
    
    st.set_page_config(
        page_title="Fraud Pipeline Dashboard",
        layout="wide",
        page_icon="FD"
    )

    st.markdown(
        f"""
        <link rel="stylesheet" href="{TABLER_ICON_CSS}">
        <style>
            .stApp {{
                background: transparent;
            }}

            .main .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }}

            .hero-card {{
                background-image: repeating-linear-gradient(90deg, hsla(57,0%,42%,0.09) 0px, hsla(57,0%,42%,0.09) 1px,transparent 1px, transparent 60px),repeating-linear-gradient(0deg, hsla(57,0%,42%,0.09) 0px, hsla(57,0%,42%,0.09) 1px,transparent 1px, transparent 60px),repeating-linear-gradient(0deg, hsla(57,0%,42%,0.09) 0px, hsla(57,0%,42%,0.09) 1px,transparent 1px, transparent 10px),repeating-linear-gradient(90deg, hsla(57,0%,42%,0.09) 0px, hsla(57,0%,42%,0.09) 1px,transparent 1px, transparent 10px),linear-gradient(90deg, rgb(20,20,20),rgb(20,20,20));
                margin-top: 1.5rem;
                color: white;
                border-radius: 24px;
                padding: 2rem;
                box-shadow: 0 1px 18px rgba(15, 23, 42, 0.18);
                margin-bottom: 1.5rem;
            }}

            .hero-eyebrow {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.12);
                color: #dbeafe;
                font-size: 0.82rem;
                font-weight: 600;
                letter-spacing: 0.02em;
            }}

            .hero-title {{
                margin: 0.9rem 0 0.5rem 0;
                font-size: 2.2rem;
                line-height: 1.05;
                color: #f8fafc;
                font-weight: 800;
            }}

            .hero-copy {{
                margin: 0;
                max-width: 720px;
                color: rgba(248, 250, 252, 0.82);
                font-size: 1rem;
            }}

            .hero-meta {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                margin-top: 1.25rem;
            }}

            .meta-pill {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.55rem 0.85rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.1);
                color: #f8fafc;
                font-size: 0.88rem;
            }}

            .section-title {{
                display: inline-flex;
                align-items: center;
                gap: 0.55rem;
                margin: 0 0 0.9rem 0;
                font-size: 1.05rem;
                font-weight: 700;
                color: #0f172a;
            }}

            .dashboard-card {{
                background: rgba(255, 255, 255, 0.85);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 20px;
                padding: 1.2rem 1.25rem;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
                height: 100%;
            }}

            .dashboard-card:hover {{
                border-color: rgba(15, 118, 110, 0.35);
                box-shadow: 0 14px 38px rgba(15, 23, 42, 0.09);
                transition: all 0.2s ease;
            }}

            .status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.45rem 0.7rem;
                margin: 0.2rem 0.25rem 0.2rem 0;
                border-radius: 999px;
                font-size: 0.85rem;
                font-weight: 600;
            }}

            .status-badge.is-complete {{
                background: rgba(16, 185, 129, 0.12);
                color: #047857;
            }}

            .status-badge.is-pending {{
                background: rgba(245, 158, 11, 0.12);
                color: #b45309;
            }}

            .status-badge .ti {{
                font-size: 0.95rem;
            }}

            .metrics-grid {{
                display: grid;
                gap: 0.85rem;
            }}

            .metric-card {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 0.95rem 1rem;
                border-radius: 16px;
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid rgba(148, 163, 184, 0.2);
            }}

            .metric-label {{
                display: flex;
                align-items: center;
                gap: 0.55rem;
                color: #334155;
                font-size: 0.9rem;
                font-weight: 600;
            }}

            .metric-value {{
                color: #0f172a;
                font-size: 1.35rem;
                font-weight: 800;
                line-height: 1;
            }}

            .metric-hint {{
                margin-top: 0.2rem;
                color: #64748b;
                font-size: 0.8rem;
            }}

            .log-panel pre {{
                margin: 0;
                border-radius: 14px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(
        f"""
        <div class="hero-card">
            <span class="hero-eyebrow">{icon("activity")} Pipeline observability</span>
            <h1 class="hero-title">Fraud Detection Pipeline</h1>
            <p class="hero-copy">
                Monitor data freshness, database ingestion, dbt transformations, model training, and API readiness from a single operational view.
            </p>
            <div class="hero-meta">
                <span class="meta-pill">{icon("clock-hour-3")} Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                <span class="meta-pill">{icon("stack-2")} End-to-end MLOps coverage</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Sidebar
    st.sidebar.header("Pipeline Status")
    st.sidebar.markdown(
        f"""
        <div style="display:flex; flex-direction:column; gap:0.75rem;">
            <div style="padding:0.8rem 0.9rem; border-radius:14px; background:rgba(15,23,42,0.05);">
                <div style="font-size:0.82rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em;">{icon("clock-hour-3")} Last Updated</div>
                <div style="margin-top:0.25rem; font-weight:700; color:#0f172a;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div style="padding:0.8rem 0.9rem; border-radius:14px; background:rgba(15,118,110,0.08); color:#0f766e; font-weight:600;">
                {icon("layout-dashboard")} Live operational dashboard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Main content
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown(f'<div class="section-title">{icon("database")} Data Status</div>', unsafe_allow_html=True)
        
        
        # Dataset info
        if Path("data/raw/creditcard.csv").exists():
            df = pd.read_csv("data/raw/creditcard.csv")
            st.markdown(
                '<div class="metrics-grid">'
                + f'<div class="metric-card"><div><div class="metric-label">{icon("database")} Total Samples</div><div class="metric-hint">Rows loaded from raw dataset</div></div><div class="metric-value">{len(df):,}</div></div>'
                + f'<div class="metric-card"><div><div class="metric-label">{icon("schema")} Features</div><div class="metric-hint">Predictor columns excluding target</div></div><div class="metric-value">{len(df.columns) - 1}</div></div>'
                + f'<div class="metric-card"><div><div class="metric-label">{icon("trending-down")} Fraud Rate</div><div class="metric-hint">Positive class prevalence</div></div><div class="metric-value">{df["Class"].mean()*100:.2f}%</div></div>'
                + '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(notice_box("Dataset not loaded"), unsafe_allow_html=True)
        
    
    with col2:
        st.markdown(f'<div class="section-title">{icon("database-export")} Database Status</div>', unsafe_allow_html=True)
        
        db_path = Path("data/warehouse/fraud.duckdb")
        if db_path.exists():
            st.markdown(
                '<div class="metric-card">'
                f'<div><div class="metric-label">{icon("database")} Database Size</div><div class="metric-hint">DuckDB warehouse footprint</div></div>'
                f'<div class="metric-value">{db_path.stat().st_size / (1024*1024):.1f} MB</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            
            try:
                with duckdb.connect(str(db_path)) as con:
                    tables = con.execute("SHOW TABLES").fetchall()
                    st.markdown(f'<div class="section-title" style="margin-top:1rem; font-size:0.98rem;">{icon("table")} Tables</div>', unsafe_allow_html=True)
                    for table in tables:
                        count = con.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                        st.markdown(
                            f'<div class="status-badge is-complete" style="justify-content:space-between; width:100%; border-radius:14px; padding:0.65rem 0.8rem;">'
                            f'<span>{icon("table")} {table[0]}</span><span>{count:,} rows</span></div>',
                            unsafe_allow_html=True,
                        )
            except Exception as e:
                st.error(f"Error reading database: {e}")
        else:
            st.markdown(notice_box("Database not initialized"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="section-title">{icon("brain")} Model Status</div>', unsafe_allow_html=True)
        
        # Model metrics
        metrics_path = Path("models/metrics.json")
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            # Display metrics
            st.markdown(f'<div class="section-title" style="margin-top:0; font-size:0.98rem;">{icon("chart-line")} Performance Metrics</div>', unsafe_allow_html=True)
            for name, value in metrics.items():
                if isinstance(value, (int, float)):
                    if "accuracy" in name.lower() or "f1" in name.lower():
                        st.markdown(
                            f'<div class="metric-card">'
                            f'<div><div class="metric-label">{icon("target-arrow")} {name.title()}</div><div class="metric-hint">Key decision metric</div></div>'
                            f'<div class="metric-value">{value:.4f}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="metric-card">'
                            f'<div><div class="metric-label">{icon("chart-bar")} {name.title()}</div><div class="metric-hint">Recorded evaluation metric</div></div>'
                            f'<div class="metric-value">{value:.4f}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
        else:
            st.markdown(notice_box("Model not trained"), unsafe_allow_html=True)
    
    # Pipeline steps
    st.markdown("<hr style='margin:1.75rem 0; border:none; border-top:1px solid rgba(148,163,184,0.28);'>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{icon("route")} Pipeline Steps</div>', unsafe_allow_html=True)
    
    steps = [
        ("1. Data Loading", Path("data/raw/creditcard.csv").exists()),
        ("2. Database Ingestion", Path("data/warehouse/fraud.duckdb").exists()),
        ("3. dbt Transformations", Path("dbt_fraud/target/manifest.json").exists()),
        ("4. Feature Engineering", Path("models/feature_columns.json").exists()),
        ("5. Model Training", Path("models/metrics.json").exists()),
        ("6. API Service", Path("api/main.py").exists()),
    ]
    
    for step, completed in steps:
        st.progress(100 if completed else 0)
        st.markdown(status_badge(step, completed), unsafe_allow_html=True)
    
    # Recent logs
    st.markdown("<hr style='margin:1.75rem 0; border:none; border-top:1px solid rgba(148,163,184,0.28);'>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{icon("file-text")} Recent Logs</div>', unsafe_allow_html=True)
    
    log_file = Path("logs/pipeline.log")
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()[-10:]
            st.markdown('<div class="dashboard-card log-panel">', unsafe_allow_html=True)
            for line in lines:
                st.code(line.strip())
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(notice_box("No logs available", "file-off"), unsafe_allow_html=True)

if __name__ == "__main__":
    create_pipeline_dashboard()