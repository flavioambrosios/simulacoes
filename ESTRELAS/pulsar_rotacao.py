import numpy as np
import plotly.graph_objects as go

# Parâmetros
R_ns = 0.3
inclinacao = np.radians(30)
abertura = np.radians(8)
mag_dir = np.array([np.sin(inclinacao), 0, np.cos(inclinacao)])
terra_dir = np.array([0, np.sin(np.radians(10)), np.cos(np.radians(10))])  # direção da Terra

# Frames para ângulos de 0 a 360 graus
n_frames = 72
angles = np.linspace(0, 2*np.pi, n_frames, endpoint=False)

frames = []
for theta in angles:
    # Matriz de rotação em torno de Z
    rot = np.array([[np.cos(theta), -np.sin(theta), 0],
                    [np.sin(theta),  np.cos(theta), 0],
                    [0, 0, 1]])
    mag_rot = rot @ mag_dir

    # Eixo magnético como linha
    line_x = [-mag_rot[0]*1.6, mag_rot[0]*1.6]
    line_y = [-mag_rot[1]*1.6, mag_rot[1]*1.6]
    line_z = [-mag_rot[2]*1.6, mag_rot[2]*1.6]

    # Feixes como cones simples (setas)
    # Vamos representar apenas a direção do feixe com um segmento mais grosso
    feixe_n = np.array([mag_rot[0]*R_ns*1.2, mag_rot[1]*R_ns*1.2, mag_rot[2]*R_ns*1.2])
    feixe_s = -feixe_n

    # Intensidade do pulso (ângulo entre mag_rot e terra_dir)
    cosang = np.dot(mag_rot, terra_dir)
    intensidade = np.exp(-0.5 * ((np.arccos(np.clip(cosang,-1,1)) / abertura)**2))

    # Dados do frame
    data_frame = [
        # Esfera da estrela (fixa, mas repetimos para cada frame)
        go.Surface(
            x=R_ns * np.outer(np.cos(np.linspace(0,2*np.pi,20)), np.sin(np.linspace(0,np.pi,20))),
            y=R_ns * np.outer(np.sin(np.linspace(0,2*np.pi,20)), np.sin(np.linspace(0,np.pi,20))),
            z=R_ns * np.outer(np.ones(20), np.cos(np.linspace(0,np.pi,20))),
            colorscale=[[0,'gray'],[1,'gray']], opacity=0.6, showscale=False
        ),
        # Eixo de rotação (fixo)
        go.Scatter3d(x=[0,0], y=[0,0], z=[-1.6,1.6], mode='lines',
                     line=dict(color='black', width=4), showlegend=False),
        # Eixo magnético (rotacionado)
        go.Scatter3d(x=line_x, y=line_y, z=line_z, mode='lines',
                     line=dict(color='blue', width=4), showlegend=False),
        # Setas dos feixes
        go.Scatter3d(x=[mag_rot[0]*R_ns, feixe_n[0]], y=[mag_rot[1]*R_ns, feixe_n[1]],
                     z=[mag_rot[2]*R_ns, feixe_n[2]], mode='lines+markers',
                     line=dict(color='orange', width=6), marker=dict(size=[0,5], color='orange'),
                     showlegend=False),
        go.Scatter3d(x=[-mag_rot[0]*R_ns, feixe_s[0]], y=[-mag_rot[1]*R_ns, feixe_s[1]],
                     z=[-mag_rot[2]*R_ns, feixe_s[2]], mode='lines+markers',
                     line=dict(color='orange', width=6), marker=dict(size=[0,5], color='orange'),
                     showlegend=False),
        # Terra
        go.Scatter3d(x=[0], y=[terra_dir[1]*2], z=[terra_dir[2]*2], mode='markers+text',
                     marker=dict(color='green', size=8), text=['Terra'], textposition='top center',
                     showlegend=False),
    ]
    layout_frame = go.Layout(
        scene=dict(
            xaxis=dict(range=[-1.5,1.5]), yaxis=dict(range=[-1.5,2.5]), zaxis=dict(range=[-1.5,1.5]),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
        ),
        annotations=[dict(
            x=0.5, y=1.05, xref='paper', yref='paper',
            text=f'Intensidade do pulso: {intensidade:.2f}',
            showarrow=False, font=dict(size=14)
        )]
    )
    frames.append(go.Frame(data=data_frame, layout=layout_frame, name=f'{np.degrees(theta):.0f}°'))

# Frame inicial (theta=0)
fig = go.Figure(data=frames[0].data, layout=frames[0].layout)
fig.frames = frames

# Slider
fig.update_layout(
    title='Rotação do Pulsar (animação interativa)',
    updatemenus=[dict(type='buttons', showactive=False,
                      buttons=[dict(label='▶', method='animate',
                                    args=[None, dict(frame=dict(duration=50, redraw=True),
                                                     fromcurrent=True, mode='immediate')]),
                               dict(label='⏸', method='animate',
                                    args=[[None], dict(frame=dict(duration=0, redraw=False),
                                                        mode='immediate')])])],
    sliders=[dict(
        steps=[dict(method='animate',
                    args=[[f'{np.degrees(theta):.0f}°'],
                          dict(mode='immediate', frame=dict(duration=0, redraw=True),
                               transition=dict(duration=0))],
                    label=f'{np.degrees(theta):.0f}°') for theta in angles]
    )]
)

fig.write_html('pulsar_rotacao.html')