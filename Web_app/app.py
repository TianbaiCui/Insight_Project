import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output
from sklearn.externals import joblib
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objs as go
import dash_colorscales
import xgboost
import pickle
### Load the trained models:
model_adidas_7 = joblib.load('models/Adidas_7days_2019-05-28.sav')
model_adidas_14 = joblib.load('models/Adidas_14days_20_2019-05-28.sav')
model_clubmonaco_7 = joblib.load('models/ClubMonaco_7days_30_35_2019-05-37.sav')
model_clubmonaco_14 = joblib.load('models/ClubMonaco_14days_30_35_2019-05-37.sav')
model_KateSpade_7 = joblib.load('models/KateSpade_7days_30_2019-07-07.sav')
model_KateSpade_14 = joblib.load('models/KateSpade_14days_30_2019-07-07.sav')
#model_MichaelKors_7 = joblib.load('models/MichaelKors_7days_25_2019-06-17.sav')
#model_MichaelKors_14 = joblib.load('models/MichaelKors_14days_25_2019-06-17.sav')
model_NewBalance_7 = joblib.load('models/NewBalance_7days_20_2019-06-30.sav')
model_NewBalance_14 = joblib.load('models/NewBalance_14days_20_2019-06-30.sav')
model_Nike_7 = joblib.load('models/Nike_7days_2019-05-29.sav')
model_Nike_14 = joblib.load('models/Nike_14days_2019-05-29.sav')
model_Reebok_7 = joblib.load('models/Reebok_7days_30_35_2019-06-16.sav')
model_Reebok_14 = joblib.load('models/Reebok_14days_30_35_2019-06-16.sav')
model_ToryBurch_7 = joblib.load('models/ToryBurch_7days_20_2019-06-30.sav')
model_ToryBurch_14 = joblib.load('models/ToryBurch_14days_20_2019-06-30.sav')
model_UnderArmour_7 = joblib.load('models/UnderArmour_7days_20_2019-06-25.sav')
model_UnderArmour_14 = joblib.load('models/UnderArmour_14days_20_2019-06-25.sav')

All_models = [[model_adidas_7, model_adidas_14], [model_clubmonaco_7, model_clubmonaco_14],
              [model_KateSpade_7, model_KateSpade_14], [model_NewBalance_7, model_NewBalance_14],
              [model_Nike_7, model_Nike_14], [model_Reebok_7, model_Reebok_14],
              [model_ToryBurch_7, model_ToryBurch_14], [model_UnderArmour_7, model_UnderArmour_14]]

### Load the historical data:
adidas = pd.read_csv('datasets/Adidas2.csv')
clubmonaco = pd.read_csv('datasets/ClubMonaco2.csv')
katespade = pd.read_csv('datasets/KateSpade2.csv')
#michaelkors = pd.read_csv('datasets/MichaelKors.csv')
newbalance = pd.read_csv('datasets/NewBalance2.csv')
nike = pd.read_csv('datasets/Nike2.csv')
reebok = pd.read_csv('datasets/Reebok2.csv')
toryburch = pd.read_csv('datasets/ToryBurch2.csv')
underarmour = pd.read_csv('datasets/UnderArmour2.csv')

def str2datetime(df, cols):
    for col in cols:
        try:
            temp= pd.to_datetime(df[col],format='%Y-%m-%d')
        except:
            temp= pd.to_datetime(df[col],format='%m/%d/%Y')
        df.loc[:,col] = temp
    return df

feature_to_use = [col for col in adidas.columns if col not in ['Posted_year', 'Posted_day',
                                                               'Discount_amount', 'Posted_date', 'target',
                                                               'Discount_next_7days', 'Discount_next_14days',
                                                               'Discount_YesOrNo', 'Posted_month_year',
                                                               "days_awayNew Year's Day",
                                                               'days_awayMartin Luther King, Jr. Day',
                                                               "days_awayWashington's Birthday", 'days_awayMemorial Day',
                                                               'days_awayIndependence Day', 'days_awayLabor Day',
                                                               'days_awayColumbus Day', 'days_awayVeterans Day',
                                                               'days_awayThanksgiving', 'days_awayChristmas Day']]


All = []
for deal in [adidas, clubmonaco, katespade, newbalance, nike, reebok, toryburch, underarmour]:
    deal = str2datetime(deal, ["Posted_date"])
    All.append(deal)

d = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5,'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(children='SmartDeal',
            style={
            'textAlign': 'center',
            'font-size': '60px'
        }),
    html.Div([
        html.Label('Select the brand or store you are looking for:',style={"font-size": "20px"}),
        dcc.Dropdown(
            id = 'brand',
            options=[
                {'label': 'Adidas', 'value': 0},
                {'label': 'Club Monaco', 'value': 1},
                {'label': 'Kate Spade', 'value': 2},
                #{'label': 'Michael Kors', 'value': 3},
                {'label': 'New Balance', 'value': 3},
                {'label': 'Nike', 'value': 4},
                {'label': 'Reebok', 'value': 5},
                {'label': 'Tory Burch', 'value': 6},
                {'label': 'Under Armour', 'value': 7}
                ],
                value=0
                ),
                html.Hr(),

                html.Label('How many weeks do I want to wait:',style={"font-size": "20px"}),
                dcc.RadioItems(
                id = 'delay_days',
                options=[
                {'label': 'One week', 'value': 'one'},
                {'label': 'Two weeks', 'value': 'two'}
                ],
                value='one',
                labelStyle={'display': 'inline-block',"font-size": "18px"}
                ),


    ],className='five columns', style={'margin':{'l': 40, 'b': 40, 't': 20, 'r': 10}}),

    html.Div([
                    html.Table([
                    html.Tr([html.Td('Our suggestion:',style={"font-size": "20px"}), html.Td(id='suggest',style={"font-size": "20px",
                    'color': 'red'})]),
                    ]),
                    html.Label('Our prediction:' ,style={"font-size": "20px"}),
                    dcc.Graph(id='prob_graph'),
                    html.Hr()

    ],className='five columns', style={'margin':{'l': 40, 'b': 40, 't': 20, 'r': 10}}),


    html.Div([
    html.Hr(),
    html.Div('Historical data',className='one columns',style={
    'margin':0,
    'width': '100%',
    'textAlign': 'center',
    'font-size': '30px'
}),]),
    html.Div([
    dcc.Graph(id='years_graph')

    ],className='six columns', style={'width': '60%', 'margin':5}),

    html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='month-slider',
        min=1,
        max=12,
        value=1,
        marks={value: key for key, value in d.items()},
        step=None
        )
        ],className='four columns', style={'margin':5}),


], style={'width': '100%'})

