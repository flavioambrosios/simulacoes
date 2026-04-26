import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.signal import hilbert
from matplotlib.widgets import Button, Slider
import matplotlib.patches as patches
import textwrap

class WaveControlApp:
    def __init__(self):
        """Inicializa toda a aplicação"""
        plt.close('all')
        plt.style.use('seaborn-v0_8')
        plt.rcParams.update({'font.size': 9})

        # Dados das frequências
        self.freqs = np.arange(400, 801, 10)
        self.n = len(self.freqs)
        self.t = np.linspace(0, 2e-13, 4000)
        self.amps1 = np.zeros(self.n)
        self.amps2 = np.zeros(self.n)
        self.amp_min, self.amp_max = -1, 1
        self.status_message = 'Pronto para editar e otimizar as ondas.'
        self.max_iterations = 5000
        self.show_layout_grid = True
        self.layout_grid_ax = None
        self.spinner_states = ['.', '..', '...']
        self.optimization_step = 0
        
        # Salva estado inicial
        self.amps_before = None  # Será definido quando otimizar
        self.amps_after = self.amps1.copy(), self.amps2.copy()

        # Configuração da figura
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Simulador de Ondas e Envelopes de Hilbert',
                          fontsize=17, fontweight='bold', y=0.985)
        self.fig.subplots_adjust(
            left=0.1, right=0.95,
            top=0.9, bottom=0.3,
            hspace=0.4, wspace=0.3
        )
        self._setup_layout_grid()

        # Inicializa componentes
        self._setup_plots()
        self._setup_sliders()
        self._setup_controls()
        
        # Atualiza os gráficos
        self._update_plots()
        print("Aplicativo inicializado com sucesso!")

    def _setup_plots(self):
        """Configura os eixos dos gráficos principais"""
        gs = self.fig.add_gridspec(2, 1,
                                 left=0.05, right=0.68,
                                 top=0.88, bottom=0.5,
                                 hspace=0.42)

        # Gráficos laterais
        self.ax_diff = self.fig.add_axes([0.72, 0.74, 0.23, 0.15])
        self.ax_summary = self.fig.add_axes([0.78, 0.31, 0.17, 0.09])
        self.ax_summary.axis('off')

        # Eixos principais ampliados
        self.ax_wave1 = self.fig.add_subplot(gs[0, 0])
        self.ax_wave2 = self.fig.add_subplot(gs[1, 0])

        # Configurações comuns
        for ax in [self.ax_wave1, self.ax_wave2, self.ax_diff]:
            ax.grid(True, linestyle=':', alpha=0.5)
            ax.set_xlabel('Tempo (fs)')
            ax.set_xlim(0, 200)
            ax.set_xticks(np.arange(0, 201, 25))

        for ax in [self.ax_wave1, self.ax_wave2]:
            ax.yaxis.set_label_position('left')
            ax.yaxis.tick_left()

        self.ax_diff.yaxis.set_label_position('right')
        self.ax_diff.yaxis.tick_right()

        self.fig.text(0.19, 0.34, 'Controles da Onda 1', ha='center', va='bottom',
                      fontsize=11, fontweight='bold', color='royalblue')
        self.fig.text(0.69, 0.34, 'Controles da Onda 2', ha='center', va='bottom',
                      fontsize=11, fontweight='bold', color='darkorange')
        self.fig.text(0.535, 0.405,
                      'Os controles verticais exibem amplitude por frequência; use OTIMIZAR para aproximar os envelopes.',
                      ha='center', va='bottom', fontsize=9, color='dimgray')
        self.status_text = self.fig.text(0.52, 0.355, self.status_message,
                                         ha='center', va='center', fontsize=9,
                                         bbox=dict(boxstyle='round', facecolor='white',
                                                   edgecolor='gray', alpha=0.9))

    def _update_sliders(self):
        """Atualiza os sliders para refletir os valores atuais de amps1 e amps2."""
        for i, slider in enumerate(self.sliders1):
            slider.eventson = False
            slider.set_val(self.amps1[i])
            slider.eventson = True
        for i, slider in enumerate(self.sliders2):
            slider.eventson = False
            slider.set_val(self.amps2[i])
            slider.eventson = True

    def _setup_sliders(self):
        """Configura os sliders de controle"""
        slider_width = 0.010
        slider_height = 0.16
        spacing = 0.00001

        left_group_x = 0.05
        right_group_x = 0.55
        y_position = 0.15

        self.sliders1 = []
        self.sliders2 = []

        for i, freq in enumerate(self.freqs):
            # Sliders Onda 1
            ax_left = self.fig.add_axes([left_group_x + i*(slider_width + spacing),
                                      y_position, slider_width, slider_height])
            slider_left = Slider(ax_left, '', self.amp_min, self.amp_max, valinit=0,
                               facecolor='royalblue', orientation='vertical')
            slider_left.on_changed(self._create_update_fn(1, i))
            self.sliders1.append(slider_left)
            slider_left.valtext.set_visible(False)

            # Sliders Onda 2
            ax_right = self.fig.add_axes([right_group_x + i*(slider_width + spacing),
                                       y_position, slider_width, slider_height])
            slider_right = Slider(ax_right, '', self.amp_min, self.amp_max, valinit=0,
                                facecolor='darkorange', orientation='vertical')
            slider_right.on_changed(self._create_update_fn(2, i))
            self.sliders2.append(slider_right)
            slider_right.valtext.set_visible(False)

        # Rótulos das frequências
        for i, freq in enumerate(self.freqs[::4]):
            self.fig.text(left_group_x + i*4*(slider_width + spacing), 0.125, f'{freq}',
                        rotation=0, fontsize=8, ha='center', va='top', color='dimgray')
            self.fig.text(right_group_x + i*4*(slider_width + spacing), 0.125, f'{freq}',
                        rotation=0, fontsize=8, ha='center', va='top', color='dimgray')

        # Informações de eixos que antes ficavam nos espectros
        group_width = (self.n - 1) * (slider_width + spacing) + slider_width
        for group_x, group_center, color, side in [
            (left_group_x, 0.19, 'royalblue', 'left'),
            (right_group_x, 0.69, 'darkorange', 'right')
        ]:
            axis_y = y_position - 0.008
            self.fig.add_artist(plt.Line2D([group_x, group_x + group_width], [axis_y, axis_y],
                                           transform=self.fig.transFigure,
                                           color='dimgray', linewidth=1.0))

            for idx in range(0, self.n, 4):
                tick_x = group_x + idx * (slider_width + spacing) + slider_width / 2
                self.fig.add_artist(plt.Line2D([tick_x, tick_x], [axis_y, axis_y + 0.006],
                                               transform=self.fig.transFigure,
                                               color='dimgray', linewidth=0.8))

            if side == 'left':
                label_x = group_x - 0.018
                number_x = group_x - 0.004
                number_ha = 'right'
            else:
                label_x = group_x + group_width + 0.018
                number_x = group_x + group_width + 0.004
                number_ha = 'left'

            self.fig.text(label_x, y_position + slider_height / 2, 'Amplitude',
                          rotation=90, fontsize=9, ha='center', va='center', color=color,
                          fontweight='bold')
            self.fig.text(number_x, y_position + slider_height, '1.0',
                          fontsize=8, ha=number_ha, va='center', color='dimgray')
            self.fig.text(number_x, y_position + slider_height / 2, '0.0',
                          fontsize=8, ha=number_ha, va='center', color='dimgray')
            self.fig.text(number_x, y_position, '-1.0',
                          fontsize=8, ha=number_ha, va='center', color='dimgray')
            self.fig.text(group_center, 0.095, 'Frequência (THz)',
                          fontsize=9, ha='center', va='top', color='black',
                          fontweight='bold')

    def _create_update_fn(self, wave, idx):
        """Cria a função de callback para os sliders"""
        def update(val):
            if wave == 1:
                self.amps1[idx] = val
            else:
                self.amps2[idx] = val
            self._update_plots()
        return update

    def _setup_controls(self):
        """Configura botões de controle"""
        # Botões de equações na parte superior
        fourier_before_ax = self.fig.add_axes([0.05, 0.92, 0.12, 0.03])
        self.fourier_before_btn = Button(fourier_before_ax, 'Fourier (Antes)', 
                                       color='lightblue', hovercolor='deepskyblue')
        self.fourier_before_btn.on_clicked(self._show_fourier_before)
        
        fourier_after_ax = self.fig.add_axes([0.18, 0.92, 0.12, 0.03])
        self.fourier_after_btn = Button(fourier_after_ax, 'Fourier (Depois)', 
                                      color='lightgreen', hovercolor='limegreen')
        self.fourier_after_btn.on_clicked(self._show_fourier_after)
        
        hilbert_ax = self.fig.add_axes([0.31, 0.92, 0.12, 0.03])
        self.hilbert_btn = Button(hilbert_ax, 'Envelopes Hilbert', 
                                color='lightcoral', hovercolor='red')
        self.hilbert_btn.on_clicked(self._show_hilbert_info)

        visible_colors_ax = self.fig.add_axes([0.44, 0.92, 0.12, 0.03])
        self.visible_colors_btn = Button(visible_colors_ax, 'Cores Visíveis',
                         color='moccasin', hovercolor='gold')
        self.visible_colors_btn.on_clicked(self._show_visible_colors)

        grid_ax = self.fig.add_axes([0.84, 0.935, 0.11, 0.03])
        self.grid_btn = Button(grid_ax, 'Grade: ON',
                               color='lavender', hovercolor='plum')
        self.grid_btn.on_clicked(self._toggle_layout_grid)

        # Botão de otimização
        optimize_ax = self.fig.add_axes([0.47, 0.20, 0.07, 0.04])
        self.optimize_btn = Button(optimize_ax, 'OTIMIZAR', color='#ddffdd',
                                 hovercolor='#99ff99')
        self.optimize_btn.label.set_fontweight('bold')
        self.optimize_btn.on_clicked(self._run_optimization)
        
        # Botão de reset
        reset_ax = self.fig.add_axes([0.47, 0.15, 0.07, 0.04])
        self.reset_btn = Button(reset_ax, 'ZERAR', color='#ffdddd',
                              hovercolor='#ff9999')
        self.reset_btn.label.set_fontweight('bold')
        self.reset_btn.on_clicked(self._reset_all)

        # Controle do número máximo de iterações
        max_iter_ax = self.fig.add_axes([0.36, 0.055, 0.30, 0.025])
        self.max_iter_slider = Slider(
            max_iter_ax,
            'Máx. iterações',
            1000,
            10000,
            valinit=self.max_iterations,
            valstep=500,
            color='mediumpurple'
        )
        self.max_iter_slider.valtext.set_text(str(self.max_iterations))
        self.max_iter_slider.on_changed(self._update_max_iterations)

    def _setup_layout_grid(self):
        """Cria uma grade de apoio para posicionamento visual dos componentes."""
        self.layout_grid_ax = self.fig.add_axes([0, 0, 1, 1], zorder=-1)
        self.layout_grid_ax.set_xlim(0, 1)
        self.layout_grid_ax.set_ylim(0, 1)
        self.layout_grid_ax.set_facecolor('none')
        self.layout_grid_ax.set_xticks(np.arange(0, 1.01, 0.1))
        self.layout_grid_ax.set_yticks(np.arange(0, 1.01, 0.1))
        self.layout_grid_ax.set_xticks(np.arange(0, 1.01, 0.05), minor=True)
        self.layout_grid_ax.set_yticks(np.arange(0, 1.01, 0.05), minor=True)
        self.layout_grid_ax.grid(True, which='major', linestyle='--', color='gray', alpha=0.25)
        self.layout_grid_ax.grid(True, which='minor', linestyle=':', color='gray', alpha=0.12)
        self.layout_grid_ax.tick_params(labelsize=7, colors='gray')
        for spine in self.layout_grid_ax.spines.values():
            spine.set_visible(False)

    def _toggle_layout_grid(self, event):
        """Mostra ou oculta a grade de apoio de layout."""
        self.show_layout_grid = not self.show_layout_grid
        if self.layout_grid_ax is not None:
            self.layout_grid_ax.set_visible(self.show_layout_grid)
        self.grid_btn.label.set_text('Grade: ON' if self.show_layout_grid else 'Grade: OFF')
        status = 'Grade de layout visível.' if self.show_layout_grid else 'Grade de layout oculta.'
        self._set_status(status, 'slateblue')
        self.fig.canvas.draw_idle()

    def _update_max_iterations(self, value):
        """Atualiza o limite máximo de iterações da otimização."""
        self.max_iterations = int(value)
        if hasattr(self, 'max_iter_slider'):
            self.max_iter_slider.valtext.set_text(str(self.max_iterations))
        if self.optimize_btn.label.get_text() == 'OTIMIZAR':
            self._set_status(f'Limite ajustado para {self.max_iterations} iterações.', 'purple')
        self.fig.canvas.draw_idle()

    def _show_fourier_before(self, event):
        """Mostra as equações de Fourier com as escolhas atuais (antes de otimizar)"""
        if self.amps_before is not None:
            amps1, amps2 = self.amps_before
        else:
            amps1, amps2 = self.amps1, self.amps2
        self._show_fourier_equations(amps1, amps2, "figura 2 - Fourier Antes")

    def _show_fourier_after(self, event):
        """Mostra as equações de Fourier depois da otimização"""
        self._show_fourier_equations(self.amps_after[0], self.amps_after[1], "figura 3 - Fourier Depois")

    def _show_fourier_equations(self, amps1, amps2, title_suffix):
        """Mostra as equações de Fourier em uma nova janela"""
        fig_eq = plt.figure(figsize=(11.5, 7.2))
        fig_eq.suptitle(title_suffix, fontsize=16, fontweight='bold')
        fig_eq.subplots_adjust(left=0.04, right=0.96, top=0.90, bottom=0.06)
        
        # Remove eixos para criar um quadro de texto
        ax = fig_eq.add_subplot(111)
        ax.axis('off')
        
        # Gera as equações
        eq1 = self._generate_fourier_equation(amps1, "Onda 1")
        eq2 = self._generate_fourier_equation(amps2, "Onda 2")
        
        # Texto explicativo
        explanatory = textwrap.dedent("""
Onde:
• Aₙ são as amplitudes das componentes de frequência
• fₙ são as frequências em THz (400, 410, 420, ..., 800 THz)
• t é o tempo em segundos
• A transformada de Hilbert é usada para calcular os envelopes

Forma geral da série:
y(t) = Σ [Aₙ · sin(2π · fₙ · t)]
        """).strip()
        
        # Texto completo sem wrap nas equações
        text_content = f"{eq1}\n\n{eq2}\n\n{explanatory}"
        
        # Adiciona retângulo de fundo - CORREÇÃO AQUI
        rect = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                    boxstyle="round,pad=0.02",
                                    facecolor='lightyellow',
                                    edgecolor='gold',
                                    linewidth=2)
        ax.add_patch(rect)
        
        # CORREÇÃO: Alinhamento à esquerda e posição ajustada
        ax.text(0.04, 0.96, text_content, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='left',  # Mudado para 'left'
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontfamily='monospace')
        
        plt.tight_layout()
        plt.show()

    def _show_hilbert_info(self, event):
        """Mostra informações sobre os envelopes de Hilbert"""
        fig_hilbert = plt.figure(figsize=(10.5, 6.6))
        fig_hilbert.suptitle("Envelopes de Hilbert - Teoria e Aplicação", fontsize=16, fontweight='bold')
        fig_hilbert.subplots_adjust(left=0.04, right=0.96, top=0.90, bottom=0.06)
        
        ax = fig_hilbert.add_subplot(111)
        ax.axis('off')
        
        hilbert_text = textwrap.dedent("""
    DEFINIÇÃO DO ENVELOPE DE HILBERT:

    Para um sinal real x(t), o envelope complexo é definido como:
        
        z(t) = x(t) + j·H{x(t)}
        
    Onde H{x(t)} é a transformada de Hilbert de x(t).

    O envelope de amplitude é dado pelo módulo:
        
        A(t) = |z(t)| = √[x²(t) + H²{x(t)}]

    APLICAÇÃO NESTE PROGRAMA:

    • Calculamos os envelopes usando scipy.signal.hilbert
    • envelope₁(t) = |hilbert(Onda₁(t))|
    • envelope₂(t) = |hilbert(Onda₂(t))|
    • A diferença entre envelopes é: Δ(t) = envelope₁(t) - envelope₂(t)

    INTERPRETAÇÃO FÍSICA:

    O envelope de Hilbert representa a amplitude instantânea do sinal,
    mostrando como a amplitude varia no tempo, independente da fase.

    A otimização busca minimizar a diferença máxima entre os envelopes:
        min max|Δ(t)|
        """).strip()
        
        rect = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                    boxstyle="round,pad=0.02",
                                    facecolor='lavender',
                                    edgecolor='purple',
                                    linewidth=2)
        ax.add_patch(rect)
        
        # CORREÇÃO: Alinhamento à esquerda
        ax.text(0.04, 0.97, hilbert_text, transform=ax.transAxes, fontsize=8.8,
                verticalalignment='top', horizontalalignment='left',  # Mudado para 'left'
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        plt.tight_layout()
        plt.show()

    def _frequency_to_rgb(self, freq_thz):
        """Converte uma frequência visível aproximada em uma cor RGB."""
        wavelength_nm = self._clamp_to_visible_wavelength(self._frequency_to_wavelength_nm(freq_thz))

        if 380 <= wavelength_nm < 440:
            red = -(wavelength_nm - 440) / (440 - 380)
            green = 0.0
            blue = 1.0
        elif wavelength_nm < 490:
            red = 0.0
            green = (wavelength_nm - 440) / (490 - 440)
            blue = 1.0
        elif wavelength_nm < 510:
            red = 0.0
            green = 1.0
            blue = -(wavelength_nm - 510) / (510 - 490)
        elif wavelength_nm < 580:
            red = (wavelength_nm - 510) / (580 - 510)
            green = 1.0
            blue = 0.0
        elif wavelength_nm < 645:
            red = 1.0
            green = -(wavelength_nm - 645) / (645 - 580)
            blue = 0.0
        else:
            red = 1.0
            green = 0.0
            blue = 0.0

        if 380 <= wavelength_nm < 420:
            factor = 0.3 + 0.7 * (wavelength_nm - 380) / (420 - 380)
        elif wavelength_nm < 701:
            factor = 1.0
        elif wavelength_nm <= 780:
            factor = 0.3 + 0.7 * (780 - wavelength_nm) / (780 - 700)
        else:
            factor = 0.0

        gamma = 0.8
        rgb = np.array([red, green, blue]) * factor
        rgb = np.where(rgb > 0, rgb ** gamma, 0)
        return np.clip(rgb, 0, 1)

    def _frequency_to_wavelength_nm(self, freq_thz):
        """Converte frequência em THz para comprimento de onda em nm."""
        return 299792.458 / freq_thz

    def _clamp_to_visible_wavelength(self, wavelength_nm):
        """Limita o comprimento de onda ao intervalo visível usado na paleta."""
        return float(np.clip(wavelength_nm, 380.0, 780.0))

    def _wavelength_to_color_name(self, wavelength_nm):
        """Retorna um nome aproximado da cor associada ao comprimento de onda."""
        wavelength_nm = self._clamp_to_visible_wavelength(wavelength_nm)
        if wavelength_nm < 430:
            return 'violeta'
        if wavelength_nm < 485:
            return 'azul'
        if wavelength_nm < 500:
            return 'ciano'
        if wavelength_nm < 565:
            return 'verde'
        if wavelength_nm < 590:
            return 'amarelo'
        if wavelength_nm < 625:
            return 'laranja'
        return 'vermelho'

    def _mix_visible_color(self, amps):
        """Mistura as cores visíveis ponderadas pela magnitude das amplitudes."""
        weights = np.abs(amps)
        total = np.sum(weights)
        if total <= 1e-12:
            return np.array([0.0, 0.0, 0.0])

        colors = np.array([self._frequency_to_rgb(freq) for freq in self.freqs])
        mixed = np.sum(colors * weights[:, None], axis=0) / total

        mixed = self._normalize_rgb(mixed)
        return np.clip(mixed, 0, 1)

    def _mix_spectral_color(self, amps):
        """Mistura as cores em RGB sem renormalizar o resultado final."""
        weights = np.abs(amps)
        total = np.sum(weights)
        if total <= 1e-12:
            return np.array([0.0, 0.0, 0.0])

        colors = np.array([self._frequency_to_rgb(freq) for freq in self.freqs])
        mixed = np.sum(colors * weights[:, None], axis=0) / total
        return np.clip(mixed, 0, 1)

    def _normalize_rgb(self, rgb):
        """Renormaliza um vetor RGB para usar o maior canal como referência."""
        peak = np.max(rgb)
        if peak > 1e-12:
            return rgb / peak
        return rgb

    def _frequency_to_visual_rgb(self, freq_thz):
        """Converte uma frequência para a versão RGB de visualização usada nos cartões."""
        return np.clip(self._normalize_rgb(self._frequency_to_rgb(freq_thz)), 0, 1)

    def _rgb_to_hex(self, rgb):
        """Converte um vetor RGB normalizado em string hexadecimal."""
        values = np.clip(np.round(rgb * 255), 0, 255).astype(int)
        return '#{:02X}{:02X}{:02X}'.format(*values)

    def _format_color_summary(self, amps):
        """Monta um resumo com as frequências dominantes de uma mistura."""
        weights = np.abs(amps)
        total = np.sum(weights)
        if total <= 1e-12:
            return 'Sem componentes ativas na mistura.'

        dominant_indices = np.argsort(weights)[-3:][::-1]
        parts = []
        for idx in dominant_indices:
            if weights[idx] <= 1e-12:
                continue
            fraction = 100 * weights[idx] / total
            wavelength_nm = self._frequency_to_wavelength_nm(self.freqs[idx])
            color_name = self._wavelength_to_color_name(wavelength_nm)
            parts.append(
                f'{self.freqs[idx]} THz | {wavelength_nm:.0f} nm | {color_name} ({fraction:.1f}%)'
            )

        if not parts:
            return 'Sem componentes ativas na mistura.'
        return 'Componentes dominantes:\n' + '\n'.join(parts)

    def _draw_color_card(self, ax, amps, wave_name, stage_name, color_mode='choice1'):
        """Desenha um cartão com a cor resultante para uma onda."""
        ax.clear()
        if color_mode == 'choice2':
            color = self._mix_spectral_color(amps)
            model_label = 'Paleta espectral com soma RGB'
        else:
            color = self._mix_visible_color(amps)
            model_label = 'Mistura RGB de visualização'

        hex_color = self._rgb_to_hex(color)

        ax.set_facecolor(color)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.2)

        text_color = 'white' if np.mean(color) < 0.45 else 'black'
        info_text = (
            f'{wave_name}\n'
            f'{stage_name}\n'
            f'{model_label}\n'
            f'Cor exibida: {hex_color}'
        )
        ax.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=10,
                color=text_color, fontweight='bold', wrap=True,
                bbox=dict(boxstyle='round', facecolor=(1, 1, 1, 0.18),
                          edgecolor=(0, 0, 0, 0.2)))

    def _draw_frequency_color_scale(self, ax, color_mode='choice1'):
        """Mostra a escala de cores associada a cada frequência."""
        ax.clear()
        if color_mode == 'choice1':
            title = 'Paleta visível em RGB de visualização'
            xlabel = 'Modo RGB: frequência (THz) na 1ª linha | comprimento de onda equivalente (nm) na 2ª'
        else:
            title = 'Paleta espectral convertida para RGB'
            xlabel = 'Modo Paleta espectral RGB: frequência (THz) na 1ª linha | comprimento de onda equivalente (nm) na 2ª'

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlim(-0.5, self.n - 0.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xticks(range(0, self.n, 4))
        ax.set_xticklabels(
            [f'{freq}\n{self._frequency_to_wavelength_nm(freq):.0f}' for freq in self.freqs[::4]],
            fontsize=8
        )
        ax.set_xlabel(xlabel)

        for i, freq in enumerate(self.freqs):
            if color_mode == 'choice1':
                patch_color = self._frequency_to_visual_rgb(freq)
            else:
                patch_color = self._frequency_to_rgb(freq)
            ax.add_patch(
                patches.Rectangle((i - 0.5, 0), 1, 1,
                                  facecolor=patch_color,
                                  edgecolor='white', linewidth=0.4)
            )

        for spine in ax.spines.values():
            spine.set_visible(False)

    def _show_visible_colors(self, event):
        """Abre uma janela comparando as cores antes e depois da otimização."""
        fig_colors = plt.figure(figsize=(11.2, 6.8))
        fig_colors.suptitle('Cores Visíveis', fontsize=16, fontweight='bold')
        fig_colors.subplots_adjust(left=0.05, right=0.95, top=0.83, bottom=0.11)
        gs = fig_colors.add_gridspec(3, 2, height_ratios=[0.55, 1, 1], hspace=0.35, wspace=0.18)
        mode_state = {'value': 'choice1'}

        ax_scale = fig_colors.add_subplot(gs[0, :])
        ax_before_wave1 = fig_colors.add_subplot(gs[1, 0])
        ax_after_wave1 = fig_colors.add_subplot(gs[1, 1])
        ax_before_wave2 = fig_colors.add_subplot(gs[2, 0])
        ax_after_wave2 = fig_colors.add_subplot(gs[2, 1])

        mode_description = fig_colors.text(0.5, 0.62,
            '',
            ha='center', va='center', fontsize=9.5, color='dimgray')

        before_title = fig_colors.text(0.26, 0.80, '', ha='center', va='center',
                                       fontsize=13, fontweight='bold', color='dimgray')
        after_title = fig_colors.text(0.74, 0.80, '', ha='center', va='center',
                                      fontsize=13, fontweight='bold', color='dimgray')
        bottom_note = fig_colors.text(0.5, 0.045,
                '',
                ha='center', va='center', fontsize=9.2, color='dimgray')

        def refresh_visible_colors(_event=None):
            if self.amps_before is not None:
                before1, before2 = self.amps_before
                before_label = 'Antes da otimização'
            else:
                before1, before2 = self.amps1.copy(), self.amps2.copy()
                before_label = 'Estado atual'

            after1, after2 = self.amps_after
            current_mode = mode_state['value']

            self._draw_frequency_color_scale(ax_scale, current_mode)
            self._draw_color_card(ax_before_wave1, before1, 'Onda 1', before_label, current_mode)
            self._draw_color_card(ax_after_wave1, after1, 'Onda 1', 'Após a otimização', current_mode)
            self._draw_color_card(ax_before_wave2, before2, 'Onda 2', before_label, current_mode)
            self._draw_color_card(ax_after_wave2, after2, 'Onda 2', 'Após a otimização', current_mode)

            before_title.set_text(before_label)
            after_title.set_text('Após a otimização')

            if current_mode == 'choice1':
                mode_description.set_text('Modo RGB: a barra e os cartões usam a mesma lógica RGB renormalizada de visualização.')
                bottom_note.set_text('Foco didático: visualizar a soma RGB na tela com cores mais saturadas e comparáveis entre si.')
                choice1_btn.ax.set_facecolor('lightsteelblue')
                choice2_btn.ax.set_facecolor('whitesmoke')
            else:
                mode_description.set_text('Modo Paleta espectral RGB: a barra usa a paleta visível convertida para RGB e os cartões seguem soma RGB ponderada.')
                bottom_note.set_text('Foco didático: manter a ordem espectral da paleta, mas assumir que toda exibição do monitor é mediada por RGB.')
                choice1_btn.ax.set_facecolor('whitesmoke')
                choice2_btn.ax.set_facecolor('lightsteelblue')

            fig_colors.canvas.draw_idle()

        def set_choice1(_event=None):
            mode_state['value'] = 'choice1'
            refresh_visible_colors()

        def set_choice2(_event=None):
            mode_state['value'] = 'choice2'
            refresh_visible_colors()

        choice1_ax = fig_colors.add_axes([0.43, 0.88, 0.19, 0.05])
        choice1_btn = Button(choice1_ax, 'Peleta RGB',
                             color='whitesmoke', hovercolor='aliceblue')
        choice1_btn.on_clicked(set_choice1)

        choice2_ax = fig_colors.add_axes([0.63, 0.88, 0.21, 0.05])
        choice2_btn = Button(choice2_ax, 'Paleta espectral',
                             color='whitesmoke', hovercolor='aliceblue')
        choice2_btn.on_clicked(set_choice2)

        refresh_ax = fig_colors.add_axes([0.85, 0.88, 0.10, 0.05])
        refresh_btn = Button(refresh_ax, 'Atualizar',
                             color='honeydew', hovercolor='palegreen')
        refresh_btn.on_clicked(refresh_visible_colors)
        fig_colors._choice1_ax = choice1_ax
        fig_colors._choice2_ax = choice2_ax
        fig_colors._choice1_btn = choice1_btn
        fig_colors._choice2_btn = choice2_btn
        fig_colors._refresh_ax = refresh_ax
        fig_colors._refresh_btn = refresh_btn
        fig_colors._refresh_visible_colors = refresh_visible_colors
        fig_colors._set_choice1 = set_choice1
        fig_colors._set_choice2 = set_choice2

        set_choice1()

        plt.show()

    def _generate_fourier_equation(self, amps, wave_name):
        """Gera a equação de Fourier para uma onda"""
        # Encontra componentes não nulas
        non_zero_indices = np.where(amps != 0)[0]
        
        if len(non_zero_indices) == 0:
            return f"{wave_name}: y(t) = 0"
        
        equation = f"{wave_name}: y(t) = "
        terms = []
        
        for i in non_zero_indices:
            amp = amps[i]
            freq = self.freqs[i]
            sign = "+" if amp >= 0 else "-"
            abs_amp = abs(amp)
            
            if abs_amp == 1:
                term = f"{sign} sin(2π·{freq}·t)"
            else:
                term = f"{sign} {abs_amp:.3f}·sin(2π·{freq}·t)"
            terms.append(term)
        
        # Remove o sinal do primeiro termo se positivo
        if terms[0].startswith("+ "):
            terms[0] = terms[0][2:]
        
        # Split into lines if too many terms
        if len(terms) > 5:
            # Group terms into lines of 3
            grouped_terms = []
            for j in range(0, len(terms), 3):
                group = " ".join(terms[j:j+3])
                grouped_terms.append(group)
            equation += "\n    ".join(grouped_terms)
        else:
            equation += " ".join(terms)
        return equation

    def _generate_wave(self, amps):
        """Gera uma onda a partir do vetor de amplitudes."""
        return np.sum([
            amp * np.sin(2 * np.pi * freq * 1e12 * self.t)
            for amp, freq in zip(amps, self.freqs)
        ], axis=0)

    def _compute_envelope(self, wave):
        """Calcula o envelope de Hilbert de uma onda."""
        return np.abs(hilbert(wave))

    def _max_envelope_difference(self, amps1, amps2):
        """Calcula a diferença máxima entre os envelopes de duas ondas."""
        wave1 = self._generate_wave(amps1)
        wave2 = self._generate_wave(amps2)
        return np.max(np.abs(self._compute_envelope(wave1) - self._compute_envelope(wave2)))

    def _set_status(self, message, color='black'):
        """Atualiza a mensagem de status mostrada na interface."""
        self.status_message = message
        if hasattr(self, 'status_text'):
            self.status_text.set_text(message)
            self.status_text.set_color(color)

    def _animate_optimization_status(self, iterations=0):
        """Mostra um aviso dinâmico enquanto a otimização está em andamento."""
        suffix = self.spinner_states[self.optimization_step % len(self.spinner_states)]
        message = f'Otimizando{suffix} iterações: {iterations}'
        self.optimization_step += 1
        self._set_status(message, 'darkgreen')
        self.fig.canvas.draw_idle()
        try:
            self.fig.canvas.flush_events()
        except Exception:
            pass
        if 'agg' not in plt.get_backend().lower():
            plt.pause(0.001)

    def _update_plots(self):
        """Atualiza todos os gráficos incluindo envelopes de Hilbert."""
        wave1 = self._generate_wave(self.amps1)
        wave2 = self._generate_wave(self.amps2)

        self._update_wave_plot(self.ax_wave1, wave1, 'royalblue', 'Onda 1')
        self._update_wave_plot(self.ax_wave2, wave2, 'darkorange', 'Onda 2')
        self.ax_wave2.set_xlabel('Tempo (fs)')

        envelope1 = self._compute_envelope(wave1)
        envelope2 = self._compute_envelope(wave2)
        self._update_difference_plot(wave1, wave2)

        if not hasattr(self, 'ax_hilbert'):
            self.ax_hilbert = self.fig.add_axes([0.72, 0.50, 0.23, 0.15])

        self.ax_hilbert.clear()
        self.ax_hilbert.plot(self.t * 1e15, envelope1, 'blue', label='Envelope Onda 1', alpha=0.7)
        self.ax_hilbert.plot(self.t * 1e15, envelope2, 'orange', label='Envelope Onda 2', alpha=0.7)

        self.ax_hilbert.set_title('Envelopes de Hilbert')
        self.ax_hilbert.grid(True, linestyle=':', alpha=0.5)
        self.ax_hilbert.legend()
        self.ax_hilbert.set_xlabel('Tempo (fs)')
        self.ax_hilbert.set_ylabel('Amplitude')
        self.ax_hilbert.yaxis.set_label_position('right')
        self.ax_hilbert.yaxis.tick_right()
        self.ax_hilbert.set_xlim(0, 200)
        self.ax_hilbert.set_xticks(np.arange(0, 201, 25))

        self.ax_summary.clear()
        self.ax_summary.axis('off')
        max_diff = np.max(np.abs(envelope1 - envelope2))
        summary_text = (
            f'Resumo rápido\n'
            f'• Pico Onda 1: {np.max(np.abs(wave1)):.3f}\n'
            f'• Pico Onda 2: {np.max(np.abs(wave2)):.3f}\n'
            f'• Dif. máx. envelopes: {max_diff:.3f}'
        )
        self.ax_summary.text(0.03, 0.92, summary_text, va='top', ha='left', fontsize=9,
                             bbox=dict(boxstyle='round', facecolor='aliceblue',
                                       edgecolor='steelblue', alpha=0.95))

        self.fig.canvas.draw_idle()

    def _update_wave_plot(self, ax, wave, color, title):
        """Atualiza um gráfico de onda."""
        ax.clear()
        ax.plot(self.t * 1e15, wave, color=color, alpha=0.7)
        ax.set_title(title)
        ax.set_ylabel('Amplitude')
        ax.yaxis.set_label_position('left')
        ax.yaxis.tick_left()
        ax.set_xlim(0, 200)
        ax.set_xticks(np.arange(0, 201, 25))
        ax.grid(True, linestyle=':', alpha=0.5)

    def _update_spectrum_plot(self, ax, amps, color, title):
        """Atualiza um gráfico de espectro."""
        ax.clear()
        ax.bar(self.freqs, amps, width=8, color=color, alpha=0.7)
        ax.set_title(title)
        ax.set_ylabel('Amplitude')
        ax.set_ylim(self.amp_min, self.amp_max)
        ax.set_xticks(self.freqs[::4])

    def _update_difference_plot(self, wave1, wave2):
        """Atualiza o gráfico de diferença entre os envelopes."""
        self.ax_diff.clear()

        envelope1 = self._compute_envelope(wave1)
        envelope2 = self._compute_envelope(wave2)
        diff_envelope = envelope1 - envelope2

        self.ax_diff.plot(self.t * 1e15, diff_envelope, 'green', label='Diferença entre Envelopes')
        self.ax_diff.axhline(0, color='black', linewidth=0.8, alpha=0.6)
        self.ax_diff.set_title('Diferença entre Envelopes')
        self.ax_diff.set_ylabel('Δ amplitude')
        self.ax_diff.yaxis.set_label_position('right')
        self.ax_diff.yaxis.tick_right()
        self.ax_diff.grid(True, linestyle=':', alpha=0.5)
        self.ax_diff.legend()
        self.ax_diff.set_xlabel('Tempo (fs)')
        self.ax_diff.set_xlim(0, 200)
        self.ax_diff.set_xticks(np.arange(0, 201, 25))
               
    def _reset_all(self, event):
        """Reseta todos os controles."""
        self.amps1.fill(0)
        self.amps2.fill(0)
        self.amps_before = None
        self.amps_after = self.amps1.copy(), self.amps2.copy()
        self.optimize_btn.label.set_text('OTIMIZAR')
        for slider in self.sliders1 + self.sliders2:
            slider.set_val(0)
        self._set_status('Tudo zerado. Ajuste os controles novamente.', 'firebrick')
        self._update_plots()

    def _run_optimization(self, event):
        """Otimização para minimizar a diferença entre envelopes."""
        print("Iniciando otimização...")
        self.optimize_btn.label.set_text('EM CURSO')
        self.optimization_step = 0
        self._animate_optimization_status(0)

        class OptimizationStopped(Exception):
            def __init__(self, amps_flat, diff, reason):
                self.amps_flat = amps_flat.copy()
                self.diff = diff
                self.reason = reason

        try:
            self.amps_before = self.amps1.copy(), self.amps2.copy()
            target_diff = 0.25
            max_iterations = self.max_iterations
            iteration_count = {'count': 0}

            def cost_function(amps_flat):
                amps1 = amps_flat[:self.n]
                amps2 = amps_flat[self.n:]
                return self._max_envelope_difference(amps1, amps2)

            def iteration_callback(xk):
                iteration_count['count'] += 1
                if iteration_count['count'] == 1 or iteration_count['count'] % 20 == 0:
                    self._animate_optimization_status(iteration_count['count'])

                current_diff = self._max_envelope_difference(xk[:self.n], xk[self.n:])
                if current_diff <= target_diff:
                    raise OptimizationStopped(xk, current_diff, 'target')
                if iteration_count['count'] >= max_iterations:
                    raise OptimizationStopped(xk, current_diff, 'limit')

            x0 = np.concatenate([self.amps1, self.amps2])
            bounds = [(self.amp_min, self.amp_max) for _ in range(2 * self.n)]

            stop_reason = 'partial'
            try:
                res = minimize(
                    cost_function,
                    x0,
                    method='L-BFGS-B',
                    bounds=bounds,
                    callback=iteration_callback,
                    options={'maxiter': max_iterations}
                )
                final_x = res.x
                max_diff = self._max_envelope_difference(final_x[:self.n], final_x[self.n:])
                if max_diff <= target_diff:
                    stop_reason = 'target'
                elif getattr(res, 'nit', 0) >= max_iterations:
                    stop_reason = 'limit'
            except OptimizationStopped as stopped:
                final_x = stopped.amps_flat
                max_diff = stopped.diff
                stop_reason = stopped.reason

            self.amps1 = final_x[:self.n]
            self.amps2 = final_x[self.n:]
            self._update_sliders()
            self._update_plots()
            self.optimize_btn.label.set_text('OTIMIZAR')

            self.amps_after = self.amps1.copy(), self.amps2.copy()

            print(f"Diferença máxima após otimização: {max_diff:.4f}")
            if stop_reason == 'target' or max_diff <= target_diff:
                message = f'Concluído: diferença máxima = {max_diff:.4f}'
                print("✅ Sucesso! Diferença ≤ 0.25 alcançada.")
                self._set_status(message, 'darkgreen')
            elif stop_reason == 'limit':
                message = f'Parada por limite de {max_iterations} iterações. Diferença = {max_diff:.4f}'
                print(f"⚠️ Otimização interrompida pelo limite de {max_iterations} iterações.")
                self._set_status(message, 'darkorange')
            else:
                message = f'Concluído com ajuste parcial: {max_diff:.4f}'
                print("⚠️ Otimização não atingiu o alvo de 0.25. Tente ajustar manualmente.")
                self._set_status(message, 'darkorange')

        except Exception as e:
            print(f"Erro durante a otimização: {str(e)}")
            self.optimize_btn.label.set_text('OTIMIZAR')
            self._set_status('Erro na otimização. A interface foi reiniciada.', 'firebrick')
            plt.close('all')
            self.__init__()

if __name__ == "__main__":
    try:
        plt.ion()
        app = WaveControlApp()
        print("Aplicativo inicializado. Use Ctrl+C para sair.")
        plt.show(block=True)
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")