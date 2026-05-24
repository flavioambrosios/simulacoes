import numpy as np
import plotly.graph_objects as go

np.random.seed(42)
n = 300

# Pulsares normais
P_n = 10**(np.random.normal(0, 0.5, n))
Pdot_n = 10**(np.random.normal(-14, 1, n))
# Millisecond
P_ms = 10**(np.random.normal(-2, 0.3, n))
Pdot_ms = 10**(np.random.normal(-19, 0.5, n))
# Magnetares
P_mg = 10**(np.random.normal(0.8, 0.2, n))
Pdot_mg = 10**(np.random.normal(-11, 1, n))

fig = go.Figure()

fig.add_trace(go.Scatter(x=P_n, y=Pdot_n, mode='markers', marker=dict(color='blue', opacity=0.4),
                         name='Pulsares normais'))
fig.add_trace(go.Scatter(x=P_ms, y=Pdot_ms, mode='markers', marker=dict(color='green', opacity=0.6),
                         name='MSP (milissegundo)'))
fig.add_trace(go.Scatter(x=P_mg, y=Pdot_mg, mode='markers', marker=dict(color='red', opacity=0.5),
                         name='Magnetares'))

# Linhas de B constante
P_grid = np.logspace(-3, 2, 100)
for B in [1e8, 1e10, 1e12, 1e14]:
    Pdot = (B/3.2e19)**2 / P_grid
    fig.add_trace(go.Scatter(x=P_grid, y=Pdot, mode='lines', line=dict(color='gray', dash='dot', width=1),
                             showlegend=False))
    fig.add_annotation(x=P_grid[-1], y=Pdot[-1]*2, text=f'{B:.0e} G', showarrow=False, font=dict(size=8))

# Linhas de idade
for tau in [1e3, 1e6, 1e9]:
    sec_per_year = 365.25*24*3600
    Pdot = P_grid / (2 * tau * sec_per_year)
    fig.add_trace(go.Scatter(x=P_grid, y=Pdot, mode='lines', line=dict(color='gray', dash='dot', width=1),
                             showlegend=False))
    fig.add_annotation(x=P_grid[10], y=Pdot[10]*1.5, text=f'{tau:.0e} anos', showarrow=False, font=dict(size=8))

fig.update_layout(
    title='Diagrama P–Ṗ – Classificação dos Pulsares',
    xaxis=dict(title='Período P (s)', type='log', range=[-3, 1.3]),
    yaxis=dict(title='Ṗ (s/s)', type='log', range=[-21, -9]),
    legend=dict(x=0.01, y=0.99),
    width=900, height=700
)

fig.write_html('diagrama_ppdot.html')