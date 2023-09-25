import psycopg2
import os
import sys
import datetime
from collections import Counter
from types import *
import argparse
import pickle

from queries import *

correct_answers = []

def pout(ans):
    print("--------- Your Query Answer ---------")
    for t in ans:
        print(t)
    print("")

def executePrint(s):
        cur.execute(s)
        ans = cur.fetchall()
        print(ans)
        return ans

correct_answers = []

conn = psycopg2.connect("dbname=flightsskewed user=vagrant")
cur = conn.cursor()

try:
    print("========== Executing William")
    print(queryWilliam)

    cur.execute(queryWilliam)
    conn.commit()
    ans = cur.fetchall()
    correct_answers.append(ans)
    pout(ans)

    ## TRIGGER
    cur.execute("insert into flewon values ('F9103', 'cust597', to_date('2016-08-04', 'YYYY-MM-DD')) ON CONFLICT DO NOTHING;")
    cur.execute("insert into flewon values ('AA134', 'cust597', to_date('2016-08-05', 'YYYY-MM-DD')) ON CONFLICT DO NOTHING;")
    cur.execute("delete from flewon where customerid = 'cust731';")

    cur.execute("drop trigger if exists update_num_status on flewon;")
    cur.execute("drop function if exists updateStatusCount;")
    cur.execute("drop table if exists NumberOfFlightsTaken;")
    cur.execute("create table NumberOfFlightsTaken as select c.customerid, c.name as customername, count(*) as numflights from customers c join flewon fo on c.customerid = fo.customerid group by c.customerid, c.name;")
    cur.execute(queryTrigger)
    conn.commit()
    
    ## Make sure not there already
    print("==== Testing: customer without a flewon entry")
    cur.execute("SELECT COUNT(*) FROM NumberOfFlightsTaken WHERE customerid = 'cust731';")
    ans = cur.fetchall()
    pout(ans)
    correct_answers.append(ans)
    conn.commit()

    print("Inserting a flewon entry for cust731")
    cur.execute("insert into flewon values ('AA101', 'cust731', to_date('2016-08-09', 'YYYY-MM-DD'));")
    conn.commit()

    print("Rerunning the query")
    cur.execute("SELECT COUNT(*) from NumberOfFlightsTaken where customerid = 'cust731';")
    ans = cur.fetchall()
    pout(ans)
    correct_answers.append(ans)
    conn.commit()

    ## Remove a customer with a few entries 
    print("==== Testing: looking at a customer's flewon entries")
    executePrint("SELECT COUNT(*) from NumberOfFlightsTaken where customerid = 'cust597';")
    conn.commit()

    print("Rerunning the query after deleting one entry")
    cur.execute("delete from flewon where customerid = 'cust597' and flightid = 'F9103';")
    conn.commit()
    cur.execute("SELECT COUNT(*) from NumberOfFlightsTaken where customerid = 'cust597';")
    ans = cur.fetchall()
    pout(ans)
    correct_answers.append(ans)
    conn.commit()

    cur.execute("delete from flewon where customerid = 'cust597' and flightid = 'AA134'")
    conn.commit()

    print("Rerunning the query after deleting both entries")
    cur.execute("SELECT COUNT(*) from NumberOfFlightsTaken where customerid = 'cust597'")
    ans = cur.fetchall()
    pout(ans)
    correct_answers.append(ans)
    conn.commit()
except:
    print(sys.exc_info())
    raise

            

with open("correct_answers.pickle", "wb") as f:
    pickle.dump(correct_answers, f)

print("wrote {} answers".format(len(correct_answers)))