app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'})

@app.callback(
    Output('suggest', 'children'),
    [Input('brand', 'value'),
    Input('delay_days', 'value')])

def pred(selected_brand, selected_day):
    dict = {'one': 0, 'two': 1}
    selected_model = All_models[selected_brand][dict[selected_day]]
    selected_brand_data = All[selected_brand][All[selected_brand]['Posted_date'] == datetime.now().strftime("%Y-%m-%d")][feature_to_use]
    data = selected_model.predict_proba(selected_brand_data)[0]
    if data[0] > 0.5:
        output = 'Buy Now! '
    else:
        output = 'Wait! '

    return output
@app.callback(
    Output('prob_graph', 'figure'),
    [Input('brand', 'value'),
    Input('delay_days', 'value')])

def pie_graph(selected_brand, selected_day):
    dict = {'one': 0, 'two': 1}
    selected_model = All_models[selected_brand][dict[selected_day]]
    selected_brand_data = All[selected_brand][All[selected_brand]['Posted_date'] == datetime.now().strftime("%Y-%m-%d")][feature_to_use]
    data = selected_model.predict_proba(selected_brand_data)[0]
    if data[0] > 0.5:
        sugg = 'Buy'
    else:
        sugg = 'Wait'
    All_labels = [[['No discount', '20% off', 'More than 25% off'], ['No discount', 'More than 20% off']],
                  [['No discount', '10% ~ 30% off', 'More than 35% off'],['No discount', '10% ~ 30% off', 'More than 35% off']],
                  [['No discount', 'More than 20% off'], ['No discount', 'More than 20% off']],
                  [['No discount', '10% ~ 15% off', 'More than 20% off'], ['No discount', '10% ~ 15% off', 'More than 20% off']],
                  [['No discount', '20% off', 'More than 25% off'], ['No discount', '20% off', 'More than 25% off']],
                  [['No discount', '15% ~ 30% off', 'More than 35% off'], ['No discount', '15% ~ 30% off', 'More than 35% off']],
                  [['No discount', 'More than 20% off'], ['No discount', 'More than 20% off']],
                  [['No discount', 'More than 20% off'], ['No discount', 'More than 20% off']]]
    trace=[
    {
      "values": data,
      "labels": All_labels[selected_brand][dict[selected_day]],
      "hoverinfo":"label+percent",
      "hole": .4,
      "type": "pie",
      "sort": False
    }]
    return {
    'data': trace,
    "layout": {
        'title':"Probablity of having a sale event:",
        'annotations':[
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": sugg,
                "x": 0.5,
                "y": 0.5
            }]
        }
    }

@app.callback(
    Output('years_graph', 'figure'),
    [Input('brand', 'value')])

def display_figure(selected_brand):
    filtered_df = All[selected_brand]
    plot_df = filtered_df[filtered_df['Discount_amount'] != 0]
    traces = []
    discount_types = np.sort(plot_df['Discount_amount'].unique())
    for i in range(len(discount_types)):
        traces.append(go.Bar(
            x= [x for x in range(1, 13)],
            y= [plot_df[(plot_df['Discount_amount'] == discount_types[i])&(plot_df['Posted_month'] == x)]['Posted_month'].count() for x in range(1,13)],
            name= 'Extra '+ str(int(100*discount_types[i])) + '% off')
        )

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis=dict(title='Month',dtick=1),
            yaxis={'title': 'Count'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            barmode='stack'
        )
    }


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('brand', 'value'),
    Input('month-slider', 'value')])


def update_figure(selected_brand, selected_month):
    filtered_df = All[selected_brand]
    plot_df = filtered_df[(filtered_df['Discount_amount'] != 0) & (filtered_df['Posted_month']==selected_month)]
    traces = []
    discount_types = np.sort(filtered_df[filtered_df['Discount_amount'] != 0]['Discount_amount'].unique())
    if len(plot_df['Posted_weekofmonth'].unique())!=0:
        if plot_df['Posted_weekofmonth'].max() > 4:
            x_range = range(1, plot_df['Posted_weekofmonth'].max()+1)
        else:
            x_range = range(1, 5)
    else:
        x_range = plot_df['Posted_weekofmonth'].unique()
    for i in range(len(discount_types)):
        traces.append(go.Bar(
            x = [x for x in x_range],
            y= [plot_df[(plot_df['Discount_amount'] == discount_types[i])&(plot_df['Posted_weekofmonth'] == x)]['Posted_weekofmonth'].count() for x in x_range],
            name= 'Extra '+ str(int(100*discount_types[i])) + '% off')
        )

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis=dict(title='Week of month',dtick=1),
            yaxis={'title': 'Count'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            barmode='stack'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
