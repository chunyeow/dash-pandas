import dash
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
import requests
import json
requests.packages.urllib3.disable_warnings()
import conf

column_titles = conf.titles
PAGE_SIZE = conf.page_size

def get_data(limit, sort):
    try:
       headers = {'Accept':'application/json', 'Authorization': 'Bearer ' + conf.gw_token }
       url = conf.url + "/" + conf.projnum + "/data" + \
             "?limit=" + limit + "&sort=" + sort
       get_resp = requests.get(url, headers=headers, verify=False)
       if get_resp.status_code == 200:
          return get_resp
       else:
          return
    except requests.exceptions.ConnectionError:
       return

res = get_data("12000", "qty desc")
if res != None:
   docs = res.json()['docs']
   df = pd.read_json(json.dumps(docs), orient='columns')
   df = df.reindex(columns=column_titles)
else:
   exit

df['Channel'] = range(1, len(df) + 1)

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table-paging-and-sorting',
    columns=[
        {'name': i, 'id': i, 'deletable': True} for i in df.columns
    ],
    pagination_settings={
        'current_page': 0,
        'page_size': PAGE_SIZE
    },
    pagination_mode='be',

    sorting='be',
    sorting_type='single',
    sort_by=[]
)


@app.callback(
    Output('table-paging-and-sorting', 'data'),
    [Input('table-paging-and-sorting', 'pagination_settings'),
     Input('table-paging-and-sorting', 'sort_by')])
def update_table(pagination_settings, sort_by):
    if len(sort_by):
        dff = df.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    else:
        # No sort is applied
        dff = df

    return dff.iloc[
        pagination_settings['current_page']*pagination_settings['page_size']:
        (pagination_settings['current_page'] + 1)*pagination_settings['page_size']
    ].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
