import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# =============================================
# Funções para estrelas massivas (8 a 60 M☉)
# =============================================

def ZAMS_relation(mass):
    """Relação massa-luminosidade-temperatura para a Sequência Principal."""
    L = mass**3.5 if mass >= 0.5 else mass**2.5
    R = mass**0.8
    Teff = 5770 * (L / R**2)**0.25
    return Teff, L

def evolutionary_track_high(mass):
    """
    Trajetória evolutiva para estrelas massivas.
    Retorna: Teff, L, labels, colors, special_markers.
    """
    T_zams, L_zams = ZAMS_relation(mass)

    if mass < 25:
        # Destino: estrela de nêutrons
        Teff = [T_zams, T_zams*1.2, 4000, 50000, 1e6, 1e6]
        L = [L_zams, L_zams*10, 1000*L_zams, 5000*L_zams, 1e5, 0.01]
        labels = ['Seq. Principal', 'Supergigante Azul', 'Supergig. Vermelha',
                  'Wolf-Rayet', 'Supernova', 'Estrela de Nêutrons']
        special = [(5, '*', 300, 'cyan')]
    else:
        # Destino: buraco negro
        Teff = [T_zams, T_zams*1.2, 4000, 50000, 1e6, 1e6]
        L = [L_zams, L_zams*10, 1000*L_zams, 5000*L_zams, 1e5, 0.001]
        labels = ['Seq. Principal', 'Supergigante Azul', 'Supergig. Vermelha',
                  'Wolf-Rayet', 'Supernova', 'Buraco Negro']
        special = [(5, 'H', 300, 'black')]

    # Cores baseadas na temperatura
    colors = []
    for t in Teff:
        if t > 30000: colors.append('cyan')
        elif t > 8000: colors.append('blue')
        elif t > 4000: colors.append('yellow')
        else: colors.append('red')
    return Teff, L, labels, colors, special

# =============================================
# Construção do diagrama HR massivo
# =============================================

# ZAMS para massas de 0.5 a 60 M☉ (referência visual)
masses_zams = np.logspace(-0.3, 1.78, 100)  # 0.5 a 60
T_zams_all, L_zams_all = [], []
for m in masses_zams:
    T, L = ZAMS_relation(m)
    T_zams_all.append(T)
    L_zams_all.append(L)

fig, ax = plt.subplots(figsize=(14, 9))
plt.subplots_adjust(bottom=0.12)

ax.loglog(T_zams_all, L_zams_all, 'k-', lw=1, alpha=0.3, label='Sequência Principal (ZAMS)')
ax.invert_xaxis()
ax.set_xlabel('Temperatura efetiva (K)', fontsize=12)
ax.set_ylabel('Luminosidade (L$_\odot$)', fontsize=12)
ax.set_title('Diagrama HR – Estrelas Massivas (8 a 60 M$_\odot$)', fontsize=14, fontweight='bold')
ax.grid(True, which='both', linestyle=':', alpha=0.6)

# Novos limites expandidos: horizontal até 10⁷ K, vertical até 10¹⁰ L☉
ax.set_xlim(1e7, 2000)    # 10 milhões K a 2 mil K
ax.set_ylim(1e-4, 1e10)   # 0.0001 L☉ a 10 bilhões L☉

# Regiões de classificação (ajustadas aos novos limites)
ax.axvspan(2000, 5000, alpha=0.1, color='red')
ax.axhspan(1e3, 1e10, alpha=0.1, color='orange')
ax.text(4000, 5e7, 'Supergigantes', fontsize=10, color='orange', ha='center', va='center')
ax.axvspan(30000, 50000, alpha=0.1, color='cyan')
ax.text(40000, 2e8, 'Wolf-Rayet', fontsize=10, color='cyan', ha='center', va='center')

# Sol como referência (ponto amarelo)
ax.plot(5770, 1, 'yo', markersize=12, alpha=0.7, label='Sol (referência)')

# Inicialização com 10 M☉
mass_init = 10.0
T_ev, L_ev, labs, cols, specials = evolutionary_track_high(mass_init)

# Pontos e linha evolutiva
scat = ax.scatter(T_ev, L_ev, c=cols, s=80, edgecolors='black', zorder=5)
line, = ax.plot(T_ev, L_ev, 'k--', lw=1, alpha=0.7, zorder=4)

# Rótulos
texts = []
for i, (x, y, lab) in enumerate(zip(T_ev, L_ev, labs)):
    txt = ax.annotate(lab, (x, y), textcoords="offset points", xytext=(10, 5),
                      fontsize=9, color=cols[i])
    texts.append(txt)

# Marcadores especiais (remanescentes)
special_patches = []
for idx, style, size, col in specials:
    if style == '*':
        p = ax.scatter(T_ev[idx], L_ev[idx], marker='*', s=size, color=col, edgecolors='black', zorder=6)
    else:
        p = ax.scatter(T_ev[idx], L_ev[idx], marker='o', s=size, color='black', edgecolors='white', linewidth=2, zorder=6)
    special_patches.append(p)

# Legenda para os remanescentes
ax.plot([], [], 'k*', markersize=15, label='Estrela de Nêutrons')
ax.plot([], [], 'ko', markersize=15, markerfacecolor='black', label='Buraco Negro')
ax.legend(loc='lower left', fontsize=10)

# =============================================
# Slider de massa (8 a 60 M☉)
# =============================================
ax_slider = plt.axes([0.2, 0.03, 0.6, 0.03])
slider_mass = Slider(ax_slider, 'Massa (M$_\odot$)', 8.0, 60.0, valinit=10.0, valstep=0.1)

def update(val):
    mass = slider_mass.val
    T, L, labs, cols, specials = evolutionary_track_high(mass)

    scat.set_offsets(np.c_[T, L])
    scat.set_color(cols)
    line.set_data(T, L)

    for txt in texts:
        txt.remove()
    texts.clear()
    for i, (x, y, lab) in enumerate(zip(T, L, labs)):
        txt = ax.annotate(lab, (x, y), textcoords="offset points", xytext=(10, 5),
                          fontsize=9, color=cols[i])
        texts.append(txt)

    for p in special_patches:
        p.remove()
    special_patches.clear()
    for idx, style, size, col in specials:
        if style == '*':
            p = ax.scatter(T[idx], L[idx], marker='*', s=size, color=col, edgecolors='black', zorder=6)
        else:
            p = ax.scatter(T[idx], L[idx], marker='o', s=size, color='black', edgecolors='white', linewidth=2, zorder=6)
        special_patches.append(p)

    ax.set_title(f'Diagrama HR – Evolução de {mass:.1f} M$_\odot$', fontsize=14, fontweight='bold')
    fig.canvas.draw_idle()

slider_mass.on_changed(update)
plt.show()