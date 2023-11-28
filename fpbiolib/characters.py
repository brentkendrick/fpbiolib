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
    sci_num = sci_num.replace("e", " \u00D7 10")
    return sci_num.replace(exp_match[-1], get_super(sci_str))


""" Various characters
Subscripts: ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
Superscripts: ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹
Lower-case Greek: α β γ δ ε ζ η θ ι κ λ µ ν ξ ο π ⍴ ς σ τ υ φ χ ψ ω
Upper-case Greek: Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
Symbols: × ∙ ± ≤ ≥ ¼ ½ ¾ ° ∞ ™ © ® ← ↑ → ↓ ⛷ ⛺ ☕
"""


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
        "f": "\u1dA0",
        "g": "\u1d4D",
        "h": "\u02B0",
        "i": "\u2071",
        "j": "\u02B2",
        "-": "\u207B",
    }

    return "".join(
        sups.get(char, char) for char in s
    )  # lose the list comprehension
