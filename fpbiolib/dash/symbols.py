from dash import html
import dash_bootstrap_components as dbc

from .chkbox_btn import control_chkbox_btn_callbacks


def symbols_callbacks(app, symbols):
    # Controller for activation button and collapse in Controls container
    control_chkbox_btn_callbacks(
        app, id=symbols
    )  # Same id as in Controls container layout


def symbols_collapse_layout(id):

    return dbc.Collapse(
        [
            html.P(
                "Use the symbols below to copy / paste into trace name and axes-label fields as needed",
                className="symbol_text_heading",
            ),
            html.Div(
                [
                    html.Div(
                        [html.P("Subscripts"), html.P("₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉"),],
                        className="symbol_text",
                    ),
                    html.Div(
                        [html.P("Superscripts"), html.P("⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹"),],
                        className="symbol_text",
                    ),
                    html.Div(
                        [
                            html.P("Lowercase greek"),
                            html.P("α β γ δ ε ζ η θ ι κ λ µ ν ξ ο π ⍴ ς σ τ υ φ χ ψ ω"),
                        ],
                        className="symbol_text",
                    ),
                    html.Div(
                        [
                            html.P("Uppercase greek"),
                            html.P("Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω"),
                        ],
                        className="symbol_text",
                    ),
                    html.Div(
                        [
                            html.P("Various"),
                            html.P("× ∙ ± ≤ ≥ ¼ ½ ¾ ° ∞ ™ © ® ← ↑ → ↓ ⛷ ⛺ ☕"),
                        ],
                        className="symbol_text",
                    ),
                ],
                className="row_container",
            ),
        ],
        id=f"{id}_collapse",  # Controlled by 'control_chkbox_btn_callbacks'
        is_open=False,
    )


# dbc.Toast([
#                 html.H6(
#                 'Some test text here...',
#                 className='float_slider_text'
#             )],
#         id=f'{symbols}_collapse', # Controlled by 'control_chkbox_btn_callbacks'
#             class_name='toast_container',
#             header="Peak Labeling Control Window",
#             icon="primary",
#             dismissable=False,
#             )
