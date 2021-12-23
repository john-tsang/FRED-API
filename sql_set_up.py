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