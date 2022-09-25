# Daric Dashboard

Developing an Interactive Dashboard for Value Investment with Python, Dash and Pandas
https://medium.com/@lesterso1027/developing-an-interactive-dashboard-for-value-investment-with-python-dash-and-pandas-version-3-d39582a710d7

<br>

## How to Use
1. Select the stocks you are interested in from the drop-down list.
2. Click the ‘Refresh Data’ button.

3. Wait for the data update.

4. Click the ‘Data’ tab and edit the ‘long_term_growth_rate’. Press ‘Enter’ to confirm the change. \
(The API used by Daric does not support a valid growth rate yet. The growth estimates in Yahoo Finance may be a proper number to input. E.g.: https://finance.yahoo.com/quote/AAPL/analysis?p=AAPL)

5. Go back to the ‘Visualization’ tab to look at the evaluation of the metric. \
The metrics in blue pass the screening and the ones in red fail.\
The line charts show the trends of the metrics.

6. The data tables in the ‘Metrics’ and the ‘Data’ tabs are editable for matching customization needs. \
(Editing the entries in the ‘Data’ tab will modify the stock raw data and the metrics will be recalculated. \
Editing the entries in the ‘Metrics’ tab will only modify the stock metrics while leaving the raw data unchanged.)

<br>

## How to Build
1. Clone this repository to the local machine

2. Create a new conda environment with ```conda create -n daric python=3.9```

3. Activate the conda environment with ```conda activate daric```

4. In the directory of the cloned repository, install the dependencies with ```pip install -r requirements.txt```

5. Run ```python dashboard_app.py```

