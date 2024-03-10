# add config variable for graph options
# see: https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
config = {
    # 'uirevision': cols,
    "edits": {"axisTitleText": True, "titleText": False, "legendText": True},
    "scrollZoom": True,
    "displayModeBar": True,
    "editable": True,
    "displaylogo": False,
    "responsive": False,
    "toImageButtonOptions": {
        "scale": 2,
        "width": 1000,
        "height": 500,
        "format": "png",
    },  # one of png, svg, jpeg, webp},
    "modeBarButtonsToRemove": [
        "toggleSpikelines",
    ],
    #             'modeBarButtonsToAdd':['drawline',
    #                                         'drawopenpath',
    #                                         'drawclosedpath',
    #                                         'drawcircle',
    #                                         'drawrect',
    #                                         'eraseshape'
    #                                        ],
}
