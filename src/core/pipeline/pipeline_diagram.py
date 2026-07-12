"""
Generate pipeline diagram for academic report.
"""

from graphviz import Digraph
import os

def create_pipeline_diagram():
    """Create a professional pipeline diagram."""
    
    dot = Digraph(
        comment='Fraud Detection Pipeline',
        format='png',
        engine='dot'
    )
    
    # Set global graph attributes
    dot.attr(
        rankdir='TB',
        splines='ortho',
        nodesep='0.5',
        ranksep='0.7',
        fontsize='12',
        fontname='Helvetica'
    )
    
    # Node styles
    dot.attr('node', 
             shape='box',
             style='rounded,filled',
             fontname='Helvetica',
             fontsize='11')
    
    # Data Layer
    with dot.subgraph(name='cluster_data') as c:
        c.attr(label='Data Layer', style='rounded', color='#2C3E50')
        c.node('Kaggle', 'Kaggle Dataset\nCredit Card Fraud', 
               fillcolor='#85C1E9')
        c.node('Raw', 'Raw Data\ncreditcard.csv', 
               fillcolor='#85C1E9')
        c.node('DuckDB', 'DuckDB Warehouse\nfraud.duckdb', 
               fillcolor='#85C1E9')
    
    # Processing Layer
    with dot.subgraph(name='cluster_processing') as c:
        c.attr(label='Processing Layer', style='rounded', color='#2C3E50')
        c.node('Ingestion', 'Data Ingestion\nPython + dlt', 
               fillcolor='#F1948A')
        c.node('dbt', 'dbt Transformations\nStaging + Mart', 
               fillcolor='#F1948A')
        c.node('Features', 'Feature Engineering\nPython', 
               fillcolor='#F1948A')
    
    # ML Layer
    with dot.subgraph(name='cluster_ml') as c:
        c.attr(label='ML Layer', style='rounded', color='#2C3E50')
        c.node('Training', 'Model Training\nRandom Forest/XGBoost', 
               fillcolor='#82E0AA')
        c.node('Evaluation', 'Model Evaluation\nMetrics + Validation', 
               fillcolor='#82E0AA')
        c.node('Model', 'Saved Model\n.pkl + .json', 
               fillcolor='#82E0AA')
    
    # Application Layer
    with dot.subgraph(name='cluster_app') as c:
        c.attr(label='Application Layer', style='rounded', color='#2C3E50')
        c.node('API', 'API Service\nFastAPI', 
               fillcolor='#F9E79F')
        c.node('Monitoring', 'Monitoring\nMetrics + Logging', 
               fillcolor='#F9E79F')
        c.node('Dashboard', 'Dashboard\nStreamlit/Gradio', 
               fillcolor='#F9E79F')
    
    # Connections
    edges = [
        ('Kaggle', 'Raw'),
        ('Raw', 'Ingestion'),
        ('Ingestion', 'DuckDB'),
        ('DuckDB', 'dbt'),
        ('dbt', 'Features'),
        ('Features', 'Training'),
        ('Training', 'Evaluation'),
        ('Evaluation', 'Model'),
        ('Model', 'API'),
        ('API', 'Dashboard'),
        ('API', 'Monitoring'),
    ]
    
    for src, dst in edges:
        dot.edge(src, dst, arrowhead='normal', arrowsize='0.8')
    
    # Save
    dot.render('pipeline_diagram', view=False, cleanup=True)
    print("✅ Pipeline diagram saved as pipeline_diagram.png")

if __name__ == "__main__":
    create_pipeline_diagram()