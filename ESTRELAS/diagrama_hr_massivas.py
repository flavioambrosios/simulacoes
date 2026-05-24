import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================
# Funções (as mesmas de antes)
# =============================================
def ZAMS_relation(mass):
    L = mass**3.5 if mass >= 0.5 else mass**2.5
    R = mass**0.8
    Teff = 5770 * (L / R**2)**0.25
    return Teff, L

def evolutionary_track_high(mass):
    T_zams, L_zams = ZAMS_relation(mass)
    if mass < 25:
        Teff = [T_zams, T_zams*1.2, 4000, 50000, 1e6, 1e6]
        L = [L_zams, L_zams*10, 1000*L_zams, 5000*L_zams, 1e5, 0.01]
        labels = ['Seq. Principal', 'Supergigante Azul', 'Supergig. Vermelha',
                  'Wolf-Rayet', 'Supernova', 'Estrela de Nêutrons']
        special_marker = dict(symbol='star', size=20, color='cyan')
    else:
        Teff = [T_zams, T_zams*1.2, 4000, 50000, 1e6, 1e6]
        L = [L_zams, L_zams*10, 1000*L_zams, 5000*L_zams, 1e5, 0.001]
        labels = ['Seq. Principal', 'Supergigante Azul', 'Supergig. Vermelha',
                  'Wolf-Rayet', 'Supernova', 'Buraco Negro']
        special_marker = dict(symbol='circle', size=20, color='black', line=dict(color='white', width=2))
    colors = []
    for t in Teff:
        if t > 30000: colors.append('cyan')
        elif t > 8000: colors.append('blue')
        elif t > 4000: colors.append('yellow')
        else: colors.append('red')
    return Teff, L, labels, colors, special_marker

# =============================================
# Preparar dados da ZAMS
# =============================================
masses_zams = np.logspace(-0.3, 1.78, 100)
T_zams_all, L_zams_all = [], []
for m in masses_zams:
    T, L = ZAMS_relation(m)
    T_zams_all.append(T)
    L_zams_all.append(L)

# =============================================
# Criar figura interativa com Plotly
# =============================================
fig = go.Figure()

# Linha ZAMS
fig.add_trace(go.Scatter(
    x=T_zams_all, y=L_zams_all,
    mode='lines',
    line=dict(color='black', width=1, dash='dot'),
    name='Sequência Principal (ZAMS)'
))

# Sol como ponto de referência
fig.add_trace(go.Scatter(
    x=[5770], y=[1],
    mode='markers',
    marker=dict(color='yellow', size=15, line=dict(color='black', width=1)),
    name='Sol (referência)'
))

# Para o slider, vamos criar frames com diferentes massas
masses_slider = np.arange(8.0, 60.5, 0.5)  # passo de 0.5 para não pesar muito
frames = []
for mass in masses_slider:
    T_ev, L_ev, labels, colors, special = evolutionary_track_high(mass)
    
    # Pontos da evolução
    scatter_trace = go.Scatter(
        x=T_ev, y=L_ev,
        mode='markers+lines+text',
        marker=dict(color=colors, size=10, line=dict(color='black', width=1)),
        text=labels,
        textposition='top center',
        textfont=dict(size=9),
        name=f'Evolução {mass:.1f} M☉'
    )
    
    # Marcador especial do remanescente (último ponto)
    last_idx = len(T_ev) - 1
    special_trace = go.Scatter(
        x=[T_ev[last_idx]], y=[L_ev[last_idx]],
        mode='markers',
        marker=special,
        showlegend=False
    )
    
    frame_data = [scatter_trace, special_trace]
    frames.append(go.Frame(data=frame_data, name=str(mass)))

# Adicionar os primeiros dados (massa inicial = 10 M☉)
T_ev, L_ev, labels, colors, special = evolutionary_track_high(10.0)
fig.add_trace(go.Scatter(
    x=T_ev, y=L_ev,
    mode='markers+lines+text',
    marker=dict(color=colors, size=10, line=dict(color='black', width=1)),
    text=labels,
    textposition='top center',
    textfont=dict(size=9),
    name='Evolução 10.0 M☉'
))
# Marcador especial
fig.add_trace(go.Scatter(
    x=[T_ev[-1]], y=[L_ev[-1]],
    mode='markers',
    marker=special,
    showlegend=False
))

# Configurar slider
sliders = [dict(
    active=0,
    currentvalue={"prefix": "Massa: ", "suffix": " M☉"},
    steps=[dict(
        method='animate',
        args=[[str(m)], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
        label=f'{m:.1f}'
    ) for m in masses_slider]
)]

# Layout
fig.update_layout(
    title='Diagrama HR Interativo – Estrelas Massivas (8 a 60 M☉)',
    xaxis=dict(
        title='Temperatura efetiva (K)',
        type='log',
        range=[np.log10(2000), np.log10(1e7)],  # de 2000 K a 10⁷ K
        autorange='reversed'  # temperatura decrescente para a direita
    ),
    yaxis=dict(
        title='Luminosidade (L☉)',
        type='log',
        range=[np.log10(1e-4), np.log10(1e10)]
    ),
    sliders=sliders,
    updatemenus=[dict(
        type='buttons',
        buttons=[dict(label='▶ Play',
                      method='animate',
                      args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)])]
    )],
    width=1000,
    height=800
)

# Adicionar frames à figura
fig.frames = frames

# Salvar como HTML
fig.write_html('diagrama_hr_massivas.html')
print("Arquivo salvo como 'diagrama_hr_massivas.html'. Abra no navegador!")