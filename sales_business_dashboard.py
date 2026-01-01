# sales_business_dashboard.py

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# -------------------------------
# Step 1: Load Prepared Dataset
# -------------------------------
file_path = "sales_data.csv"

# Try reading with a different encoding
df= pd.read_csv(file_path, encoding='cp1252')  # or encoding='latin1'



# Ensure ORDERDATE is datetime
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
df['Month'] = df['ORDERDATE'].dt.month
df['Year'] = df['ORDERDATE'].dt.year

# -------------------------------
# Step 2: Initialize Dash App
# -------------------------------
app = dash.Dash(__name__)
app.title = "Sales Business Dashboard"

# -------------------------------
# Step 3: Layout
# -------------------------------
app.layout = html.Div([
    html.H1("Sales Business Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': y, 'value': y} for y in sorted(df['Year'].unique())],
            value=sorted(df['Year'].unique())[0]
        ),
        html.Label("Select Product Line:"),
        dcc.Dropdown(
            id='product-dropdown',
            options=[{'label': p, 'value': p} for p in df['PRODUCTLINE'].unique()],
            value=df['PRODUCTLINE'].unique()[0]
        ),
        html.Label("Select Country:"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in df['COUNTRY'].unique()],
            value=df['COUNTRY'].unique()[0]
        )
    ], style={'width':'30%', 'display':'inline-block', 'verticalAlign':'top'}),

    html.Div([
        html.H3(id='total-sales', style={'color':'green'}),
        html.H3(id='avg-order', style={'color':'blue'}),
        html.H3(id='max-sale', style={'color':'red'})
    ], style={'width':'65%', 'display':'inline-block', 'paddingLeft':'5%'}),

    dcc.Graph(id='monthly-sales-trend'),
    dcc.Graph(id='top-products'),
    dcc.Graph(id='sales-by-dealsize')
])

# -------------------------------
# Step 4: Callbacks for Interactivity
# -------------------------------
@app.callback(
    [Output('monthly-sales-trend', 'figure'),
     Output('top-products', 'figure'),
     Output('sales-by-dealsize', 'figure'),
     Output('total-sales', 'children'),
     Output('avg-order', 'children'),
     Output('max-sale', 'children')],
    [Input('year-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_dashboard(selected_year, selected_product, selected_country):
    # Filter data
    filtered = df[(df['Year'] == selected_year) &
                  (df['PRODUCTLINE'] == selected_product) &
                  (df['COUNTRY'] == selected_country)]

    # Monthly Sales Trend
    monthly_sales = filtered.groupby('Month')['SALES'].sum().reset_index()
    fig1 = px.line(monthly_sales, x='Month', y='SALES', markers=True,
                   title=f"Monthly Sales Trend ({selected_product}, {selected_year})")

    # Top Products by Sales
    top_products = filtered.groupby('PRODUCTCODE')['SALES'].sum().sort_values(ascending=False).reset_index()
    fig2 = px.bar(top_products.head(10), x='PRODUCTCODE', y='SALES',
                  title="Top 10 Products by Sales", text='SALES')

    # Sales by Deal Size
    deal_sales = filtered.groupby('DEALSIZE')['SALES'].sum().reset_index()
    fig3 = px.bar(deal_sales, x='DEALSIZE', y='SALES',
                  title="Sales by Deal Size", text='SALES')

    # Key Metrics
    total_sales = f"Total Sales: ${filtered['SALES'].sum():,.2f}"
    avg_order = f"Average Order Value: ${filtered['SALES'].mean():,.2f}"
    max_sale = f"Max Single Sale: ${filtered['SALES'].max():,.2f}"

    return fig1, fig2, fig3, total_sales, avg_order, max_sale

# -------------------------------
# Step 5: Run App
# -------------------------------
if __name__ == '__main__':
     app.run(debug=True)
