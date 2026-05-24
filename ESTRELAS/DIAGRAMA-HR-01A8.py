import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def ZAMS_relation(mass):
    if mass < 0.5:
        L = mass**2.5
    else:
        L = mass**3.5
    R = mass**0.8
    Teff = 5770 * (L / R**2)**0.25
    return Teff, L

def evolutionary_track_low(mass):
    T_zams, L_zams = ZAMS_relation(mass)
    if mass < 0.5:
        return [T_zams], [L_zams], ['Seq. Principal'], ['red'], []
    else:
        Teff = [T_zams, T_zams*0.7, 4000, 5000, 3000, 10000, 15000]
        L = [L_zams, L_zams*3, 100*L_zams, 50*L_zams, 200*L_zams, 500*L_zams, 0.01]
        labels = ['Seq. Principal', 'Subgigante', 'Gigante Vermelha',
                  'Ramo Horizontal', 'Supergig. Verm. (AGB)',
                  'Nebulosa Planetária', 'Anã Branca']
        colors = []
        for t in Teff:
            if t > 8000: colors.append('blue')
            elif t > 5000: colors.append('yellow')
            else: colors.append('red')
        return Teff, L, labels, colors, []

# Construção do gráfico
masses_zams = np.logspace(-0.8, 0.9, 100)  # 0.15 a 8 M☉
T_zams_all, L_zams_all = [], []
for m in masses_zams:
    T, L = ZAMS_relation(m)
    T_zams_all.append(T)
    L_zams_all.append(L)

fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(bottom=0.12)

ax.loglog(T_zams_all, L_zams_all, 'k-', lw=1, alpha=0.5, label='Sequência Principal (ZAMS)')
ax.invert_xaxis()
ax.set_xlabel('Temperatura efetiva (K)', fontsize=12)
ax.set_ylabel('Luminosidade (L$_\odot$)', fontsize=12)
ax.set_title('Diagrama HR – Estrelas de 0,1 a 8 M$_\odot$', fontsize=14, fontweight='bold')
ax.grid(True, which='both', linestyle=':', alpha=0.6)
ax.set_xlim(2e4, 2e3)
ax.set_ylim(1e-3, 1e7)  # Limite inferior para incluir anãs brancas, superior para gigantes

# Regiões
ax.axvspan(15000, 100000, alpha=0.08, color='cyan')
ax.axhspan(1e-3, 0.1, alpha=0.08, color='cyan')
ax.text(20000, 0.005, 'Anãs Brancas', fontsize=10, color='cyan')
ax.axvspan(2000, 5000, alpha=0.1, color='red')
ax.axhspan(10, 1000, alpha=0.1, color='red')
ax.text(3500, 100, 'Gigantes Vermelhas', fontsize=10, color='red')

ax.plot(5770, 1, 'yo', markersize=12, label='Sol (hoje)')

# Inicialização com massa=1
mass_init = 1.0
T_ev, L_ev, labs, cols, _ = evolutionary_track_low(mass_init)
scat = ax.scatter(T_ev, L_ev, c=cols, s=80, edgecolors='black', zorder=5)
line, = ax.plot(T_ev, L_ev, 'k--', lw=1, alpha=0.7, zorder=4)
texts = []
for i, (x, y, lab) in enumerate(zip(T_ev, L_ev, labs)):
    txt = ax.annotate(lab, (x, y), textcoords="offset points", xytext=(10,5),
                      fontsize=9, color=cols[i])
    texts.append(txt)

ax.legend(loc='lower left')

# Slider (0.1 a 8)
ax_slider = plt.axes([0.2, 0.03, 0.6, 0.03])
slider_mass = Slider(ax_slider, 'Massa (M$_\odot$)', 0.01, 8.00, valinit=1.0, valstep=0.1)

def update(val):
    mass = slider_mass.val
    T, L, labs, cols, _ = evolutionary_track_low(mass)
    scat.set_offsets(np.c_[T, L])
    scat.set_color(cols)
    line.set_data(T, L)
    for txt in texts: txt.remove()
    texts.clear()
    for i, (x, y, lab) in enumerate(zip(T, L, labs)):
        txt = ax.annotate(lab, (x, y), textcoords="offset points", xytext=(10,5),
                          fontsize=9, color=cols[i])
        texts.append(txt)
    ax.set_title(f'Diagrama HR – Evolução de {mass:.1f} M$_\odot$', fontsize=14, fontweight='bold')
    fig.canvas.draw_idle()

slider_mass.on_changed(update)
plt.show()