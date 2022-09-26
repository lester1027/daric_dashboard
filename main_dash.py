from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, html

app = DashProxy(__name__, transforms=[MultiplexerTransform()])
app.config.suppress_callback_exceptions = True