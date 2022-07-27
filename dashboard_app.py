from dash import Dash, dcc, html
from dash_extensions.enrich import Output, State, Input, html
import pandas as pd

from main_dash import app
from vis_components import help_tab, visualization_tab, metrics_tab, data_tab
from data_pipeline.data_source import FMPDataSource

app.layout = html.Div(
    children=[
        dcc.Interval(id='app-start', interval=1, max_intervals=1),
        dcc.Store(id='stock-symbol-all', storage_type='local'),
        dcc.Store(id='stock-symbol-selected', storage_type='local'),
        dcc.Store(id='stock-data', storage_type='local'),
        dcc.Tabs(id='tabs-bar', value='tab-visualization', persistence=True, children=[
            dcc.Tab(label='Help', value='tab-help'),
            dcc.Tab(label='Visualization', value='tab-visualization'),
            dcc.Tab(label='Metrics', value='tab-metrics'),
            dcc.Tab(label='Data', value='tab-data'),
        ]),
        html.Div(id='tabs-content')
    ]
)

# choose different tabs
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-bar', 'value'),
)
def render_content(tab):
    if tab == 'tab-visualization':
        return visualization_tab.tab_visualization_layout
    elif tab == 'tab-metrics':
        return metrics_tab.tab_metrics_layout
    elif tab == 'tab-data':
        return data_tab.tab_data_layout

if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    app.run_server(debug=True)