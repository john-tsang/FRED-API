# Purpose: Get a time-series through the FRED API and
#          print summary statistics and graphs of the time-series
# Date   : December 2021
# File   : get_obs_json.py
# Author : John Tsang

# Compulsory input: api_key and series_id
# Optional input  : realtime_start, realtime_end, limit, offset,
#                   sort_order, observation_start, observation_end,
#                   units, frequency, aggregation_method, 
#                   output_type, and vintage_dates
# Please refer to the read-me file for meaning of input parameters.
# Output: summary statistics (mean, variance, maximum and minimum)
# Return: a named-tuple Info:
#         df          : a dataframe containing the time-series
#         realtime_end: the realtime_end of the time-series
#         graph       : the matplotlib object of the time-series' graph 
#         db_data     : a dictionary containing information for database management
#             name                : series_id of the time-series
#             n                   : number of observations
#             n_missing           : number of missing observations
#             Start date          : Start date of the time-series
#             End date            : End date of the time-series
#             Realtime Start date : Realtime start date of the time-series
#             Realtime End date   : Realtime end date of the time-series

def get_obs_json(api_key, series_id, realtime_start = "",
            realtime_end = "", limit = "", offset = "",
            sort_order = "", observation_start = "", observation_end = "",
            units = "", frequency = "", aggregation_method = "", 
            output_type = "", vintage_dates="", save_graph = True):
    saved_args = locals()
    import urllib3
    http = urllib3.PoolManager()
    service_link  = "https://api.stlouisfed.org/fred/series/observations"
    
    saved_args['file_type'] = "json"
    r = http.request('GET', service_link, fields=saved_args)
    
    if (r.status != 200):
        print "Error:",r.status
        return r.status
    
    import json
    all_data = json.loads(r.data.decode('utf-8'))
    try:
        data = all_data["observations"]
    except DataRetrieveError:
        print "JSON does not have observations"
        return DataRetrieveError
    try:
        del all_data['observations']
    except KeyError:
        print "Header information is missing"
        return DataRetrieveError
            
    header = all_data
    
    import pandas as pd
    import numpy as np
    df = pd.DataFrame(data=data)
    df.rename(index=str, columns={"value": series_id}, inplace = True)
    # Count missing values
    len_df = len(df)
    n_missing = 0
    df['__m'] = 0
    import decimal
    for index in range(0,len_df):
        try:
            df[series_id][index] = float(decimal.Decimal(df[series_id][index]))
            df['__m'] = 1
        except KeyError:
            n_missing += 1
            df['__m'] = -1
    db_data = dict()
    db_data['series_id'] = series_id
    db_data['n']    = len_df
    db_data['n_missing'] = n_missing
    db_data['start_date'] = df.iloc[0]["date"]
    db_data['end_date'] = df.iloc[-1]["date"]
    db_data['r_start_date'] = df.iloc[0]["realtime_start"]
    db_data['r_end_date'] = df.iloc[0]["realtime_end"]
    
    print "Name of Series         :", series_id
    print "Number of Obs          :",len_df
    print "Number of Missing Obs  :",n_missing
    print "Start Date             :",df.iloc[0]["date"]
    print "End   Date             :",df.iloc[-1]["date"]
    print "Realtime End   Date    :",df.iloc[0]["realtime_end"]
    print 
    df = df.drop(df[df['__m'] == -1].index)
    df.drop('__m',axis = 1, inplace = True)
    print n_missing,"observations removed for analysis and graphing\n"
    
    print "Mean                   :",df[series_id].mean()
    print "Variance               :",df[series_id].var()
    print "Maximum                :",df[series_id].max()
    print "Minimum                :",df[series_id].min()
    
    import matplotlib.pyplot as plt
    graph_df = df[['date',series_id]]
    graph_df.set_index('date')
    graph = graph_df.plot(kind="line",title = series_id)
    
    xAxis = range(0,len(df))
    date = [str() for c in 'c' * len(df)]
    date[0] = df['date'].iloc[0]
    date[-1] = df['date'].iloc[-1]
    plt.xticks(xAxis,date)
    
    graph.set_xlabel("Date")
    graph.set_ylabel(series_id)
    plt.show()
    
    # Convert date to date object
    from datetime import datetime
    df["date"] = df["date"].apply(lambda x: datetime.strptime(x,'%Y-%m-%d'))
    
    import collections
    Info = collections.namedtuple("Info",["df",'realtime_end','graph','db_data'])
    graph_file_name = series_id + ".png"
    db_data['graph_file'] = graph_file_name
    if (save_graph):
        plt.savefig(graph_file_name, dpi = 300, bbox_inches='tight')
    df.set_index('date', inplace = True)
    rt = Info(df = df,realtime_end = header['realtime_end'],graph = graph, db_data=db_data)
    return rt