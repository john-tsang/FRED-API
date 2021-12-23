# Purpose: Create a table of summarizing all time-series_id
#          where series_id is the primary key

def sql_set_up(conn):
    import sqlite3
    # Create Table Series_info
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS Series_info''')
    fields_lst = [("series_id","String"),("n","Integer"),("n_missing","Integer"),
                  ("start_date","String"),("end_date","String"),
                  ("r_start_date","String"),("r_end_date","String"),
                  ("graph_file","String")]
    query = "CREATE TABLE Series_info ("
    counter = 0
    for field in fields_lst:
        counter += 1
        query += field[0]+" "+field[1]
        if (counter != len(fields_lst)):
            query += ","
        else:
            query += ", Primary Key (series_id))"
    cur.execute(query)
    return

# Purpose: The main program to retrieve time-series 
#          from the Federal Reserve Economic Data (FRED)

def fetch_FRED_data(db_file_name, series_id, api_key):
    import pandas as pd
    import numpy as np
    from get_obs_json import get_obs_json
    # Check if database set up
    import sqlite3
    conn = sqlite3.connect(db_file_name)
    cur = conn.cursor()
    # Set up if not exist
    try:
        cur.execute("SELECT * FROM Series_info")
    except:
        sql_set_up(conn)
        print "Table Series_info set-up success!"
        
    # Check if series_id exist
    series_exist = True
    try:
        query = "SELECT * FROM "+series_id+" ORDER BY date DESC LIMIT 1"
        print query
        rt = cur.execute(query)
    except:
        series_exist = False
    if (series_exist):
        # Check if series is up-to-date
        result = rt.fetchall()
        last_date = result[0][0][:10]
        print "Last date in data set:",last_date
        rt = get_obs_json(api_key, series_id, realtime_start = "",
                          realtime_end = "", limit = "", offset = "",
                          sort_order = "", observation_start = last_date, observation_end = "",
                          units = "", frequency = "", aggregation_method = "", 
                          output_type = "", vintage_dates="",save_graph = False)
        # Check if series is up-to-date
          # try to get observations using the last date as the start date
        # Update if necessary
        if (len(rt.df) > 1):
            df = rt.df.iloc[1:]
            df.to_sql(series_id,conn,if_exists='append')
            print len(df)," additional observations added"
            # Update series_info
            
        else:
            print series_id+" is up to date"
    else:
        # Create series
        rt = get_obs_json(api_key, series_id, realtime_start = "",
                          realtime_end = "", limit = "", offset = "",
                          sort_order = "", observation_start = "", observation_end = "",
                          units = "", frequency = "", aggregation_method = "", 
                          output_type = "", vintage_dates="")
        rt.df.to_sql(series_id,conn)
        print series_id," created"
        # ADD TO series_info
        query_head = "INSERT INTO Series_info ("
        query_tail = "("
        
        for key,val in rt.db_data.items():
            query_head += "`"+str(key) +"`"+ ","
            if (str(key) == "n") or (str(key) == "n_missing"):
                query_tail += str(val) + ","
            else:
                query_tail += "'"+str(val) +"'"+ ","
        
        query_head = query_head[:-1]+") VALUES "
        query_tail = query_tail[:-1]+")"
        query = query_head + query_tail
        #print query
        cur.execute(query)
        conn.commit()
        conn.close()
        print "Series_info updated"
    return 