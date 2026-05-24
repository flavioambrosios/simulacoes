import os
import unicodedata
from datetime import datetime

import numpy as np
from dash import Dash, Input, Output, State, ctx, dcc, html, dash_table
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.optimize import minimize
from scipy.signal import hilbert


FREQS = np.arange(400, 801, 10)
N_FREQS = len(FREQS)
T = np.linspace(0, 2e-13, 4000)
T_OPT = np.linspace(0, 2e-13, 1200)
TIME_FS = T * 1e15
AMP_MIN = -1.0
AMP_MAX = 1.0
TARGET_DIFF = 0.25
ZERO_AMPS = np.zeros(N_FREQS)
BASIS = np.sin(2 * np.pi * FREQS[:, None] * 1e12 * T[None, :])
BASIS_OPT = np.sin(2 * np.pi * FREQS[:, None] * 1e12 * T_OPT[None, :])
MAX_FREQ_DELTA = int(FREQS[-1] - FREQS[0])
DEFAULT_SMOOTHING = 1
DEFAULT_FREQ_DELTA = MAX_FREQ_DELTA


def clamp_amp(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return float(np.clip(numeric, AMP_MIN, AMP_MAX))


def amps_to_table_data(amps1, amps2):
    return [
        {
            "frequencia": int(freq),
            "onda1": round(float(amp1), 1),
            "onda2": round(float(amp2), 1),
        }
        for freq, amp1, amp2 in zip(FREQS, amps1, amps2)
    ]


def table_data_to_amps(table_data):
    amps1 = []
    amps2 = []
    for row in table_data:
        amps1.append(clamp_amp(row.get("onda1", 0)))
        amps2.append(clamp_amp(row.get("onda2", 0)))
    return np.array(amps1, dtype=float), np.array(amps2, dtype=float)


def generate_wave(amps, basis=BASIS):
    return amps @ basis


def sanitize_smoothing_window(value, signal_length):
    window = max(1, int(value or 1))
    if window % 2 == 0:
        window += 1
    max_allowed = signal_length if signal_length % 2 == 1 else signal_length - 1
    window = min(window, max_allowed)
    return max(1, window)


def smooth_signal(signal, smoothing_window):
    window = sanitize_smoothing_window(smoothing_window, len(signal))
    if window <= 1:
        return signal

    pad = window // 2
    kernel = np.ones(window, dtype=float) / window
    padded = np.pad(signal, (pad, pad), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def compute_envelope(wave, smoothing_window=DEFAULT_SMOOTHING):
    envelope = np.abs(hilbert(wave))
    return smooth_signal(envelope, smoothing_window)


def max_envelope_difference(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    return float(np.max(np.abs(
        compute_envelope(wave1, smoothing_window) - compute_envelope(wave2, smoothing_window)
    )))


def max_envelope_difference_fast(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING):
    wave1 = generate_wave(amps1, BASIS_OPT)
    wave2 = generate_wave(amps2, BASIS_OPT)
    return float(np.max(np.abs(
        compute_envelope(wave1, smoothing_window) - compute_envelope(wave2, smoothing_window)
    )))


def is_frequency_delta_unrestricted(freq_delta):
    return int(freq_delta) >= MAX_FREQ_DELTA


def format_frequency_delta(freq_delta):
    if is_frequency_delta_unrestricted(freq_delta):
        return "livre"
    return f"+-{int(freq_delta)} THz"


def build_single_wave_optimization_mask(initial_amps, freq_delta):
    if is_frequency_delta_unrestricted(freq_delta):
        return np.ones(N_FREQS, dtype=bool)

    active_mask = np.abs(initial_amps) > 1e-12
    if not np.any(active_mask):
        return np.ones(N_FREQS, dtype=bool)

    active_freqs = FREQS[active_mask]
    distances = np.abs(FREQS[:, None] - active_freqs[None, :])
    return np.min(distances, axis=1) <= int(freq_delta)


def build_optimization_masks(initial_amps1, initial_amps2, freq_delta):
    return (
        build_single_wave_optimization_mask(initial_amps1, freq_delta),
        build_single_wave_optimization_mask(initial_amps2, freq_delta),
    )


def merge_optimized_values(optimized_values, base_amps1, base_amps2, optimize_masks):
    optimize_mask1, optimize_mask2 = optimize_masks
    free_count1 = int(np.sum(optimize_mask1))
    amps1 = base_amps1.copy()
    amps2 = base_amps2.copy()
    amps1[optimize_mask1] = optimized_values[:free_count1]
    amps2[optimize_mask2] = optimized_values[free_count1:]
    return amps1, amps2


def normalize_text(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    return normalized.encode("ascii", "ignore").decode("ascii").lower()


def generate_fourier_equation(amps, wave_name):
    non_zero_indices = np.where(np.abs(amps) > 1e-12)[0]
    if len(non_zero_indices) == 0:
        return f"{wave_name}: y(t) = 0"

    terms = []
    for index in non_zero_indices:
        amp = float(amps[index])
        freq = int(FREQS[index])
        sign = "+" if amp >= 0 else "-"
        abs_amp = abs(amp)
        if np.isclose(abs_amp, 1.0):
            term = f"{sign} sin(2*pi*{freq}*t)"
        else:
            term = f"{sign} {abs_amp:.3f}*sin(2*pi*{freq}*t)"
        terms.append(term)

    if terms[0].startswith("+ "):
        terms[0] = terms[0][2:]

    grouped_terms = []
    for start in range(0, len(terms), 3):
        grouped_terms.append(" ".join(terms[start:start + 3]))

    return f"{wave_name}: y(t) = " + "\n    ".join(grouped_terms)


def frequency_to_wavelength_nm(freq_thz):
    return 299792.458 / freq_thz


def clamp_to_visible_wavelength(wavelength_nm):
    return float(np.clip(wavelength_nm, 380.0, 780.0))


def frequency_to_rgb(freq_thz):
    wavelength_nm = clamp_to_visible_wavelength(frequency_to_wavelength_nm(freq_thz))

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


def normalize_rgb(rgb):
    peak = np.max(rgb)
    if peak > 1e-12:
        return rgb / peak
    return rgb


def compute_emitted_rgb(amps):
    weights = np.abs(amps)
    total = np.sum(weights)
    if total <= 1e-12:
        return np.array([0.0, 0.0, 0.0])
    colors = np.array([frequency_to_rgb(freq) for freq in FREQS])
    emitted_rgb = np.sum(colors * weights[:, None], axis=0) / total
    return np.clip(emitted_rgb, 0, 1)


def compute_display_rgb_visual(amps):
    return np.clip(normalize_rgb(compute_emitted_rgb(amps)), 0, 1)


def compute_display_rgb_palette(amps):
    return np.clip(compute_emitted_rgb(amps), 0, 1)


def rgb_to_hex(rgb):
    values = np.clip(np.round(rgb * 255), 0, 255).astype(int)
    return "#{:02X}{:02X}{:02X}".format(*values)


def format_rgb(rgb):
    return f"{rgb_to_hex(rgb)} | R={rgb[0]:.2f} G={rgb[1]:.2f} B={rgb[2]:.2f}"


def has_valid_optimization_result(current1, current2, history_data):
    if not history_data or not bool(history_data.get("has_optimization", False)):
        return False

    after1 = np.array(history_data.get("after1", current1.tolist()), dtype=float)
    after2 = np.array(history_data.get("after2", current2.tolist()), dtype=float)
    return (
        after1.shape == current1.shape
        and after2.shape == current2.shape
        and np.allclose(current1, after1, atol=1e-12)
        and np.allclose(current2, after2, atol=1e-12)
    )


GRAPH_CONFIG = {
    "displayModeBar": False,
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "doubleClick": False,
}


def lock_figure_interaction(figure):
    figure.update_xaxes(fixedrange=True)
    figure.update_yaxes(fixedrange=True)
    return figure


def build_main_figure(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1, smoothing_window)
    envelope2 = compute_envelope(wave2, smoothing_window)
    diff = envelope1 - envelope2
    envelope_title = "Envelopes"

    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Onda 1",
            "Onda 2",
            envelope_title,
            "Diferença",
        ),
        vertical_spacing=0.22,
        horizontal_spacing=0.12,
    )

    figure.add_trace(
        go.Scatter(x=TIME_FS, y=wave1, mode="lines", name="Onda 1", line=dict(color="royalblue")),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=wave2, mode="lines", name="Onda 2", line=dict(color="darkorange")),
        row=1,
        col=2,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=envelope1, mode="lines", name="Envelope 1", line=dict(color="royalblue")),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=envelope2, mode="lines", name="Envelope 2", line=dict(color="darkorange")),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(x=TIME_FS, y=diff, mode="lines", name="Delta envelopes", line=dict(color="green")),
        row=2,
        col=2,
    )
    figure.add_hline(y=0, line_width=1, line_color="black", opacity=0.5, row=2, col=2)

    for col in [1, 2]:
        figure.update_xaxes(range=[0, 200], dtick=25, row=1, col=col)
        figure.update_xaxes(title_text="Tempo (fs)", title_standoff=10, range=[0, 200], dtick=25, row=2, col=col)

    for row, col in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        figure.update_yaxes(row=row, col=col)

    figure.update_layout(
        height=820,
        template="plotly_white",
        margin=dict(l=30, r=30, t=110, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
    )
    return lock_figure_interaction(figure)


def build_intensity_figure(amps1, amps2):
    figure = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Controle de Onda 1",
            "Controle de Onda 2",
        ),
        horizontal_spacing=0.1,
    )

    figure.add_trace(
        go.Bar(
            x=FREQS,
            y=amps1,
            name="Onda 1",
            marker=dict(color=[rgb_to_hex(normalize_rgb(frequency_to_rgb(freq))) for freq in FREQS]),
            hovertemplate="%{x} THz<br>Amplitude: %{y:.1f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Bar(
            x=FREQS,
            y=amps2,
            name="Onda 2",
            marker=dict(color=[rgb_to_hex(normalize_rgb(frequency_to_rgb(freq))) for freq in FREQS]),
            hovertemplate="%{x} THz<br>Amplitude: %{y:.1f}<extra></extra>",
        ),
        row=1,
        col=2,
    )

    for col in [1, 2]:
        figure.update_xaxes(title_text="Frequência (THz)", dtick=40, row=1, col=col)
        figure.update_yaxes(title_text="Amplitude", range=[AMP_MIN, AMP_MAX], row=1, col=col)

    figure.update_layout(
        height=360,
        template="plotly_white",
        margin=dict(l=30, r=30, t=60, b=30),
        showlegend=False,
    )
    return lock_figure_interaction(figure)


