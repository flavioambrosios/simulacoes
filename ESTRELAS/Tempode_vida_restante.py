import numpy as np
import plotly.graph_objects as go

def calcular_tempos(M):
    """
    Retorna (elementos, tempos_restantes) para a massa M.
    tempo_restante[i] = anos de vida que restam a partir do início da fase i.
    """
    # Queima do H (sequência principal)
    if M <= 10:
        t_H = 1e10 * M**(-2.5)
    else:
        t_H_base = 1e10 * 10**(-2.5)   # ≈3.16e7 anos
        t_H = t_H_base * (M / 10)**(-1.3)

    if M < 8:
        # Apenas H e He; termina como anã branca de C/O
        f_He = 0.02 + (0.08 / 7) * (M - 1)   # de 0.02 (1 M☉) a 0.10 (8 M☉)
        t_He = f_He * t_H
        rest_H = t_H + t_He    # total de vida desde o nascimento (queima de H)
        rest_He = t_He         # vida restante quando começa a queima do He
        elementos = ['He<br>(H→He)', 'C (não queima)<br>[fim]']
        tempos = [rest_H, rest_He]
        return elementos, tempos
    else:
        t_He = 0.1 * t_H
        frac_C  = 8.57e-5
        frac_Ne = 1.43e-7
        frac_O  = 7.14e-8
        frac_Si = 4.29e-10

        t_C  = frac_C * t_H
        t_Ne = frac_Ne * t_H
        t_O  = frac_O * t_H
        t_Si = frac_Si * t_H

        rest_Si = t_Si
        rest_O  = t_O + rest_Si
        rest_Ne = t_Ne + rest_O
        rest_C  = t_C + rest_Ne
        rest_He = t_He + rest_C
        rest_H  = t_H + rest_He

        elementos = ['He<br>(H→He)', 'C<br>(He→C)', 'Ne<br>(C→Ne)',
                     'O<br>(Ne→O)', 'Si<br>(O→Si)', 'Fe<br>(Si→Fe)']
        tempos = [rest_H, rest_He, rest_C, rest_Ne, rest_O, rest_Si]
        return elementos, tempos

# Valores de massa para o slider (1 a 60, passo 0.5)
massas = np.arange(1.0, 60.5, 0.5)

# Criar frames
frames = []
for M in massas:
    elem, tmp = calcular_tempos(M)
    x_pos = list(range(len(elem)))

    # Trace de linha + pontos
    trace_line = go.Scatter(
        x=x_pos, y=tmp,
        mode='lines+markers',
        marker=dict(color='darkred', size=8),
        line=dict(color='darkred', width=2),
        name='Tempo restante',
        showlegend=False
    )

    # Trace de texto (valores)
    textos = [f'{t:.2e} anos' if t > 1e-10 else '0 (fim)' for t in tmp]
    trace_text = go.Scatter(
        x=x_pos, y=tmp,
        mode='text',
        text=textos,
        textposition='top center',
        textfont=dict(color='darkred', size=9),
        showlegend=False,
        hoverinfo='skip'
    )

    # Layout do frame: ajustar ticks do eixo X
    frame_layout = go.Layout(
        xaxis=dict(
            tickvals=x_pos,
            ticktext=elem
        )
    )

    frames.append(go.Frame(data=[trace_line, trace_text], layout=frame_layout, name=str(M)))

# Criar figura inicial com massa=14.0 (ou primeiro valor)
M0 = 14.0
elem0, tmp0 = calcular_tempos(M0)
x0 = list(range(len(elem0)))
textos0 = [f'{t:.2e} anos' if t > 1e-10 else '0 (fim)' for t in tmp0]

fig = go.Figure()

# Trace de linha inicial
fig.add_trace(go.Scatter(
    x=x0, y=tmp0,
    mode='lines+markers',
    marker=dict(color='darkred', size=8),
    line=dict(color='darkred', width=2),
    name='Tempo restante',
    showlegend=False
))

# Trace de texto inicial
fig.add_trace(go.Scatter(
    x=x0, y=tmp0,
    mode='text',
    text=textos0,
    textposition='top center',
    textfont=dict(color='darkred', size=9),
    showlegend=False,
    hoverinfo='skip'
))

# Configurar layout principal
fig.update_layout(
    title=f'Tempo de vida restante – estrela de {M0:.1f} M☉',
    xaxis=dict(
        title='Elemento produzido na fusão',
        tickvals=x0,
        ticktext=elem0,
        tickfont=dict(size=10)
    ),
    yaxis=dict(
        title='Tempo de vida restante (anos)',
        type='log',
        tickformat='.0e',
        showexponent='all',
        exponentformat='e'
    ),
    sliders=[dict(
        active=np.argmin(np.abs(massas - M0)),
        currentvalue={"prefix": "Massa: ", "suffix": " M☉"},
        steps=[dict(
            method='animate',
            args=[[str(m)], dict(mode='immediate', frame=dict(duration=0, redraw=True),
                                 transition=dict(duration=0))],
            label=f'{m:.1f}'
        ) for m in massas]
    )],
    updatemenus=[dict(
        type='buttons',
        buttons=[
            dict(label='▶ Play',
                 method='animate',
                 args=[None, dict(frame=dict(duration=300, redraw=True), fromcurrent=True)]),
            dict(label='⏸ Pause',
                 method='animate',
                 args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')])
        ],
        showactive=True,
        x=0.1,
        y=-0.1
    )]
)

# Adicionar frames
fig.frames = frames

# Salvar como HTML
fig.write_html('tempo_vida_restante.html')
print("Arquivo salvo como 'tempo_vida_restante.html'.")