import matplotlib.pyplot as plt
import numpy as np

# Dados corrigidos (unidades didáticas)
elementos = ['H', 'He', 'C', 'Ne', 'O', 'Si', 'Fe']
iniciar   = [1, 1, 6, 12, 15, 27, 80]
liberada  = [100, 85, 60, 40, 30, 15, 0]
saldo     = np.array(liberada) - np.array(iniciar)   # [99, 84, 54, 28, 15, -12, -80]

x = np.arange(len(elementos))

fig, ax = plt.subplots(figsize=(10,6))

# Linhas com marcadores
ax.plot(x, iniciar,  'o-', color='orange', linewidth=2, markersize=8, label='Energia para iniciar')
ax.plot(x, liberada, 's-', color='green',  linewidth=2, markersize=8, label='Energia liberada')
ax.plot(x, saldo,    'D-', color='blue',   linewidth=2, markersize=8, label='Saldo (liberada − iniciar)')

# Linha horizontal no zero (referência crítica)
ax.axhline(y=0, color='black', linewidth=1.5, linestyle='--', alpha=0.7)

# Destacando a região de virada
ax.annotate('Saldo positivo\n(fusão vantajosa)',
            xy=(2, 54), xytext=(3.5, 70),
            arrowprops=dict(arrowstyle='->', color='gray'),
            fontsize=10, color='darkgreen')
ax.annotate('Saldo negativo\n(fusão inviável)',
            xy=(5, -12), xytext=(3.2, -45),
            arrowprops=dict(arrowstyle='->', color='gray'),
            fontsize=10, color='darkred')

# Rótulos e formatação
ax.set_xticks(x)
ax.set_xticklabels(elementos, fontsize=12)
ax.set_ylabel('Energia (unidades didáticas)', fontsize=12)
ax.set_title('Fusão estelar: o saldo energético decide até onde a estrela queima', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_ylim(-100, 120)

plt.tight_layout()
plt.show()