# base version number
__version__ = "0.5.0"  # update ftir file parsing


from .formatting import (
    dec_notation,
    get_super,
    process_str_list,
    sci_notation,
    str_px_width,
    to_sup,
)
from .rounders import (
    base_rounddown,
    base_roundup,
    interval_range,
    round_down_nearest_order_mag,
    round_up_nearest_order_mag,
    ten_to_the_x,
)
