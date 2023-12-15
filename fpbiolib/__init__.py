# base version number
__version__ = "0.1.7"  # add dir_file_ops


from .rounders import (
    base_roundup,
    base_rounddown,
    interval_range,
    round_down_nearest_order_mag,
    round_up_nearest_order_mag,
    ten_to_the_x,
)
from .formatting import (
    get_super,
    to_sup,
    dec_notation,
    sci_notation,
    process_str_list,
    str_px_width,
)
