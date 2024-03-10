import math
import re


# function to convert to superscript
def get_super(x):
    """
    Very few fonts seem to render the unicode superscripts correctly.
    Menlo seems to do okay on VS Code.
    """
    normal = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    )
    super_s = (
        "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    )
    res = x.maketrans("".join(normal), "".join(super_s))
    return x.translate(res)


def dec_notation(num, sci_note_upper):
    num_order_power = math.floor(math.log10(abs(num)))
    num_order = 10**num_order_power
    dec = str(int(math.log10(sci_note_upper) - math.log10(num_order)))
    # print("dec: ", dec)
    return f"{num:.{3}f}"


def sci_notation(num, sig_figs, e_notation=True, cap_e=False):
    """Return a numeric value as a string
    formatted as either e notation or scientific
    notation, e.g.
     - e notation:  3.56e+06
     - E notation: 3.56E+06
     - Scientific notation: 3.56 × 10⁺⁰⁶
    """
    sci_num = f"{num:.{sig_figs}e}"
    if cap_e and e_notation:
        sci_num = f"{num:.{sig_figs}E}"
    if e_notation:
        return sci_num
    pattern = re.compile(r"(e)([+-]\d+)")
    matches = pattern.findall(sci_num)
    exp_match = matches[0]
    pattern = re.compile(r"([+-])(\d)(\d)")
    matches = pattern.findall(exp_match[-1])
    exp2_match = matches[0]
    if exp2_match[1] == "0":
        exp2_match = [exp2_match[i] for i in [0, 2]]
    if exp2_match[0] == "+":
        exp2_match = exp2_match[1:]
    sci_str = "".join(exp2_match)
    sci_num = sci_num.replace("e", " \u00d7 10")
    return sci_num.replace(exp_match[-1], get_super(sci_str))


""" Various characters
Subscripts: ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
Superscripts: ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹
Lower-case Greek: α β γ δ ε ζ η θ ι κ λ µ ν ξ ο π ⍴ ς σ τ υ φ χ ψ ω
Upper-case Greek: Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
Symbols: × ∙ ± ≤ ≥ ¼ ½ ¾ ° ∞ ™ © ® ← ↑ → ↓ ⛷ ⛺ ☕
"""

greek_alphabet = "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"
latin_alphabet = "AaBbGgDdEeZzHhJjIiKkLlMmNnXxOoPpRrSssTtUuFfQqYyWw"
greek2latin = str.maketrans(greek_alphabet, latin_alphabet)


def to_sup(s):
    sups = {
        "0": "\u2070",
        "1": "\xb9",
        "2": "\xb2",
        "3": "\xb3",
        "4": "\u2074",
        "5": "\u2075",
        "6": "\u2076",
        "7": "\u2077",
        "8": "\u2078",
        "9": "\u2079",
        "a": "\u1d43",
        "b": "\u1d47",
        "c": "\u1d9c",
        "d": "\u1d48",
        "e": "\u1d49",
        "f": "\u1da0",
        "g": "\u1d4d",
        "h": "\u02b0",
        "i": "\u2071",
        "j": "\u02b2",
        "-": "\u207b",
    }

    return "".join(
        sups.get(char, char) for char in s
    )  # lose the list comprehension


def process_str_list(str_list: list) -> list:
    """Some list characters are stored as strings
    for user readability.  Process it
    to create a normal python list with floats.
    """
    if not str_list:
        return None

    bad_chars = "]['"
    for c in bad_chars:
        str_list = str_list.replace(c, "")
    str_list = str_list.split(",")
    return [float(x) for x in str_list]


def none_to_empty_str(d):
    return {k: v or "" for k, v in d.items()}


def slider_num_formatter(
    num, sci_sig_figs=3, sci_note_upper=10000, sci_note_lower=0.01
):
    if num == 0:
        return "0"
    elif num >= sci_note_upper or num < sci_note_lower:
        return sci_notation(num, sci_sig_figs)
    else:
        return dec_notation(num, sci_note_upper).rstrip("0").rstrip(".")


font_widths = {
    "open_sans_12pt_px": {
        ".": 4,
        "-": 5.3,
        "e": 7.1,
        "E": 9.8,
        "0": 8,
        "1": 8,
        "2": 8,
        "3": 8,
        "4": 8,
        "5": 8,
        "6": 8,
        "7": 8,
        "8": 8,
        "9": 8,
    },
}


def str_px_width(text: str, font="open_sans_12pt_px"):
    """Determine total px width of text
    - requires a font_widths dictionary of
    characters and px widths.
    """
    char_widths = font_widths.get(font)
    px_width = sum(char_widths.get(c) for c in str(text))
    if px_width <= 11:
        px_width = 11
    return f"{str(px_width)}px"