def build_summary(amps1, amps2, smoothing_window=DEFAULT_SMOOTHING, freq_delta=DEFAULT_FREQ_DELTA):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1, smoothing_window)
    envelope2 = compute_envelope(wave2, smoothing_window)
    max_diff = float(np.max(np.abs(envelope1 - envelope2)))
    return html.Ul(
        [
            html.Li(f"Pico da Onda 1: {np.max(np.abs(wave1)):.3f}"),
            html.Li(f"Pico da Onda 2: {np.max(np.abs(wave2)):.3f}"),
            html.Li(f"Diferença máxima entre envelopes: {max_diff:.3f}"),
            html.Li("Envelopes: comparam a intensidade instantânea das duas ondas após o cálculo de Hilbert."),
            html.Li("Diferença: mostra quanto os envelopes ainda estão afastados em cada instante de tempo."),
            html.Li(f"Componentes ativas na Onda 1: {int(np.sum(np.abs(amps1) > 1e-12))}"),
            html.Li(f"Componentes ativas na Onda 2: {int(np.sum(np.abs(amps2) > 1e-12))}"),
            html.Li(f"Suavização de Hilbert: {sanitize_smoothing_window(smoothing_window, len(T))} ponto(s)"),
            html.Li(f"Janela da otimização em delta f: {format_frequency_delta(freq_delta)}"),
        ],
        style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.7"},
    )


def build_color_scale_figure(mode):
    if mode == "visual":
        colors = [rgb_to_hex(normalize_rgb(frequency_to_rgb(freq))) for freq in FREQS]
        title = "Escala de cores por frequência no modo RGB visual"
    else:
        colors = [rgb_to_hex(frequency_to_rgb(freq)) for freq in FREQS]
        title = "Escala de cores por frequência no modo paleta em RGB"

    figure = go.Figure(
        go.Bar(
            x=[str(freq) for freq in FREQS],
            y=[1] * len(FREQS),
            marker_color=colors,
            hovertext=[f"{freq} THz | {frequency_to_wavelength_nm(freq):.1f} nm" for freq in FREQS],
            hoverinfo="text",
        )
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        height=260,
        margin=dict(l=30, r=30, t=60, b=80),
        yaxis=dict(visible=False),
        xaxis=dict(title="Frequência (THz)"),
        bargap=0,
        showlegend=False,
    )
    return lock_figure_interaction(figure)


def build_rgb_card(amps, wave_name, stage_name, mode):
    emitted_rgb = compute_emitted_rgb(amps)
    if mode == "visual":
        displayed_rgb = compute_display_rgb_visual(amps)
        mode_label = "RGB visual renormalizado"
    else:
        displayed_rgb = compute_display_rgb_palette(amps)
        mode_label = "Paleta em RGB"

    background = rgb_to_hex(displayed_rgb)
    text_color = "white" if np.mean(displayed_rgb) < 0.45 else "black"
    return html.Div(
        [
            html.Strong(f"{wave_name} | {stage_name}"),
            html.Div(mode_label, style={"marginTop": "6px"}),
            html.Div(f"Emite: {format_rgb(emitted_rgb)}", style={"marginTop": "10px"}),
            html.Div(f"Mostra: {format_rgb(displayed_rgb)}", style={"marginTop": "4px"}),
        ],
        style={
            "background": background,
            "color": text_color,
            "padding": "16px",
            "borderRadius": "12px",
            "border": "1px solid rgba(0, 0, 0, 0.18)",
            "boxShadow": "0 8px 18px rgba(15, 23, 42, 0.08)",
            "lineHeight": "1.6",
            "minHeight": "140px",
        },
    )


def build_pending_rgb_card(wave_name, stage_name):
    return html.Div(
        [
            html.Strong(f"{wave_name} | {stage_name}"),
            html.Div("Aguardando otimização", style={"marginTop": "6px"}),
            html.Div("Este cartão só é preenchido depois que a otimização é executada.", style={"marginTop": "10px"}),
        ],
        style={
            "background": "#e2e8f0",
            "color": "#334155",
            "padding": "16px",
            "borderRadius": "12px",
            "border": "1px dashed rgba(51, 65, 85, 0.35)",
            "boxShadow": "0 8px 18px rgba(15, 23, 42, 0.04)",
            "lineHeight": "1.6",
            "minHeight": "140px",
        },
    )


