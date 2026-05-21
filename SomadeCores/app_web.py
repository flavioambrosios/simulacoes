import os
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
TIME_FS = T * 1e15
AMP_MIN = -1.0
AMP_MAX = 1.0
TARGET_DIFF = 0.25
ZERO_AMPS = np.zeros(N_FREQS)
BASIS = np.sin(2 * np.pi * FREQS[:, None] * 1e12 * T[None, :])


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


def generate_wave(amps):
    return amps @ BASIS


def compute_envelope(wave):
    return np.abs(hilbert(wave))


def max_envelope_difference(amps1, amps2):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    return float(np.max(np.abs(compute_envelope(wave1) - compute_envelope(wave2))))


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


def build_main_figure(amps1, amps2):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1)
    envelope2 = compute_envelope(wave2)
    diff = envelope1 - envelope2

    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Onda 1",
            "Onda 2",
            "Envelopes de Hilbert",
            "Diferença entre os envelopes",
        ),
        vertical_spacing=0.16,
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

    for row, col in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        figure.update_xaxes(title_text="Tempo (fs)", range=[0, 200], dtick=25, row=row, col=col)
        figure.update_yaxes(title_text="Amplitude", row=row, col=col)

    figure.update_layout(
        height=760,
        template="plotly_white",
        margin=dict(l=30, r=30, t=70, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    return figure


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
    return figure


def build_summary(amps1, amps2):
    wave1 = generate_wave(amps1)
    wave2 = generate_wave(amps2)
    envelope1 = compute_envelope(wave1)
    envelope2 = compute_envelope(wave2)
    max_diff = float(np.max(np.abs(envelope1 - envelope2)))
    return html.Ul(
        [
            html.Li(f"Pico da Onda 1: {np.max(np.abs(wave1)):.3f}"),
            html.Li(f"Pico da Onda 2: {np.max(np.abs(wave2)):.3f}"),
            html.Li(f"Diferença máxima entre envelopes: {max_diff:.3f}"),
            html.Li(f"Componentes ativas na Onda 1: {int(np.sum(np.abs(amps1) > 1e-12))}"),
            html.Li(f"Componentes ativas na Onda 2: {int(np.sum(np.abs(amps2) > 1e-12))}"),
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
    return figure


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


def optimize_amplitudes(initial_amps1, initial_amps2, max_iterations):
    class OptimizationStopped(Exception):
        def __init__(self, amps_flat, diff, reason):
            self.amps_flat = amps_flat.copy()
            self.diff = diff
            self.reason = reason

    def cost_function(amps_flat):
        amps1 = amps_flat[:N_FREQS]
        amps2 = amps_flat[N_FREQS:]
        return max_envelope_difference(amps1, amps2)

    iteration_counter = {"count": 0}

    def iteration_callback(xk):
        iteration_counter["count"] += 1
        current_diff = max_envelope_difference(xk[:N_FREQS], xk[N_FREQS:])
        if current_diff <= TARGET_DIFF:
            raise OptimizationStopped(xk, current_diff, "target")
        if iteration_counter["count"] >= max_iterations:
            raise OptimizationStopped(xk, current_diff, "limit")

    x0 = np.concatenate([initial_amps1, initial_amps2])
    bounds = [(AMP_MIN, AMP_MAX) for _ in range(2 * N_FREQS)]

    try:
        result = minimize(
            cost_function,
            x0,
            method="L-BFGS-B",
            bounds=bounds,
            callback=iteration_callback,
            options={"maxiter": int(max_iterations)},
        )
        final_x = result.x
        final_diff = max_envelope_difference(final_x[:N_FREQS], final_x[N_FREQS:])
        if final_diff <= TARGET_DIFF:
            reason = "target"
        elif getattr(result, "nit", 0) >= max_iterations:
            reason = "limit"
        else:
            reason = "partial"
    except OptimizationStopped as stopped:
        final_x = stopped.amps_flat
        final_diff = stopped.diff
        reason = stopped.reason

    return final_x[:N_FREQS], final_x[N_FREQS:], final_diff, reason


app = Dash(__name__)
server = app.server

initial_history = {
    "before1": ZERO_AMPS.tolist(),
    "before2": ZERO_AMPS.tolist(),
    "after1": ZERO_AMPS.tolist(),
    "after2": ZERO_AMPS.tolist(),
}

app.layout = html.Div(
    [
        dcc.Store(id="history-store", data=initial_history),
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
                                        dash_table.DataTable(
                                            id="amp-table",
                                            columns=[
                                                {"name": "Frequência (THz)", "id": "frequencia", "editable": False},
                                                {"name": "Onda 1", "id": "onda1", "editable": True},
                                                {"name": "Onda 2", "id": "onda2", "editable": True},
                                            ],
                                            data=amps_to_table_data(ZERO_AMPS, ZERO_AMPS),
                                            editable=True,
                                            style_table={"height": "520px", "overflowY": "auto", "border": "1px solid #d7deea"},
                                            style_header={"fontWeight": "bold", "backgroundColor": "#eef4ff"},
                                            style_cell={"textAlign": "center", "padding": "5px", "minWidth": "68px", "width": "68px", "maxWidth": "68px"},
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Máximo de iterações da otimização"),
                                                dcc.Slider(
                                                    id="max-iter-slider",
                                                    min=1000,
                                                    max=10000,
                                                    step=500,
                                                    value=5000,
                                                    marks={value: str(value) for value in range(1000, 10001, 1500)},
                                                ),
                                            ],
                                            style={"marginTop": "18px"},
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
                                    style={"minWidth": "320px"},
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id="intensity-graph"),
                                        dcc.Graph(id="main-graph"),
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
                            ],
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "minmax(320px, 380px) 1fr",
                                "gap": "20px",
                                "padding": "20px 0",
                            },
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
                                dcc.Graph(id="rgb-scale-graph"),
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
            ]
        ),
    ],
    style={
        "maxWidth": "1400px",
        "margin": "0 auto",
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
        "background": "#f7f8fb",
        "color": "#1f2937",
    },
)


