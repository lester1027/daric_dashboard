# ticker_dashboard

Developing an Interactive Dashboard for Value Investment with Python, Dash and Pandas
https://medium.com/@lesterso1027/developing-an-interactive-dashboard-for-value-investment-with-python-dash-and-pandas-version-2-2c2616542b5c

## How to use
I. Enter the account as ‘Lester’ and the password as ‘wildcard’.

II. Choose the tickers in the dropdown list (can filter the results with typing).

III. Select the date range and update the price (this step is not necessary for doing fundamental analysis).

IV. Enter the safety margin in terms of percentage (if a safety margin is not needed, leave the value as default).

V. Click the ‘Fundamental analysis’ button to show the financial figures and the analysis results of the selected stocks. The column ‘Comparison’ shows whether the stock is over-valued or under-valued.

VI. If there are financial figures shown as ‘9999999999’, this means the required figure is not accessible from the data source and manual input is required.

VII. The table is fully editable. In case there is an error like the above-mentioned one or the user wants to make some adjustment of the financial figures, columns showing financial figures 1 to 14 should be edited.

VIII. If the stock to be analysed cannot be found in the drop-down list, users can click the ‘Add an empty row’ button and input all the figures manually.


## Requirements

alabaster==0.7.12

astroid==2.3.2

attrs==19.3.0

autopep8==1.4.4

Babel==2.7.0

backcall==0.1.0

bleach==3.1.0

certifi==2019.9.11

cffi==1.13.2

chardet==3.0.4

click==6.7

cloudpickle==1.2.2

colorama==0.4.1

cryptography==2.8

Cython==0.28.2

dash==1.7.0

dash-auth==1.3.2

dash-core-components==1.6.0

dash-html-components==1.0.2

dash-renderer==1.2.2

dash-table==4.5.1

decorator==4.3.0

defusedxml==0.6.0

docutils==0.15.2

Flask==1.1.1

Flask-Compress==1.4.0

Flask-SeaSurf==0.2.2

future==0.18.2

gunicorn==20.0.4

idna==2.8

itsdangerous==1.1.0

Jinja2==2.11.1

lazy-object-proxy==1.4.3

lxml==4.5.0

MarkupSafe==1.1.1

numpy==1.18.1

pandas==1.0.0

plotly==4.5.0

pycodestyle==2.5.0

pycparser==2.19

python-dateutil==2.8.1

pytz==2019.3

requests==2.22.0

retrying==1.3.3

six==1.12.0

typed-ast==1.4.1

ua-parser==0.8.0

urllib3==1.25.8

webencodings==0.5.1

Werkzeug==0.16.1

wrapt==1.11.2