def optimize_amplitudes(
    initial_amps1,
    initial_amps2,
    max_iterations,
    smoothing_window=DEFAULT_SMOOTHING,
    freq_delta=DEFAULT_FREQ_DELTA,
):
    class OptimizationStopped(Exception):
        def __init__(self, amps_flat, diff, reason):
            self.amps_flat = amps_flat.copy()
            self.diff = diff
            self.reason = reason

    optimize_masks = build_optimization_masks(initial_amps1, initial_amps2, freq_delta)
    optimize_mask1, optimize_mask2 = optimize_masks
    free_count1 = int(np.sum(optimize_mask1))
    free_count2 = int(np.sum(optimize_mask2))
    free_count = free_count1 + free_count2

    if free_count == 0:
        final_diff = max_envelope_difference(initial_amps1, initial_amps2, smoothing_window)
        return initial_amps1.copy(), initial_amps2.copy(), final_diff, "blocked"

    def cost_function(amps_flat):
        amps1, amps2 = merge_optimized_values(amps_flat, initial_amps1, initial_amps2, optimize_masks)
        return max_envelope_difference_fast(amps1, amps2, smoothing_window)

    iteration_counter = {"count": 0}

    def iteration_callback(xk):
        iteration_counter["count"] += 1
        amps1, amps2 = merge_optimized_values(xk, initial_amps1, initial_amps2, optimize_masks)
        current_diff = max_envelope_difference_fast(amps1, amps2, smoothing_window)
        if current_diff <= TARGET_DIFF:
            raise OptimizationStopped(xk, current_diff, "target")
        if iteration_counter["count"] >= max_iterations:
            raise OptimizationStopped(xk, current_diff, "limit")

    x0 = np.concatenate([initial_amps1[optimize_mask1], initial_amps2[optimize_mask2]])
    bounds = [(AMP_MIN, AMP_MAX) for _ in range(free_count)]

    initial_diff = max_envelope_difference_fast(initial_amps1, initial_amps2, smoothing_window)
    if initial_diff <= TARGET_DIFF:
        final_diff = max_envelope_difference(initial_amps1, initial_amps2, smoothing_window)
        return initial_amps1.copy(), initial_amps2.copy(), final_diff, "target"

    try:
        result = minimize(
            cost_function,
            x0,
            method="L-BFGS-B",
            bounds=bounds,
            callback=iteration_callback,
            options={"maxiter": int(max_iterations)},
        )
        final_amps1, final_amps2 = merge_optimized_values(result.x, initial_amps1, initial_amps2, optimize_masks)
        fast_diff = max_envelope_difference_fast(final_amps1, final_amps2, smoothing_window)
        final_diff = max_envelope_difference(final_amps1, final_amps2, smoothing_window)
        if fast_diff <= TARGET_DIFF or final_diff <= TARGET_DIFF:
            reason = "target"
        elif getattr(result, "nit", 0) >= max_iterations:
            reason = "limit"
        else:
            reason = "partial"
    except OptimizationStopped as stopped:
        final_amps1, final_amps2 = merge_optimized_values(stopped.amps_flat, initial_amps1, initial_amps2, optimize_masks)
        final_diff = stopped.diff
        reason = stopped.reason

    return final_amps1, final_amps2, final_diff, reason


def build_hilbert_notes(smoothing_window, freq_delta):
    smoothing_window = sanitize_smoothing_window(smoothing_window, len(T))
    smoothing_text = (
        f"Suavização adicional atual: desligada (janela = {smoothing_window} ponto)."
        if smoothing_window <= 1
        else f"Suavização adicional atual: média móvel de {smoothing_window} pontos após o módulo de Hilbert."
    )
    delta_text = (
        "Janela atual da otimização: toda a faixa espectral está liberada."
        if is_frequency_delta_unrestricted(freq_delta)
        else f"Janela atual da otimização: apenas frequências dentro de +- {int(freq_delta)} THz das componentes iniciais podem variar."
    )
    return smoothing_text, delta_text