@app.callback(
    Output("amp-table", "data"),
    Output("history-store", "data"),
    Output("status-message", "children"),
    Input("optimize-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("amp-table", "data"),
    State("max-iter-slider", "value"),
    prevent_initial_call=True,
    running=[
        (Output("optimization-indicator", "children"), "Otimização em andamento...", ""),
        (Output("optimize-btn", "disabled"), True, False),
        (Output("reset-btn", "disabled"), True, False),
    ],
)
def handle_actions(optimize_clicks, reset_clicks, table_data, max_iterations):
    trigger = ctx.triggered_id
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    amps1, amps2 = table_data_to_amps(table_data)

    if trigger == "reset-btn":
        zero_table = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
        history = {
            "before1": ZERO_AMPS.tolist(),
            "before2": ZERO_AMPS.tolist(),
            "after1": ZERO_AMPS.tolist(),
            "after2": ZERO_AMPS.tolist(),
        }
        return zero_table, history, "Tudo zerado. Ajuste as amplitudes novamente."

    optimized1, optimized2, final_diff, reason = optimize_amplitudes(amps1, amps2, int(max_iterations))
    history = {
        "before1": amps1.tolist(),
        "before2": amps2.tolist(),
        "after1": optimized1.tolist(),
        "after2": optimized2.tolist(),
    }

    if reason == "target" or final_diff <= TARGET_DIFF:
        status = f"Concluído: diferença máxima entre envelopes = {final_diff:.4f}"
    elif reason == "limit":
        status = f"Parada pelo limite de {int(max_iterations)} iterações. Diferença = {final_diff:.4f}"
    else:
        status = f"Otimização parcial: diferença máxima = {final_diff:.4f}"

    return amps_to_table_data(optimized1, optimized2), history, status


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
    Output("fourier-before", "children"),
    Output("fourier-after", "children"),
    Output("rgb-scale-graph", "figure"),
    Output("rgb-cards-container", "children"),
    Input("amp-table", "data"),
    Input("history-store", "data"),
    Input("rgb-mode", "value"),
    Input("rgb-refresh-btn", "n_clicks"),
)
def refresh_outputs(table_data, history_data, rgb_mode, rgb_refresh_clicks):
    if table_data is None:
        table_data = amps_to_table_data(ZERO_AMPS, ZERO_AMPS)
    if history_data is None:
        history_data = initial_history
    if rgb_mode is None:
        rgb_mode = "visual"

    current1, current2 = table_data_to_amps(table_data)

    before1 = np.array(history_data.get("before1", current1.tolist()), dtype=float)
    before2 = np.array(history_data.get("before2", current2.tolist()), dtype=float)
    after1 = np.array(history_data.get("after1", current1.tolist()), dtype=float)
    after2 = np.array(history_data.get("after2", current2.tolist()), dtype=float)

    fourier_before = generate_fourier_equation(before1, "Onda 1") + "\n\n" + generate_fourier_equation(before2, "Onda 2")
    fourier_after = generate_fourier_equation(after1, "Onda 1") + "\n\n" + generate_fourier_equation(after2, "Onda 2")

    cards = [
        build_rgb_card(before1, "Onda 1", "Antes da otimização", rgb_mode),
        build_rgb_card(after1, "Onda 1", "Depois da otimização", rgb_mode),
        build_rgb_card(before2, "Onda 2", "Antes da otimização", rgb_mode),
        build_rgb_card(after2, "Onda 2", "Depois da otimização", rgb_mode),
    ]

    return (
        build_intensity_figure(current1, current2),
        build_main_figure(current1, current2),
        build_summary(current1, current2),
        fourier_before,
        fourier_after,
        build_color_scale_figure(rgb_mode),
        cards,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)