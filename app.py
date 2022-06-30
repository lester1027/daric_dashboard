from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

from vis_components import help_, visualization, calculation, data

app = Dash(__name__)
app.config.suppress_callback_exceptions=True

app.layout = html.Div([
    dcc.Store(id='stock-name'),
    dcc.Tabs(id='tabs-bar', value='tab-visualization', persistence=True, children=[
        dcc.Tab(label='Help', value='tab-help'),
        dcc.Tab(label='Visualization', value='tab-visualization'),
        dcc.Tab(label='Calculation', value='tab-calculation'),
        dcc.Tab(label='Data', value='tab-data'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-bar', 'value'),
)
def render_content(tab):
    if tab == 'tab-visualization':
        return visualization.tab_visualization_layout
    elif tab == 'tab-data':
        return data.tab_data_layout

@app.callback(
    Output('stock-name', 'data'),
    Input('stock-symbol-dropdown', 'value')
)
def save_stock_name(stock_name):
    return {'name': stock_name}

@app.callback(
    Output('stock-name-text', 'children'),
    Input('stock-name', 'data')
)
def print_stock_name(data):
    print(data)
    return str(data['name'])

if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    app.run_server(debug=True)