from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, html

app = DashProxy(__name__, transforms=[MultiplexerTransform()])
app.config.suppress_callback_exceptions = True
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%favicon%}
        {%css%}
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6437726536363317"
            crossorigin="anonymous">
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''