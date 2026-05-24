import numpy as np
import plotly.graph_objects as go

# Parâmetros
R_ns = 0.3
inclinacao = np.radians(30)
abertura_feixe = np.radians(10)
mag_dir = np.array([np.sin(inclinacao), 0, np.cos(inclinacao)])

# Estrela de nêutrons (esfera)
u = np.linspace(0, 2*np.pi, 30)
v = np.linspace(0, np.pi, 30)
x = R_ns * np.outer(np.cos(u), np.sin(v))
y = R_ns * np.outer(np.sin(u), np.sin(v))
z = R_ns * np.outer(np.ones(np.size(u)), np.cos(v))

# Eixo de rotação
z_rot = np.linspace(-1.6, 1.6, 20)
x_rot = np.zeros_like(z_rot)
y_rot = np.zeros_like(z_rot)

# Eixo magnético
z_mag = np.linspace(-1.6, 1.6, 50)
x_mag = z_mag * np.tan(inclinacao)
y_mag = np.zeros_like(z_mag)

# Cones (feixes) – simplificados como linhas de grade de um cone
theta_cone = np.linspace(0, 2*np.pi, 20)
r_cone = np.linspace(0, 1.2, 10)
Theta, R = np.meshgrid(theta_cone, r_cone)
X_cone_local = R * np.sin(abertura_feixe) * np.cos(Theta)
Y_cone_local = R * np.sin(abertura_feixe) * np.sin(Theta)
Z_cone_local = R * np.cos(abertura_feixe)

def rotate_cone(X, Y, Z, direction):
    d = direction / np.linalg.norm(direction)
    if np.allclose(d, [0,0,1]):
        e1 = np.array([1,0,0])
        e2 = np.array([0,1,0])
    else:
        e1 = np.cross(d, [0,0,1]); e1 /= np.linalg.norm(e1)
        e2 = np.cross(d, e1)
    Rmat = np.column_stack((e1, e2, d))
    Xg = Rmat[0,0]*X + Rmat[0,1]*Y + Rmat[0,2]*Z
    Yg = Rmat[1,0]*X + Rmat[1,1]*Y + Rmat[1,2]*Z
    Zg = Rmat[2,0]*X + Rmat[2,1]*Y + Rmat[2,2]*Z
    return Xg, Yg, Zg

# Vértices na superfície
vertice_norte = mag_dir * R_ns
vertice_sul = -mag_dir * R_ns

Xc_n, Yc_n, Zc_n = rotate_cone(X_cone_local, Y_cone_local, Z_cone_local, mag_dir)
Xc_s, Yc_s, Zc_s = rotate_cone(X_cone_local, Y_cone_local, Z_cone_local, -mag_dir)

# Deslocar para os vértices
Xc_n += vertice_norte[0]; Yc_n += vertice_norte[1]; Zc_n += vertice_norte[2]
Xc_s += vertice_sul[0]; Yc_s += vertice_sul[1]; Zc_s += vertice_sul[2]

# Criar figura 3D
fig = go.Figure()

# Esfera
fig.add_trace(go.Surface(x=x, y=y, z=z, colorscale=[[0,'gray'],[1,'gray']],
                         opacity=0.6, showscale=False, name='Estrela de Nêutrons'))

# Eixo de rotação
fig.add_trace(go.Scatter3d(x=x_rot, y=y_rot, z=z_rot, mode='lines',
                           line=dict(color='black', width=4), name='Eixo de Rotação'))

# Eixo magnético
fig.add_trace(go.Scatter3d(x=x_mag, y=y_mag, z=z_mag, mode='lines',
                           line=dict(color='blue', width=4), name='Eixo Magnético'))

# Cones (superfície)
fig.add_trace(go.Surface(x=Xc_n, y=Yc_n, z=Zc_n, colorscale=[[0,'gold'],[1,'gold']],
                         opacity=0.3, showscale=False, name='Feixe Norte'))
fig.add_trace(go.Surface(x=Xc_s, y=Yc_s, z=Zc_s, colorscale=[[0,'gold'],[1,'gold']],
                         opacity=0.3, showscale=False, name='Feixe Sul'))

# Terra (linha de visada)
fig.add_trace(go.Scatter3d(x=[0,0], y=[0,2], z=[0.5,0.5], mode='lines+markers',
                           line=dict(color='green', dash='dash', width=3),
                           marker=dict(color='green', size=[0,8]), name='Terra'))

# Layout
fig.update_layout(
    title='Modelo 3D do Pulsar (Farol Cósmico)',
    scene=dict(
        xaxis=dict(range=[-1.5,1.5]), yaxis=dict(range=[-1,2.5]), zaxis=dict(range=[-1.5,1.5]),
        xaxis_title='X', yaxis_title='Y', zaxis_title='Z'
    ),
    width=800, height=700
)

fig.write_html('pulsar_3d.html')