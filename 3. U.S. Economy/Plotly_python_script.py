import pandas as pd
import psycopg2 as ps # needed to establish connection with AWS RDS
import boto3
import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly
import plotly.graph_objects as go
import plotly.subplots
from plotly.subplots import make_subplots
import plotly.express as px
from waitress import serve
# from jupyter_dash import JupyterDash # for local test env

# Connect to S3 to download secrets and keys
s3 = boto3.client('s3')
bucket_name = 'econdaily-prod-app-config'
file_name = 'env.source'
local_filename = '/app/myfilefroms3'

s3.download_file(bucket_name, file_name, local_filename)

with open(local_filename, 'r') as f:
    secrets = {line.strip().split('=')[0]: line.strip().split('=')[1] for line in f}
# print('secrets are:', secrets) # for debugging

def connect_to_db(dbname, user, password, host, port):
    try:
        conn = ps.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    except ps.OperationalError as e:
        raise e
    else:
        print('Connected!')
        return conn
    
dbname  = secrets['DB_NAME']
user    = secrets['DB_USER']
password= secrets['DB_PASSWORD']
host    = secrets['DB_HOST']
port    = secrets['DB_PORT']

conn = connect_to_db(dbname, user, password, host, port)
conn.set_isolation_level(ps.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

query = "SELECT * FROM econ_metrics;"
df_final = pd.read_sql_query(query, conn)

cur.close()
conn.close()
# print(df_final) #for debugging

# Visualization with charts for Confidence and FRED economic metrics
# Features include FRED economic metrics dropdown bar, time range button selector and date slider at bottom

fig = make_subplots(rows = 3,
    cols = 1,
    subplot_titles = ('Confidence', 'SP500', 'Other Economic Metrics'),
    shared_xaxes = True)

fig.append_trace(go.Scatter(
    x = df_final['date'],
    y = df_final['confidence'],
    name = 'confidence'), row = 1, col = 1)

fig.add_trace(go.Scatter(
    x = df_final['date'],
    y = df_final['sp500'],
    name = 'sp500'), row = 2, col = 1)

fig.append_trace(go.Scatter(
    x = df_final['date'],
    y = df_final['dow'],
    name = 'dow'), row = 3, col = 1)

fig.update_layout(height = 700,
                  width = 1100) # title_text = "Consumer Confidence and the U.S. Economy")

# Add date range selector buttons - starter code from Plotly documentation
fig.update_layout(
    xaxis = dict(
        rangeselector = dict(
            buttons = list([
                dict(count = 1,
                    label = "1m",
                    step = "month",
                    stepmode = "backward"),
                dict(count = 6,
                    label = "6m",
                    step = "month",
                    stepmode = "backward"),
                dict(count = 1,
                    label = "YTD",
                    step = "year",
                    stepmode = "todate"),
                dict(count = 1,
                    label = "1y",
                    step = "year",
                    stepmode = "backward"),
                dict(step = "all")
            ]), x = 1.05 #, y = 1.5
        ),
        type = "date"
    )
)

# fig.update_xaxes(matches = 'x')
fig.update_layout(xaxis_showticklabels = True,
    xaxis2_showticklabels = True,
    xaxis3_showticklabels = True)

updatemenu = []
buttons = []

# button with one option for each dataframe column excluding first df column
for col in df_final.columns[1: ]:
    buttons.append(dict(method = 'restyle',
        label = col,
        visible = True,
        args = [{
                'y': [df_final[col]],
                'x': [df_final['date']],
                'type': 'scatter'
            },
            [2]
        ],
    ))

# some adjustments to the updatemenus
updatemenu = []
your_menu = dict()
updatemenu.append(your_menu)

updatemenu[0]['buttons'] = buttons
updatemenu[0]['direction'] = 'down'
updatemenu[0]['showactive'] = True # Position dropdown: https: //stackoverflow.com/questions/50330544/positioning-a-dropdown-in-plotly
updatemenu[0]['x'] = 1.25
updatemenu[0]['y'] = 0.22

# add dropdown menus to the figure
fig.update_layout(showlegend = False, updatemenus = updatemenu)

# Add date range selector slider
fig.update_layout(xaxis3 = dict(rangeslider = dict(visible = True), type = 'date'))

fig.update_layout(
    height = 700,
    width = 1100,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

legend_data = pd.DataFrame({
    'Metric': ['Confidence', 'SP500', 'dow', 'nasdaq', 'inflation_5yr', 'oil',
               'interest', 't_note_10yr', 'cpi_item_cost', 'cpi_purchase_power'],
    'Description': ['Consumer Confidence', 'S&P 500', 'Dow Jones Industrial Average', 
                    'NASDAQ Composite', '5-Year Breakeven Inflation Rate', 
                    'Crude Oil Prices: West Texas Intermediate', 'Federal Funds Effective Rate',
                    'US Treasury Securities - 10 year', 'Consumer Price Index - avg price',
                    'Consumer Price Index - purchase power']
})

legend_table = html.Table([
    html.Thead(
        html.Tr([
            html.Th(col, style={'backgroundColor': 'f0e442', 'fontWeight': 'bold', 'fontSize': '14px'}) for col in legend_data.columns
        ])
    ),
    html.Tbody([
        html.Tr([
            html.Td(legend_data.iloc[i][col], style={'fontSize': '14px'}) for col in legend_data.columns
        ]) for i in range(len(legend_data))
    ])
])

app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

image_path = '/assets/Flowchart.jpg'

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
                html.H1("Consumer Confidence and the U.S. Economy"), 
                html.H3("By: Mushfiqur Rahman")
        ],
            width = 'auto',
            style = {
                'padding': '7px',
                'backgroundColor': '#f0e442',
                'align': 'center',
                'width': '100%',
                "justify": "center",
                'textAlign': 'center'
            })
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id = 'plot', figure = fig,
                style = {
                    "width": "80.8%",
                    #"height": "800px",
                    "display": "inline-block",
                    #"border": "2px #3c1c1c solid",
                    #"padding-top": "0px",
                    #"padding-left": "10px",
                    #"overflow": "hidden",
                    #"top": "200%",
                    #"left": "20%",
                    "align": "center",
                    "justify": "center",
                    'horizontal-align': 'center',
                    #"margin-top": "-400px"
                })
            ], width='auto')
            ]),

    dbc.Row([
        dbc.Col([
            legend_table
            ], width='80.8%', align='center', 
            style={
            # 'display': 'flex', 'justifyContent': 'center', 
            # 'align':'center', 'justify':'center', 'horizontal-align':'center'
            'marginLeft': '25%'
            },
            )
    ]),

    dbc.Row([
        dbc.Col([
                html.H3("")
                ],
                width = 'auto',
                style = {
                    'padding': '7px',
                    'align': 'center',
                    'width': '90%',
                    'justify': 'center',
                    'textAlign': 'center'
                    })
            ]),

    dbc.Row([
        dbc.Col([
            dcc.Markdown('''  
                         
                **Overview:**  
                The project's goal is to visually compare consumer confidence of the US economy
                with respect to important economic metrics from the Federal Reserve's FRED API using Dash and Plotly.
                Furthermore, the project showcases my knowledge of data, deployment and cloud tools.
                
                Initial questions to explore:  
                What is the current consumer confidence of the economy?  
                How has it varied over time?  
                Is there a correlation between consumer confidence and economic metrics 
                    like stock market performance?  
                
                Once enough data are collected, they will be fed into machine learning models
                to best fit a predictive model and determine if any economic indicators have correlations with 
                consumer confidence as the target variable.
                                
                **Methodology:**  
                1. Download economic data from U.S. Federal Reserve's FRED API and create a pandas dataframe.  
                2. Run Dockerized python script daily to update a AWS RDS PostgreSQL database using AWS ECS automation.  
                3. Visualize data with Plotly Dash and deploy as a website using AWS ECR, ECS, EC2 & Lambda.
                
                **Skills:**  
                Python; FRED API; Pandas; Docker; Github Actions; PostgreSQL;
                AWS - RDS, S3, ECR, ECS, EC2, Lambda, SNS, Cloudwatch, IAM, EventBridge;
                Plotly; Dash; pgAdmin; YAML; Cloudflare; Data Munging; Automation; Continuous Delivery  
                
                **Architecture Flowchart:**
                
                
                ''',
                style = {
                    'width': '85%',
                    'padding-left': '50px',
                    'fontSize':18
                })
        ], width = 'auto')
    ], justify = 'center'),

    # Adds image of architecture flowchart
    dbc.Row([
        dbc.Col([
            html.Img(src=image_path, style={'width': '85%',
                                            'align': 'center',
                                            'justify': 'center',
                                            'horizontal-align': 'center'})
        ], width='auto')
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Markdown('''  
                           
                                
                &emsp;  
                **Resources:**  
                Github portfolio  
                &emsp;https://github.com/lflrnr/Portfolio/  
                Federal Reserve Bank of St. Louis - FRED API docs  
                &emsp;https://fred.stlouisfed.org/docs/api/fred/  
                
                **Disclaimers:**  
                "This product uses the FRED® API but is not endorsed or certified by 
                the Federal Reserve Bank of St. Louis."  
                Furthermore, this exercise is for demonstration purposes only. 
                This dashboard, the underlying code, technologies involved and 
                their related organizations and the author does not assume any liability 
                for the use or misuse of any of the aforementioned 
                resources nor claim their veracity, timeliness, or conclusions stated or inferred.
                
                **Confidence metric citation:**  
                Organization for Economic Co-operation and Development, Consumer Opinion Surveys: Confidence Indicators: 
                Composite Indicators: OECD Indicator for the United States [ CSCICP03USM665S ], retrieved from FRED, 
                Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/CSCICP03USM665S, August 4, 2023.
                
                **Endnotes:**  
                Initially, this project was to conduct sentiment analyses of the US economy using 
                Twitter data.  Coding was completed but Twitter drastically reduced its free tier
                rate limits that were needed for the code to work. An example run is posted at my Github portfolio found above.
                Finally, the latest available date displayed my not be recent due to FRED having lags in data updates 
                         which usually resolve within a week or two.
                
                
                
                ''',
                style = {
                    'width': '85%',
                    'padding-left': '50px',
                    'fontSize':18
                })
        ], width = 'auto')
    ], justify = 'center'),
])

# if __name__ == '__main__':
#     app.run_server(debug = False, use_reloader = False) # turn off inline to get url " mode='inline' "

# if __name__ == '__main__':
#     app.run_server()
#     display()

# # Dash app default port is 8050, this option serves Flask app - a development server
# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0', port=8050)

# Dash app default port is 8050, this option serves Waitress app - a production server
if __name__ == '__main__':
    serve(app.server, host='0.0.0.0', port=8050)