import io
from base64 import b64encode


def create_fig_html_download(fig):
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_bytes = buffer.getvalue().encode()
    encoded = b64encode(html_bytes).decode()
    trace_html_download_href = "data:text/html;base64," + encoded
    return trace_html_download_href
