#!/usr/bin/python3
import psycopg2
import json
import sys
from types import *

def runPsy(conn, curs, jsonFile):
    with open(jsonFile) as f:
        
        for line in f:
            tmp_line = json.loads(line)

            print(tmp_line)

            if 'flewon' in tmp_line: #flewon
                F_id = tmp_line['flewon']['flightid']
                date = tmp_line['flewon']['flightdate']
                customers = tmp_line['flewon']['customers']
                curs.execute('select count(*) from flewon')  #id of row is the count of all rows
                count = curs.fetchone()[0]
                
            
                for customer in customers: #each customer in customers dict
                    if 'customerid' in customer:
                        cust_id = customer['customerid']
                    if 'name' in customer:
                        name = customer['name']
                    if 'birthdate' in customer:
                        bday = customer['birthdate']
                    if 'frequentflieron' in customer:
                        ff = customer['frequentflieron']
                        

                        
                        curs.execute("select name from airlines where airlineid = \'"+ ff +"\'")  #frequent flier doesn't match airline
                        flag2 = curs.fetchone()
                       
                        if  flag2 is None:
                            print("Error424")
                            exit()

                    curs.execute('select customerid from customers where customerid = \'' + str(cust_id) +'\'')
                    if  curs.fetchone() is None:   #customer DNE
                        curs.execute('INSERT INTO customers(customerid,name,birthdate,frequentflieron) values(\''+str(cust_id)+'\',\''+str(name)+'\',\''+bday+'\',\'' +ff+'\')')
                    
                    count = count + 1
                    curs.execute('INSERT INTO flewon(flightid,customerid,flightdate,id) values(\''+ F_id + '\',\'' + cust_id + '\',\'' + date +'\','+str(count)+')' )

                    

                    
               
               
                #insert into flewon
             
                  
            else:  #new customer

               #data
                if 'customerid' in tmp_line['newcustomer']:
                    id = tmp_line['newcustomer']['customerid']
                if 'name' in tmp_line['newcustomer']:
                    name = tmp_line['newcustomer']['name']
                if 'birthdate' in tmp_line['newcustomer']:
                    bday = tmp_line['newcustomer']['birthdate']
                if 'frequentflieron' in tmp_line['newcustomer']:
                    ff = tmp_line['newcustomer']['frequentflieron']
               
          
                #check if exists
                curs.execute('select customerid from customers where customerid = \'' + id +'\'')
                flag = curs.fetchone()
                curs.execute('select airlineid from airlines where name = \'' + ff+'\'')
                flag2 = curs.fetchone()[0]
                ff = flag2

                
                if flag or flag2 is None:
                    print("Error424")
                    exit()
                else:
                    
                    curs.execute('INSERT INTO customers(customerid,name,birthdate,frequentflieron) values(\'' +str(id)+'\',\''+str(name)+'\',\''+bday+'\',\'' +ff+'\')')


            
##      load in line. change to string. use execute to write sql queries (check for errrors). execute for inserting as well ...

        conn.commit()
      
