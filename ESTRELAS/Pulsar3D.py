import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Modelo 3D do Pulsar (Farol Cósmico)', fontsize=16, fontweight='bold', pad=20)

# Parâmetros
R_ns = 0.3  # raio da estrela de nêutrons (escala arbitrária)
inclinacao = np.radians(30)  # inclinação do eixo magnético em relação ao de rotação
abertura_feixe = np.radians(10)  # abertura angular do feixe

# Vetor unitário do eixo magnético (DEFINIÇÃO QUE ESTAVA FALTANDO)
mag_dir = np.array([np.sin(inclinacao), 0, np.cos(inclinacao)])

# --- Estrela de nêutrons (esfera) ---
u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 30)
x = R_ns * np.outer(np.cos(u), np.sin(v))
y = R_ns * np.outer(np.sin(u), np.sin(v))
z = R_ns * np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(x, y, z, color='gray', alpha=0.7, edgecolor='dimgray')

# --- Eixo de rotação (vertical, Z) ---
z_rot = np.array([-1.8, 1.8])
ax.plot(np.zeros_like(z_rot), np.zeros_like(z_rot), z_rot, 'k-', linewidth=3, label='Eixo de rotação')
ax.quiver(0, 0, 1.5, 0, 0, 0.5, color='black', linewidth=3, arrow_length_ratio=0.3)

# --- Eixo magnético (linha contínua) ---
z_mag_line = np.linspace(-1.6, 1.6, 50)
x_mag_line = z_mag_line * np.tan(inclinacao)
y_mag_line = np.zeros_like(z_mag_line)
ax.plot(x_mag_line, y_mag_line, z_mag_line, 'b-', linewidth=3, label='Eixo magnético')

# --- Setas nas pontas (fora da estrela) indicando o sentido do campo ---
# Ponta norte
ax.quiver(x_mag_line[-1], y_mag_line[-1], z_mag_line[-1],
          mag_dir[0]*0.3, mag_dir[1]*0.3, mag_dir[2]*0.3,
          color='blue', linewidth=2, arrow_length_ratio=0.4)
# Ponta sul
ax.quiver(x_mag_line[0], y_mag_line[0], z_mag_line[0],
          -mag_dir[0]*0.3, -mag_dir[1]*0.3, -mag_dir[2]*0.3,
          color='blue', linewidth=2, arrow_length_ratio=0.4)

# --- Cones de emissão ---
def plot_cone(ax, apex, direction, angle, length=1.2, color='gold', alpha=0.2):
    theta = np.linspace(0, 2*np.pi, 30)
    r = np.linspace(0, length, 20)
    Theta, R = np.meshgrid(theta, r)
    X_local = R * np.sin(angle) * np.cos(Theta)
    Y_local = R * np.sin(angle) * np.sin(Theta)
    Z_local = R * np.cos(angle)
    d = direction / np.linalg.norm(direction)
    if np.allclose(d, [0,0,1]):
        e1 = np.array([1,0,0])
        e2 = np.array([0,1,0])
    else:
        e1 = np.cross(d, [0,0,1])
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(d, e1)
    R_mat = np.column_stack((e1, e2, d))
    X_glob = apex[0] + R_mat[0,0]*X_local + R_mat[0,1]*Y_local + R_mat[0,2]*Z_local
    Y_glob = apex[1] + R_mat[1,0]*X_local + R_mat[1,1]*Y_local + R_mat[1,2]*Z_local
    Z_glob = apex[2] + R_mat[2,0]*X_local + R_mat[2,1]*Y_local + R_mat[2,2]*Z_local
    ax.plot_surface(X_glob, Y_glob, Z_glob, color=color, alpha=alpha, edgecolor='none')

vertice_norte = mag_dir * R_ns
vertice_sul = -mag_dir * R_ns
plot_cone(ax, vertice_norte, mag_dir, abertura_feixe, length=1.2, color='gold', alpha=0.3)
plot_cone(ax, vertice_sul, -mag_dir, abertura_feixe, length=1.2, color='gold', alpha=0.3)

# Anotar "Feixe"
ax.text(vertice_norte[0] + mag_dir[0]*1.3, vertice_norte[1] + mag_dir[1]*1.3, vertice_norte[2] + mag_dir[2]*1.3, 
        'Feixe', color='darkorange', fontsize=12, ha='center')
ax.text(vertice_sul[0] - mag_dir[0]*1.3, vertice_sul[1] - mag_dir[1]*1.3, vertice_sul[2] - mag_dir[2]*1.3, 
        'Feixe', color='darkorange', fontsize=12, ha='center')

# --- Linha de visada da Terra ---
terra_dist = 2.0
ax.plot([0, 0], [0, terra_dist], [0.5, 0.5], 'g--', linewidth=2, label='Linha de visada (Terra)')
ax.scatter(0, terra_dist, 0.5, color='green', s=100, label='Terra')
ax.text(0, terra_dist + 0.2, 0.5, 'Terra', color='green', fontsize=12)

# --- Configurações dos eixos ---
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 2.5])
ax.set_zlim([-1.5, 1.5])
ax.view_init(elev=20, azim=-60)
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()