def generate_random_exercise(previous_id=None):
    seed = int(datetime.now().timestamp() * 1000000) % 1000000000
    rng = np.random.default_rng(seed)
    target_diff = float(rng.choice([0.35, 0.30, 0.25]))
    target_smoothing = int(rng.choice([5, 9, 13, 17]))
    target_delta = int(rng.choice([40, 60, 80, 100]))

    exercises = [
        {
            "type": "envelope-target",
            "title": "Exercicio: aproximar envelopes",
            "difficulty": "fundamental",
            "prompt": (
                f"Tente fazer os dois envelopes ficarem mais parecidos. Voce pode ajustar manualmente ou usar a otimizacao. "
                f"O objetivo e deixar a diferenca maxima menor ou igual a {target_diff:.2f}. "
                "Ao final, escreva uma conclusao bem curta dizendo o que aconteceu com a diferenca entre os envelopes."
            ),
            "checklist": [
                f"A meta e: diferenca maxima <= {target_diff:.2f}.",
                "Observe se os envelopes ficaram mais proximos ao longo do tempo.",
                "Escreva uma conclusao bem curta antes de enviar.",
            ],
            "keyword_groups": [["envelope", "envelopes"], ["diferenca", "aproximou", "reduziu"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_diff": target_diff,
        },
        {
            "type": "smoothing-observe",
            "title": "Exercicio: observar a suavizacao",
            "difficulty": "intermediario",
            "prompt": (
                f"Aumente a suavizacao de Hilbert para pelo menos {target_smoothing} pontos e observe com calma o grafico dos envelopes. "
                "Depois, descreva em uma frase curta o que mudou nos picos e nas variacoes mais rapidas do grafico."
            ),
            "checklist": [
                f"Ajuste o controle para suavizacao >= {target_smoothing} pontos.",
                "Descreva o efeito visual da suavizacao no grafico.",
                "Use uma explicacao curta e objetiva.",
            ],
            "keyword_groups": [["suavizacao", "suavizar", "media"], ["pico", "variacao", "oscilacao"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_smoothing": target_smoothing,
        },
        {
            "type": "frequency-window",
            "title": "Exercicio: limitar frequencias da otimizacao",
            "difficulty": "intermediario",
            "prompt": (
                f"Defina delta f em no maximo {target_delta} THz. Deixe pelo menos uma frequencia ativa em cada onda e execute a otimizacao. "
                "Na conclusao, explique em uma frase curta por que esse limite ajuda a evitar frequencias novas muito distantes das iniciais."
            ),
            "checklist": [
                f"Ajuste o controle para delta f <= {target_delta} THz.",
                "Mantenha ao menos uma componente ativa em cada onda.",
                "Explique a ideia da restricao espectral com suas palavras.",
            ],
            "keyword_groups": [["frequencia", "espectral", "delta"], ["distante", "janela", "restricao"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_delta": target_delta,
        },
        {
            "type": "color-compare",
            "title": "Exercicio: relacionar envelope e cor",
            "difficulty": "avancado",
            "prompt": (
                f"Use a otimizacao para atingir diferenca maxima menor ou igual a {target_diff:.2f}. Depois, abra o Lab RGB e compare os cartoes Antes da otimizacao e Depois da otimizacao. "
                "Na conclusao, diga em uma frase curta se a aproximacao dos envelopes mudou muito ou pouco a cor mostrada na tela."
            ),
            "checklist": [
                f"A meta e: diferenca maxima <= {target_diff:.2f}.",
                "Use o Lab RGB para comparar antes e depois.",
                "Explique a relacao observada entre envelopes e cor.",
            ],
            "keyword_groups": [["cor", "rgb", "cartao"], ["envelope", "mudanca", "comparacao"]],
            "min_keyword_groups": 0,
            "min_words": 4,
            "target_diff": target_diff,
        },
    ]

    if previous_id is not None and len(exercises) > 1:
        previous_type = str(previous_id).split("-", 1)[0]
        filtered = [exercise for exercise in exercises if exercise["type"] != previous_type]
        if filtered:
            exercises = filtered

    index = int(rng.integers(0, len(exercises)))
    exercise = exercises[index]
    exercise["id"] = f"{exercise['type']}-{seed}"
    return exercise


def build_exercise_rubric(exercise):
    return html.Ul(
        [html.Li(item) for item in exercise.get("checklist", [])],
        style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.8"},
    )


def build_exercise_feedback(feedback=None):
    if feedback is None:
        feedback = {
            "title": "Pronto para comecar",
            "message": "Clique em Sortear novo exercicio para gerar uma atividade ou responda o exercicio atual com os dados da simulacao.",
            "details": [],
            "accent": "#2563eb",
            "background": "#eff6ff",
        }

    return html.Div(
        [
            html.Strong(feedback["title"]),
            html.P(feedback["message"], style={"margin": "10px 0 0 0", "lineHeight": "1.7"}),
            html.Ul(
                [html.Li(detail) for detail in feedback.get("details", [])],
                style={"margin": "10px 0 0 0", "paddingLeft": "18px", "lineHeight": "1.7"},
            ) if feedback.get("details") else html.Div(),
        ],
        style={
            "border": f"1px solid {feedback['accent']}",
            "background": feedback["background"],
            "borderRadius": "12px",
            "padding": "14px 16px",
            "marginTop": "14px",
        },
    )


def build_exercise_progress_panel(progress_data):
    attempts = int(progress_data.get("attempts", 0))
    correct = int(progress_data.get("correct", 0))
    partial = int(progress_data.get("partial", 0))
    incorrect = int(progress_data.get("incorrect", 0))
    streak = int(progress_data.get("streak", 0))
    best_streak = int(progress_data.get("best_streak", 0))
    best_score = int(progress_data.get("best_score", 0))
    last_score = int(progress_data.get("last_score", 0))
    history_entries = progress_data.get("history", [])[-5:][::-1]
    accuracy = 0.0 if attempts == 0 else 100.0 * correct / attempts

    return html.Div(
        [
            html.Div(
                [
                    html.Div([
                        html.Strong("Tentativas"),
                        html.Div(str(attempts), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#eff6ff"}),
                    html.Div([
                        html.Strong("Acertos"),
                        html.Div(str(correct), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#ecfdf5"}),
                    html.Div([
                        html.Strong("Parciais"),
                        html.Div(str(partial), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#fef3c7"}),
                    html.Div([
                        html.Strong("Precisao"),
                        html.Div(f"{accuracy:.0f}%", style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#fff7ed"}),
                    html.Div([
                        html.Strong("Sequencia"),
                        html.Div(str(streak), style={"fontSize": "1.5rem", "marginTop": "6px"}),
                    ], style={"padding": "12px", "borderRadius": "12px", "background": "#ede9fe"}),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(110px, 1fr))", "gap": "12px"},
            ),
            html.P(
                f"Ultima pontuacao: {last_score}/100 | Melhor pontuacao: {best_score}/100 | Melhor sequencia: {best_streak}.",
                style={"marginTop": "14px", "marginBottom": "0", "color": "#475569", "lineHeight": "1.7"},
            ),
            html.H4("Ultimos envios", style={"marginTop": "18px", "marginBottom": "10px"}),
            html.Ul(
                [
                    html.Li(
                        f"{entry['timestamp']} | {entry['title']} | {entry['result']} | {entry['score']}/100 | {entry['metric']}"
                    )
                    for entry in history_entries
                ],
                style={"margin": "0", "paddingLeft": "18px", "lineHeight": "1.8"},
            ) if history_entries else html.P(
                "Nenhum envio registrado ainda. O progresso ficara salvo neste navegador.",
                style={"margin": "0", "lineHeight": "1.7"},
            ),
            html.P(
                f"Erros registrados: {incorrect}. Cada novo envio atualiza o historico salvo localmente.",
                style={"marginTop": "16px", "color": "#475569", "lineHeight": "1.7"},
            ),
        ]
    )


def collect_simulation_metrics(table_data, history_data, smoothing_window, freq_delta):
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    amps1, amps2 = table_data_to_amps(table_data)
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1, smoothing_window)
    envelope2 = compute_envelope(wave2, smoothing_window)
    active_count1 = int(np.sum(np.abs(amps1) > 1e-12))
    active_count2 = int(np.sum(np.abs(amps2) > 1e-12))
    valid_optimization = has_valid_optimization_result(amps1, amps2, history_data)

    if valid_optimization:
        optimized_diff = history_data.get("after_diff")
        if optimized_diff is None:
            optimized_diff = max_envelope_difference(amps1, amps2, smoothing_window)
        max_diff = float(optimized_diff)
    else:
        max_diff = float(np.max(np.abs(envelope1 - envelope2)))

    return {
        "max_diff": max_diff,
        "smoothing_window": sanitize_smoothing_window(smoothing_window, len(T)),
        "freq_delta": int(freq_delta),
        "active_count1": active_count1,
        "active_count2": active_count2,
        "has_optimization": valid_optimization,
    }


def evaluate_exercise(exercise, metrics, answer_text):
    answer_normalized = normalize_text(answer_text)
    answer_word_count = len([word for word in answer_normalized.split() if word])
    keyword_groups = exercise.get("keyword_groups", [])
    matched_groups = 0
    missing_topics = []

    for group in keyword_groups:
        if any(keyword in answer_normalized for keyword in group):
            matched_groups += 1
        else:
            missing_topics.append(group[0])

    min_keyword_groups = int(exercise.get("min_keyword_groups", len(keyword_groups)))
    min_words = int(exercise.get("min_words", 4))
    keyword_score = 0.0 if len(keyword_groups) == 0 else matched_groups / len(keyword_groups)
    depth_score = min(1.0, answer_word_count / max(1, min_words))
    text_score = max(depth_score, 0.45 * keyword_score + 0.55 * depth_score)
    text_pass = answer_word_count >= min_words and (min_keyword_groups <= 0 or matched_groups >= min_keyword_groups)
    numeric_pass = False
    metric_message = ""
    numeric_score = 0.0

    if exercise["type"] == "envelope-target":
        numeric_pass = metrics["max_diff"] <= float(exercise["target_diff"])
        numeric_score = 1.0 if numeric_pass else min(1.0, float(exercise["target_diff"]) / max(metrics["max_diff"], 1e-9))
        metric_message = f"Diferença atual: {metrics['max_diff']:.3f}. Meta: <= {exercise['target_diff']:.2f}."
    elif exercise["type"] == "smoothing-observe":
        numeric_pass = metrics["smoothing_window"] >= int(exercise["target_smoothing"])
        numeric_score = min(1.0, metrics["smoothing_window"] / max(1, int(exercise["target_smoothing"])))
        metric_message = (
            f"Suavização atual: {metrics['smoothing_window']} ponto(s). "
            f"Meta: >= {exercise['target_smoothing']} ponto(s)."
        )
    elif exercise["type"] == "frequency-window":
        delta_ratio = min(1.0, int(exercise["target_delta"]) / max(metrics["freq_delta"], 1))
        active_ratio = 0.5 * int(metrics["active_count1"] > 0) + 0.5 * int(metrics["active_count2"] > 0)
        optimization_ratio = 1.0 if metrics["has_optimization"] else 0.0
        numeric_pass = (
            metrics["freq_delta"] <= int(exercise["target_delta"])
            and metrics["active_count1"] > 0
            and metrics["active_count2"] > 0
        )
        numeric_score = 0.5 * delta_ratio + 0.25 * active_ratio + 0.25 * optimization_ratio
        metric_message = (
            f"delta f atual: {metrics['freq_delta']} THz. Meta: <= {exercise['target_delta']} THz. "
            f"Otimizacao executada: {'sim' if metrics['has_optimization'] else 'nao'}."
        )
    elif exercise["type"] == "color-compare":
        numeric_pass = metrics["max_diff"] <= float(exercise["target_diff"])
        diff_ratio = min(1.0, float(exercise["target_diff"]) / max(metrics["max_diff"], 1e-9))
        optimization_ratio = 1.0 if metrics["has_optimization"] else 0.0
        numeric_score = 0.75 * diff_ratio + 0.25 * optimization_ratio
        metric_message = (
            f"Diferença atual: {metrics['max_diff']:.3f}. Meta: <= {exercise['target_diff']:.2f}. "
            f"Otimizacao executada: {'sim' if metrics['has_optimization'] else 'nao'}."
        )

    total_score = int(round((0.65 * numeric_score + 0.35 * text_score) * 100))
    passed = numeric_pass and text_pass
    partial = (numeric_pass or total_score >= 55) and not passed
    details = [metric_message]
    details.append(
        f"Conclusao textual: {matched_groups}/{max(1, len(keyword_groups))} topico(s) essenciais identificados em {answer_word_count} palavra(s)."
    )
    details.append(f"Pontuacao da tentativa: {total_score}/100.")
    if missing_topics and not text_pass:
        details.append("Sugestao para a conclusao: inclua termos ligados a " + ", ".join(missing_topics[:2]) + ".")
    if answer_word_count < min_words:
        details.append(f"A conclusao ainda esta curta. Tente usar pelo menos {min_words} palavras.")

    if passed:
        feedback = {
            "title": "Acerto registrado",
            "message": "Envio recebido com criterio numerico e conclusao textual consistentes.",
            "details": details,
            "accent": "#15803d",
            "background": "#ecfdf5",
        }
    elif partial:
        feedback = {
            "title": "Envio registrado com avanço parcial",
            "message": "A conclusao foi salva. Houve progresso, mas a meta numerica ou a analise textual ainda pode melhorar.",
            "details": details,
            "accent": "#b45309",
            "background": "#fffbeb",
        }
    else:
        feedback = {
            "title": "Envio registrado",
            "message": "A conclusao foi salva mesmo sem atingir a meta do exercicio nesta tentativa.",
            "details": details,
            "accent": "#c2410c",
            "background": "#fff7ed",
        }

    metric_summary = metric_message.replace("Meta: ", "meta ")
    result_label = "acerto" if passed else "parcial" if partial else "erro"
    return passed, partial, total_score, feedback, metric_summary, result_label


def build_mobile_active_summary(table_data):
        if table_data is None:
                table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)

        amps1, amps2 = table_data_to_amps(table_data)
        active_wave1 = [str(int(freq)) for freq, amp in zip(FREQS, amps1) if abs(amp) > 1e-12]
        active_wave2 = [str(int(freq)) for freq, amp in zip(FREQS, amps2) if abs(amp) > 1e-12]

        def summarize(freqs):
                if not freqs:
                        return "nenhuma ativa"
                preview = ", ".join(freqs[:6])
                if len(freqs) > 6:
                        preview += ", ..."
                return preview + " THz"

        return html.Div(
                [
                        html.Strong("Resumo rapido das frequencias ativas"),
                        html.Div(f"Onda 1: {summarize(active_wave1)}", style={"marginTop": "8px"}),
                        html.Div(f"Onda 2: {summarize(active_wave2)}", style={"marginTop": "4px"}),
                ],
                style={"lineHeight": "1.7"},
        )


def clone_figure_for_mobile(figure, height, top_margin=58):
    cloned = go.Figure(figure)
    for trace in cloned.data:
        if getattr(trace, "type", None) == "scatter" and "lines" in str(getattr(trace, "mode", "")):
            trace.line.width = 1.4
    for shape in cloned.layout.shapes or []:
        if hasattr(shape, "line"):
            shape.line.width = min(getattr(shape.line, "width", 1), 1)
    cloned.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=top_margin, b=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
    )
    return cloned


def build_mobile_visual_content(view_name, intensity_figure, main_figure, scale_figure, cards, summary_box, control_note):
        if view_name == "controls":
                return html.Div(
                        [
                                html.H4("Controle das amplitudes", style={"marginBottom": "10px"}),
                                dcc.Graph(
                                        figure=clone_figure_for_mobile(intensity_figure, 300),
                                    config=GRAPH_CONFIG,
                                ),
                        ]
                )

        if view_name == "rgb":
                return html.Div(
                        [
                                html.H4("Lab RGB no celular", style={"marginBottom": "10px"}),
                                dcc.Graph(
                                        figure=clone_figure_for_mobile(scale_figure, 240),
                                    config=GRAPH_CONFIG,
                                ),
                                html.Div(
                                        cards,
                                        style={
                                                "display": "grid",
                                                "gridTemplateColumns": "1fr",
                                                "gap": "12px",
                                                "marginTop": "12px",
                                        },
                                ),
                        ]
                )

        if view_name == "summary":
                return html.Div(
                        [
                                html.H4("Resumo da simulacao", style={"marginBottom": "10px"}),
                                html.Div(
                                        [summary_box],
                                        style={
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "14px",
                                                "background": "#ffffff",
                                        },
                                ),
                                html.Div(
                                        [control_note],
                                        style={
                                                "marginTop": "12px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "14px",
                                                "background": "#ffffff",
                                        },
                                ),
                        ]
                )

        return html.Div(
                [
                        html.H4("Ondas, envelopes e diferenca", style={"marginBottom": "10px"}),
                        dcc.Graph(
                    figure=clone_figure_for_mobile(main_figure, 620, top_margin=88),
                            config=GRAPH_CONFIG,
                        ),
                ]
        )


app = Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1"}],
)
server = app.server

initial_history = {
    "before1": ZERO_AMPS.tolist(),
    "before2": ZERO_AMPS.tolist(),
    "after1": ZERO_AMPS.tolist(),
    "after2": ZERO_AMPS.tolist(),
    "after_diff": None,
    "has_optimization": False,
}

initial_exercise_progress = {
    "attempts": 0,
    "correct": 0,
    "partial": 0,
    "incorrect": 0,
    "streak": 0,
    "best_streak": 0,
    "last_score": 0,
    "best_score": 0,
    "history": [],
}

initial_exercise = generate_random_exercise()

app.layout = html.Div(
    [
        dcc.Store(id="history-store", data=initial_history),
        dcc.Store(id="exercise-store", data=initial_exercise, storage_type="local"),
        dcc.Store(id="exercise-progress-store", data=initial_exercise_progress, storage_type="local"),
        html.H1("Simulador de Ondas e Envelopes de Hilbert - Versão Web"),
        html.P(
            "Esta versão foi adaptada para navegador. As janelas do programa original foram preservadas como abas da página, o que funciona melhor para uso online.",
            style={"lineHeight": "1.6"},
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Simulador",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("Controles das amplitudes"),
                                        html.P(
                                            "Edite os valores das colunas Onda 1 e Onda 2. Cada linha corresponde a uma frequência em THz.",
                                            style={"lineHeight": "1.6"},
                                        ),
                                        html.Div(
                                            className="desktop-only",
                                            children=[
                                                dash_table.DataTable(
                                                    id="amp-table",
                                                    columns=[
                                                        {"name": "Freq. (THz)", "id": "frequencia", "editable": False},
                                                        {"name": "Onda 1", "id": "onda1", "editable": True},
                                                        {"name": "Onda 2", "id": "onda2", "editable": True},
                                                    ],
                                                    data=amps_to_table_data(ZERO_AMPS, ZERO_AMPS),
                                                    editable=True,
                                                    persistence=True,
                                                    persisted_props=["data"],
                                                    persistence_type="local",
                                                    style_table={
                                                        "height": "520px",
                                                        "overflowY": "auto",
                                                        "overflowX": "auto",
                                                        "border": "1px solid #d7deea",
                                                    },
                                                    style_header={
                                                        "fontWeight": "bold",
                                                        "backgroundColor": "#eef4ff",
                                                        "fontSize": "11px",
                                                        "whiteSpace": "normal",
                                                        "height": "auto",
                                                    },
                                                    style_cell={
                                                        "textAlign": "center",
                                                        "padding": "4px",
                                                        "fontSize": "11px",
                                                        "minWidth": "60px",
                                                        "width": "60px",
                                                        "maxWidth": "60px",
                                                    },
                                                )
                                            ],
                                        ),
                                        html.Div(
                                            className="mobile-only mobile-card",
                                            children=[
                                                html.P(
                                                    "No celular, a edicao acontece uma frequencia por vez. Escolha a frequencia, ajuste os dois valores e toque em Aplicar.",
                                                    style={"marginTop": "0", "lineHeight": "1.7"},
                                                ),
                                                html.Div(
                                                    [
                                                        html.Button("Anterior", id="mobile-prev-freq-btn", n_clicks=0),
                                                        html.Button("Proxima", id="mobile-next-freq-btn", n_clicks=0),
                                                    ],
                                                    style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "marginTop": "12px"},
                                                ),
                                                dcc.Dropdown(
                                                    id="mobile-frequency-picker",
                                                    options=[
                                                        {"label": f"{int(freq)} THz", "value": int(freq)}
                                                        for freq in FREQS
                                                    ],
                                                    value=int(FREQS[0]),
                                                    clearable=False,
                                                    searchable=False,
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Div(id="mobile-frequency-position", style={"marginTop": "10px", "color": "#475569"}),
                                                html.Div(
                                                    className="mobile-controls-grid",
                                                    children=[
                                                        html.Div(
                                                            [
                                                                html.Label("Amplitude da Onda 1"),
                                                                dcc.Input(
                                                                    id="mobile-amp1-input",
                                                                    type="number",
                                                                    step=0.1,
                                                                    min=AMP_MIN,
                                                                    max=AMP_MAX,
                                                                    value=0,
                                                                    style={"width": "100%", "marginTop": "6px", "padding": "10px"},
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label("Amplitude da Onda 2"),
                                                                dcc.Input(
                                                                    id="mobile-amp2-input",
                                                                    type="number",
                                                                    step=0.1,
                                                                    min=AMP_MIN,
                                                                    max=AMP_MAX,
                                                                    value=0,
                                                                    style={"width": "100%", "marginTop": "6px", "padding": "10px"},
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Button(
                                                    "Aplicar a frequencia",
                                                    id="mobile-apply-btn",
                                                    n_clicks=0,
                                                    style={"marginTop": "14px", "width": "100%"},
                                                ),
                                                html.Div(id="mobile-active-summary", style={"marginTop": "14px"}),
                                            ],
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Suavização dos envelopes de Hilbert"),
                                                dcc.Slider(
                                                    id="smoothing-slider",
                                                    min=1,
                                                    max=121,
                                                    step=2,
                                                    value=DEFAULT_SMOOTHING,
                                                    marks={value: str(value) for value in [1, 11, 21, 31, 51, 81, 121]},
                                                    persistence=True,
                                                    persistence_type="local",
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("delta f limite para a otimização"),
                                                dcc.Slider(
                                                    id="freq-delta-slider",
                                                    min=0,
                                                    max=MAX_FREQ_DELTA,
                                                    step=10,
                                                    value=DEFAULT_FREQ_DELTA,
                                                    marks={value: str(value) for value in [0, 40, 80, 120, 200, 300, 400]},
                                                    persistence=True,
                                                    persistence_type="local",
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Máximo de iterações da otimização"),
                                                dcc.Slider(
                                                    id="max-iter-slider",
                                                    min=1000,
                                                    max=10000,
                                                    step=500,
                                                    value=2000,
                                                    marks={value: str(value) for value in range(1000, 10001, 1500)},
                                                    persistence=True,
                                                    persistence_type="local",
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            id="control-note-box",
                                            style={
                                                "marginTop": "18px",
                                                "padding": "12px 14px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "10px",
                                                "background": "#f8fafc",
                                                "lineHeight": "1.7",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Button("OTIMIZAR", id="optimize-btn", n_clicks=0, style={"marginRight": "10px"}),
                                                html.Button("ZERAR", id="reset-btn", n_clicks=0),
                                            ],
                                            style={"marginTop": "18px", "display": "flex", "gap": "10px"},
                                        ),
                                        dcc.Loading(
                                            id="optimize-loading",
                                            type="circle",
                                            color="#2563eb",
                                            children=html.Div(
                                                id="optimization-indicator",
                                                style={"marginTop": "12px", "minHeight": "24px", "fontWeight": "bold", "color": "#2563eb"},
                                            ),
                                        ),
                                        html.Div(
                                            "Pronto para editar e otimizar as ondas.",
                                            id="status-message",
                                            style={
                                                "marginTop": "18px",
                                                "padding": "12px 14px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "10px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                    ],
                                    className="panel-card",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            className="desktop-only graph-stack",
                                            children=[
                                                dcc.Graph(id="intensity-graph", config=GRAPH_CONFIG),
                                                dcc.Graph(id="main-graph", config=GRAPH_CONFIG),
                                                html.Div(
                                                    [
                                                        html.H3("Resumo rápido"),
                                                        html.Div(id="summary-box"),
                                                    ],
                                                    style={
                                                        "border": "1px solid #d7deea",
                                                        "borderRadius": "12px",
                                                        "padding": "16px",
                                                        "background": "#ffffff",
                                                    },
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            className="mobile-only mobile-card",
                                            children=[
                                                html.H3("Visualização no celular"),
                                                html.P(
                                                    "Escolha uma etapa para visualizar um bloco por vez. Isso deixa a leitura mais confortável em telas pequenas.",
                                                    style={"lineHeight": "1.7"},
                                                ),
                                                dcc.RadioItems(
                                                    id="mobile-visual-view",
                                                    options=[
                                                        {"label": "Ondas e envelopes", "value": "main"},
                                                        {"label": "Controles", "value": "controls"},
                                                        {"label": "Lab RGB", "value": "rgb"},
                                                        {"label": "Resumo", "value": "summary"},
                                                    ],
                                                    value="main",
                                                    inline=False,
                                                    labelStyle={"display": "block", "marginBottom": "8px"},
                                                    style={"marginTop": "12px"},
                                                ),
                                                html.Div(id="mobile-visual-content", style={"marginTop": "14px"}),
                                            ],
                                        ),
                                    ],
                                    className="panel-card",
                                ),
                            ],
                            className="simulator-grid",
                        )
                    ],
                ),
                dcc.Tab(
                    label="Fourier Antes",
                    children=[
                        html.Div(
                            [
                                html.H3("Equações de Fourier antes da otimização"),
                                html.Pre(id="fourier-before", style={"whiteSpace": "pre-wrap", "lineHeight": "1.7"}),
                            ],
                            style={"padding": "20px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Fourier Depois",
                    children=[
                        html.Div(
                            [
                                html.H3("Equações de Fourier depois da otimização"),
                                html.Pre(id="fourier-after", style={"whiteSpace": "pre-wrap", "lineHeight": "1.7"}),
                            ],
                            style={"padding": "20px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Hilbert",
                    children=[
                        html.Div(
                            [
                                html.H3("Envelopes de Hilbert - teoria e aplicação"),
                                html.P("Para um sinal real x(t), o envelope complexo é z(t) = x(t) + j*H{x(t)}."),
                                html.P("O envelope de amplitude é A(t) = sqrt(x^2(t) + H^2{x(t)})."),
                                html.P("Nesta aplicação, os envelopes são calculados com scipy.signal.hilbert e a otimização busca reduzir a diferença máxima entre os dois envelopes."),
                                html.P(id="hilbert-smoothing-note"),
                                html.P(id="hilbert-delta-note"),
                                html.P("Critério principal: minimizar max|A1(t) - A2(t)|."),
                            ],
                            style={"padding": "20px", "lineHeight": "1.8"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Lab RGB",
                    children=[
                        html.Div(
                            [
                                html.H3("Laboratório RGB do Monitor"),
                                html.Div(
                                    [
                                        dcc.RadioItems(
                                            id="rgb-mode",
                                            options=[
                                                {"label": "RGB visual", "value": "visual"},
                                                {"label": "Paleta em RGB", "value": "palette"},
                                            ],
                                            value="visual",
                                            inline=True,
                                        ),
                                        html.Button("Atualizar", id="rgb-refresh-btn", n_clicks=0),
                                    ],
                                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "gap": "12px", "flexWrap": "wrap"},
                                ),
                                html.Div(
                                    "Clique em Atualizar para recalcular os cartões do laboratório RGB com o estado atual.",
                                    id="rgb-refresh-message",
                                    style={"marginTop": "10px", "fontWeight": "bold", "color": "#2563eb", "minHeight": "24px"},
                                ),
                                dcc.Graph(id="rgb-scale-graph", config=GRAPH_CONFIG),
                                html.Div(
                                    id="rgb-cards-container",
                                    style={
                                        "display": "grid",
                                        "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                                        "gap": "16px",
                                    },
                                ),
                            ],
                            style={"padding": "20px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Exercícios",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(id="exercise-title", children=initial_exercise["title"]),
                                        html.Div(
                                            id="exercise-difficulty",
                                            children=f"Nivel atual: {initial_exercise.get('difficulty', 'fundamental')}",
                                            style={
                                                "display": "inline-block",
                                                "marginBottom": "12px",
                                                "padding": "6px 10px",
                                                "borderRadius": "999px",
                                                "background": "#e0f2fe",
                                                "color": "#0f172a",
                                                "fontWeight": "bold",
                                                "fontSize": "0.92rem",
                                            },
                                        ),
                                        html.P(
                                            id="exercise-prompt",
                                            children=initial_exercise["prompt"],
                                            style={"lineHeight": "1.8"},
                                        ),
                                        html.Div(
                                            [
                                                html.H4("Critérios de conferência"),
                                                html.Div(id="exercise-rubric", children=build_exercise_rubric(initial_exercise)),
                                            ],
                                            style={
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "16px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Conclusão do estudante"),
                                                dcc.Textarea(
                                                    id="exercise-answer",
                                                    value="",
                                                    placeholder="Escreva aqui sua conclusão, observação ou justificativa física.",
                                                    style={
                                                        "width": "100%",
                                                        "minHeight": "180px",
                                                        "marginTop": "8px",
                                                        "padding": "12px",
                                                        "borderRadius": "12px",
                                                        "border": "1px solid #cbd5e1",
                                                        "lineHeight": "1.7",
                                                    },
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Button("Sortear novo exercício", id="new-exercise-btn", n_clicks=0),
                                                html.Button(
                                                    "Enviar resposta e dados",
                                                    id="submit-exercise-btn",
                                                    n_clicks=0,
                                                    style={"marginLeft": "10px"},
                                                ),
                                            ],
                                            style={"marginTop": "18px", "display": "flex", "gap": "10px", "flexWrap": "wrap"},
                                        ),
                                        html.Div(id="exercise-feedback", children=build_exercise_feedback()),
                                    ],
                                    className="panel-card",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.H3("Progresso salvo"),
                                                html.Div(id="exercise-progress-panel", children=build_exercise_progress_panel(initial_exercise_progress)),
                                            ],
                                            style={
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "16px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.H3("Dinâmica da aba"),
                                                html.P(
                                                    "Os exercícios já seguem uma lógica de sorteio, envio, correção automática e histórico local salvo no navegador. A parte visual foi adaptada à identidade desta simulação de ondas e cores.",
                                                    style={"lineHeight": "1.8"},
                                                ),
                                                html.P(
                                                    "Cada envio compara os dados atuais da simulação com os critérios do exercício e também verifica a conclusão escrita por palavras-chave conceituais.",
                                                    style={"lineHeight": "1.8"},
                                                ),
                                            ],
                                            style={
                                                "marginTop": "18px",
                                                "border": "1px solid #d7deea",
                                                "borderRadius": "12px",
                                                "padding": "16px",
                                                "background": "#ffffff",
                                            },
                                        ),
                                    ],
                                    className="panel-card",
                                ),
                            ],
                            className="exercise-grid",
                        )
                    ],
                ),
            ]
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("amp-table", "data"),
    Output("history-store", "data"),
    Output("status-message", "children"),
    Input("optimize-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    Input("mobile-apply-btn", "n_clicks"),
    State("amp-table", "data"),
    State("max-iter-slider", "value"),
    State("smoothing-slider", "value"),
    State("freq-delta-slider", "value"),
    State("mobile-frequency-picker", "value"),
    State("mobile-amp1-input", "value"),
    State("mobile-amp2-input", "value"),
    State("history-store", "data"),
    prevent_initial_call=True,
    running=[
        (Output("optimization-indicator", "children"), "Otimização em andamento...", ""),
        (Output("optimize-btn", "disabled"), True, False),
        (Output("reset-btn", "disabled"), True, False),
        (Output("mobile-apply-btn", "disabled"), True, False),
    ],
)
def handle_actions(
    optimize_clicks,
    reset_clicks,
    mobile_apply_clicks,
    table_data,
    max_iterations,
    smoothing_window,
    freq_delta,
    mobile_frequency,
    mobile_amp1,
    mobile_amp2,
    history_data,
):
    trigger = ctx.triggered_id
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    if history_data is None:
        history_data = initial_history
    amps1, amps2 = table_data_to_amps(table_data)

    if trigger == "mobile-apply-btn":
        current_frequency = int(mobile_frequency or FREQS[0])
        updated_table = [dict(row) for row in table_data]
        selected_index = int(np.where(FREQS == current_frequency)[0][0])
        updated_table[selected_index]["onda1"] = round(clamp_amp(mobile_amp1), 1)
        updated_table[selected_index]["onda2"] = round(clamp_amp(mobile_amp2), 1)
        status = f"Frequência {current_frequency} THz atualizada pelo editor móvel."
        return updated_table, history_data, status

    if trigger == "reset-btn":
        zero_table = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
        history = {
            "before1": ZERO_AMPS.tolist(),
            "before2": ZERO_AMPS.tolist(),
            "after1": ZERO_AMPS.tolist(),
            "after2": ZERO_AMPS.tolist(),
            "after_diff": None,
            "has_optimization": False,
        }
        return zero_table, history, "Tudo zerado. Ajuste as amplitudes novamente."

    optimized1, optimized2, final_diff, reason = optimize_amplitudes(
        amps1,
        amps2,
        int(max_iterations),
        smoothing_window=smoothing_window,
        freq_delta=freq_delta,
    )
    optimized_table = amps_to_table_data(optimized1, optimized2)
    displayed1, displayed2 = table_data_to_amps(optimized_table)
    displayed_diff = max_envelope_difference(displayed1, displayed2, smoothing_window)
    history = {
        "before1": amps1.tolist(),
        "before2": amps2.tolist(),
        "after1": displayed1.tolist(),
        "after2": displayed2.tolist(),
        "after_diff": float(displayed_diff),
        "has_optimization": True,
    }

    if reason == "blocked":
        status = "Nenhuma frequência ficou disponível para variar na janela escolhida."
    elif displayed_diff <= TARGET_DIFF:
        status = f"Concluído: diferença máxima entre envelopes = {displayed_diff:.4f}"
    elif reason == "limit":
        status = f"Parada pelo limite de {int(max_iterations)} iterações. Diferença = {displayed_diff:.4f}"
    else:
        status = f"Otimização parcial: diferença máxima = {displayed_diff:.4f}"

    return optimized_table, history, status


@app.callback(
    Output("rgb-refresh-message", "children"),
    Input("rgb-refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_lab_rgb(refresh_clicks):
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"Laboratório RGB atualizado às {timestamp}."


@app.callback(
    Output("intensity-graph", "figure"),
    Output("main-graph", "figure"),
    Output("summary-box", "children"),
    Output("control-note-box", "children"),
    Output("fourier-before", "children"),
    Output("fourier-after", "children"),
    Output("hilbert-smoothing-note", "children"),
    Output("hilbert-delta-note", "children"),
    Output("rgb-scale-graph", "figure"),
    Output("rgb-cards-container", "children"),
    Output("mobile-visual-content", "children"),
    Input("amp-table", "data"),
    Input("history-store", "data"),
    Input("rgb-mode", "value"),
    Input("rgb-refresh-btn", "n_clicks"),
    Input("smoothing-slider", "value"),
    Input("freq-delta-slider", "value"),
    Input("mobile-visual-view", "value"),
)
def refresh_outputs(table_data, history_data, rgb_mode, rgb_refresh_clicks, smoothing_window, freq_delta, mobile_visual_view):
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    if history_data is None:
        history_data = initial_history
    if rgb_mode is None:
        rgb_mode = "visual"
    if smoothing_window is None:
        smoothing_window = DEFAULT_SMOOTHING
    if freq_delta is None:
        freq_delta = DEFAULT_FREQ_DELTA
    if mobile_visual_view is None:
        mobile_visual_view = "main"

    current1, current2 = table_data_to_amps(table_data)

    before1 = np.array(history_data.get("before1", current1.tolist()), dtype=float)
    before2 = np.array(history_data.get("before2", current2.tolist()), dtype=float)
    after1 = np.array(history_data.get("after1", current1.tolist()), dtype=float)
    after2 = np.array(history_data.get("after2", current2.tolist()), dtype=float)
    has_optimization = has_valid_optimization_result(current1, current2, history_data)
    control_smoothing = sanitize_smoothing_window(smoothing_window, len(T))
    hilbert_smoothing_note, hilbert_delta_note = build_hilbert_notes(smoothing_window, freq_delta)

    fourier_before = generate_fourier_equation(before1, "Onda 1") + "\n\n" + generate_fourier_equation(before2, "Onda 2")
    fourier_after = generate_fourier_equation(after1, "Onda 1") + "\n\n" + generate_fourier_equation(after2, "Onda 2")
    control_note = html.Div(
        [
            html.Div(f"Suavização atual dos envelopes: {control_smoothing} ponto(s)."),
            html.Div(f"Janela atual da otimização em delta f: {format_frequency_delta(freq_delta)}."),
        ]
    )

    if not has_optimization:
        before1 = current1.copy()
        before2 = current2.copy()
        after1 = ZERO_AMPS.copy()
        after2 = ZERO_AMPS.copy()

    cards = [
        build_rgb_card(before1, "Onda 1", "Antes da otimização", rgb_mode),
        build_rgb_card(after1, "Onda 1", "Depois da otimização", rgb_mode) if has_optimization else build_pending_rgb_card("Onda 1", "Depois da otimização"),
        build_rgb_card(before2, "Onda 2", "Antes da otimização", rgb_mode),
        build_rgb_card(after2, "Onda 2", "Depois da otimização", rgb_mode) if has_optimization else build_pending_rgb_card("Onda 2", "Depois da otimização"),
    ]

    intensity_figure = build_intensity_figure(current1, current2)
    main_figure = build_main_figure(current1, current2, smoothing_window)
    summary_box = build_summary(current1, current2, smoothing_window, freq_delta)
    mobile_visual_content = build_mobile_visual_content(
        mobile_visual_view,
        intensity_figure,
        main_figure,
        build_color_scale_figure(rgb_mode),
        cards,
        summary_box,
        control_note,
    )
    scale_figure = build_color_scale_figure(rgb_mode)

    return (
        intensity_figure,
        main_figure,
        summary_box,
        control_note,
        fourier_before,
        fourier_after,
        hilbert_smoothing_note,
        hilbert_delta_note,
        scale_figure,
        cards,
        mobile_visual_content,
    )


@app.callback(
    Output("mobile-frequency-picker", "value"),
    Input("mobile-prev-freq-btn", "n_clicks"),
    Input("mobile-next-freq-btn", "n_clicks"),
    State("mobile-frequency-picker", "value"),
    prevent_initial_call=True,
)
def browse_mobile_frequency(prev_clicks, next_clicks, current_frequency):
    trigger = ctx.triggered_id
    current_frequency = int(current_frequency or FREQS[0])
    current_index = int(np.where(FREQS == current_frequency)[0][0])

    if trigger == "mobile-prev-freq-btn":
        return int(FREQS[(current_index - 1) % N_FREQS])
    return int(FREQS[(current_index + 1) % N_FREQS])


@app.callback(
    Output("mobile-amp1-input", "value"),
    Output("mobile-amp2-input", "value"),
    Output("mobile-frequency-position", "children"),
    Output("mobile-active-summary", "children"),
    Input("amp-table", "data"),
    Input("mobile-frequency-picker", "value"),
)
def sync_mobile_editor(table_data, mobile_frequency):
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)

    current_frequency = int(mobile_frequency or FREQS[0])
    row_lookup = {int(row["frequencia"]): row for row in table_data}
    current_row = row_lookup.get(current_frequency, {"onda1": 0, "onda2": 0})
    current_index = int(np.where(FREQS == current_frequency)[0][0])
    position_text = f"Editando {current_frequency} THz ({current_index + 1} de {N_FREQS})."

    return (
        current_row.get("onda1", 0),
        current_row.get("onda2", 0),
        position_text,
        build_mobile_active_summary(table_data),
    )


@app.callback(
    Output("exercise-store", "data"),
    Output("exercise-progress-store", "data"),
    Output("exercise-title", "children"),
    Output("exercise-difficulty", "children"),
    Output("exercise-prompt", "children"),
    Output("exercise-rubric", "children"),
    Output("exercise-feedback", "children"),
    Output("exercise-progress-panel", "children"),
    Output("exercise-answer", "value"),
    Input("new-exercise-btn", "n_clicks"),
    Input("submit-exercise-btn", "n_clicks"),
    State("exercise-store", "data"),
    State("exercise-progress-store", "data"),
    State("amp-table", "data"),
    State("exercise-answer", "value"),
    State("smoothing-slider", "value"),
    State("freq-delta-slider", "value"),
    State("history-store", "data"),
    prevent_initial_call=True,
)
def handle_exercises(
    new_exercise_clicks,
    submit_exercise_clicks,
    exercise_data,
    progress_data,
    table_data,
    answer_text,
    smoothing_window,
    freq_delta,
    history_data,
):
    trigger = ctx.triggered_id
    exercise_data = exercise_data or generate_random_exercise()
    progress_data = progress_data or initial_exercise_progress.copy()

    if trigger == "new-exercise-btn":
        new_exercise = generate_random_exercise(exercise_data.get("id"))
        feedback = build_exercise_feedback(
            {
                "title": "Novo exercício sorteado",
                "message": "A estrutura da atividade foi atualizada. Ajuste a simulação e envie quando terminar.",
                "details": ["O progresso já salvo foi mantido."],
                "accent": "#2563eb",
                "background": "#eff6ff",
            }
        )
        return (
            new_exercise,
            progress_data,
            new_exercise["title"],
            f"Nivel atual: {new_exercise.get('difficulty', 'fundamental')}",
            new_exercise["prompt"],
            build_exercise_rubric(new_exercise),
            feedback,
            build_exercise_progress_panel(progress_data),
            "",
        )

    metrics = collect_simulation_metrics(table_data, history_data, smoothing_window, freq_delta)
    passed, partial, total_score, feedback_data, metric_summary, result_label = evaluate_exercise(exercise_data, metrics, answer_text)
    timestamp = datetime.now().strftime("%H:%M:%S")
    next_streak = int(progress_data.get("streak", 0)) + 1 if passed else 0
    updated_progress = {
        "attempts": int(progress_data.get("attempts", 0)) + 1,
        "correct": int(progress_data.get("correct", 0)) + (1 if passed else 0),
        "partial": int(progress_data.get("partial", 0)) + (1 if partial else 0),
        "incorrect": int(progress_data.get("incorrect", 0)) + (1 if not passed and not partial else 0),
        "streak": next_streak,
        "best_streak": max(int(progress_data.get("best_streak", 0)), next_streak),
        "last_score": total_score,
        "best_score": max(int(progress_data.get("best_score", 0)), total_score),
        "history": list(progress_data.get("history", [])) + [
            {
                "timestamp": timestamp,
                "title": exercise_data["title"],
                "result": result_label,
                "score": total_score,
                "metric": metric_summary,
            }
        ],
    }
    updated_progress["history"] = updated_progress["history"][-12:]

    return (
        exercise_data,
        updated_progress,
        exercise_data["title"],
        f"Nivel atual: {exercise_data.get('difficulty', 'fundamental')}",
        exercise_data["prompt"],
        build_exercise_rubric(exercise_data),
        build_exercise_feedback(feedback_data),
        build_exercise_progress_panel(updated_progress),
        answer_text,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)