import matplotlib.pyplot as plt
import numpy as np

# ---- Dados didáticos (energias, unidades arbitrárias) ----
elementos = ['H', 'He', 'C', 'Ne', 'O', 'Si', 'Fe']
iniciar   = [1, 1, 6, 12, 15, 27, 80]
liberada  = [100, 85, 60, 40, 30, 15, 0]
saldo     = np.array(liberada) - np.array(iniciar)   # [99, 84, 54, 28, 15, -12, -80]

# ---- Temperaturas reais (em milhões de K) ----
# Temperatura de ignição (mínima para iniciar a queima)
temp_ignicao = [15, 100, 500, 1200, 1500, 2700, np.nan]   # Fe não queima

# Temperatura central resultante (típica durante a queima, estrela massiva)
temp_central = [35, 200, 800, 1500, 2000, 3500, np.nan]   # valores aproximados

x = np.arange(len(elementos))

# ---- Gráfico ----
fig, ax1 = plt.subplots(figsize=(12, 6))

# Eixo principal: energias didáticas
ax1.plot(x, iniciar,  'o-', color='orange', linewidth=2, markersize=8,
         label='Energia p/ iniciar (didática)')
ax1.plot(x, liberada, 's-', color='green',  linewidth=2, markersize=8,
         label='Energia liberada (didática)')
ax1.plot(x, saldo,    'D-', color='blue',   linewidth=2, markersize=8,
         label='Saldo (liberada − iniciar)')
ax1.axhline(y=0, color='black', linewidth=1.5, linestyle='--', alpha=0.7)

ax1.set_ylabel('Energia (unidades didáticas)', fontsize=12)
ax1.set_ylim(-100, 120)
ax1.set_xticks(x)
ax1.set_xticklabels(elementos, fontsize=12)
ax1.set_xlabel('Elemento', fontsize=12)

# Eixo secundário: temperaturas reais
ax2 = ax1.twinx()

# Curva de temperatura de ignição
ax2.plot(x[:-1], temp_ignicao[:-1], '^--', color='darkred', linewidth=2,
         markersize=9, label='Temp. de ignição (MK)')
# Curva de temperatura central resultante
ax2.plot(x[:-1], temp_central[:-1], 'o-', color='red', linewidth=2,
         markersize=9, label='Temp. central resultante (MK)')
# Ferro: não queima, mas temperatura continua subindo (colapso)
ax2.scatter(x[-1], 5000, marker='x', color='red', s=100, zorder=5,
            label='Fe: colapso (~8 GK)')
# Opcional: anotar que a temp. central do Fe dispara
ax2.annotate('Colapso\ngravitacional',
             xy=(6, 5000), xytext=(5.5, 4000),
             arrowprops=dict(arrowstyle='->', color='gray'),
             fontsize=10, color='darkred')

ax2.set_ylabel('Temperatura (milhões de K)', fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0, 5500)

# Legenda unificada
linhas1, labels1 = ax1.get_legend_handles_labels()
linhas2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(linhas1 + linhas2, labels1 + labels2, fontsize=10, loc='upper left')

# Anotações didáticas
ax1.annotate('Saldo positivo', xy=(2, 54), xytext=(4.5, 70),
            arrowprops=dict(arrowstyle='->', color='gray'), fontsize=10, color='darkgreen')
ax1.annotate('Saldo negativo', xy=(5, -12), xytext=(3.5, -45),
            arrowprops=dict(arrowstyle='->', color='gray'), fontsize=10, color='darkred')

ax1.set_title('Fusão estelar: saldo energético e temperaturas (ignição e central)',
              fontsize=14)
ax1.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()