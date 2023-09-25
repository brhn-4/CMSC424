
from peewee import *
from datetime import date
from datetime import datetime
import json


database = PostgresqlDatabase('flightsskewed', **{'host': 'localhost','user': 'vagrant', 'password': 'vagrant'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Airports(BaseModel):
    airportid = CharField(primary_key=True)
    city = CharField(null=True)
    name = CharField(null=True)
    total2011 = IntegerField(null=True)
    total2012 = IntegerField(null=True)
    class Meta:
        table_name = 'airports'

class Airlines(BaseModel):
    airlineid = CharField(primary_key=True)
    hub = ForeignKeyField(column_name='hub', field='airportid', model=Airports, null=True)
    name = CharField(null=True)
    class Meta:
        table_name = 'airlines'

class Customers(BaseModel):
    birthdate = DateField(null=True)
    customerid = CharField(primary_key=True)
    frequentflieron = ForeignKeyField(column_name='frequentflieron', field='airlineid', model=Airlines, null=True)
    name = CharField(null=True)
    class Meta:
        table_name = 'customers'

class Flights(BaseModel):
    airlineid = ForeignKeyField(column_name='airlineid', field='airlineid', model=Airlines, null=True)
    dest = ForeignKeyField(column_name='dest', field='airportid', model=Airports, null=True)
    flightid = CharField(primary_key=True)
    local_arrival_time = TimeField(null=True)
    local_departing_time = TimeField(null=True)
    source = ForeignKeyField(backref='airports_source_set', column_name='source', field='airportid', model=Airports, null=True)
    class Meta:
        table_name = 'flights'

class Flewon(BaseModel):
    customerid = ForeignKeyField(column_name='customerid', field='customerid', model=Customers, null=True)
    flightdate = DateField(null=True)
    flightid = ForeignKeyField(column_name='flightid', field='flightid', model=Flights, null=True)
    class Meta:
        table_name = 'flewon'

class Numberofflightstaken(BaseModel):
    customerid = CharField(null=True)
    customername = CharField(null=True)
    numflights = IntegerField(null=True)
    class Meta:
        table_name = 'numberofflightstaken'
        primary_key = False

def runORM(jsonFile):
        with open(jsonFile) as f:
        
            for line in f:
                tmp_line = json.loads(line)
               
                
                if 'flewon' in tmp_line: #flewon
                    
                    F_id = tmp_line['flewon']['flightid']
                    date = tmp_line['flewon']['flightdate']
                    customers = tmp_line['flewon']['customers']
                    count = Flewon.select().count()

                    for customer in customers: #each customer in customers dict
                        if 'customerid' in customer:
                            cust_id = customer['customerid']
                        if 'name' in customer:
                            c_name = customer['name']
                        if 'birthdate' in customer:
                            bday = customer['birthdate']
                        if 'frequentflieron' in customer:
                            ff = customer['frequentflieron']

                        
                            flag1 = Airlines.select().where(Airlines.airlineid == ff)

                            if  flag1 is None:
                                    print("Error424")
                                    exit()
                        flag2 = Customers.select().where(Customers.customerid == cust_id)
                        
                        

                        if flag2.exists() is False:
                            temp = Customers(name = c_name,customerid = cust_id,birthdate = bday,frequentflieron = ff)
                            temp.save(force_insert=True)

                        count = count + 1

                        temp = Flewon(flightid =F_id,customerid = cust_id,flightdate = date,id = str(count))
                        temp.save(force_insert=True)

                else:  #new customer
                    if 'customerid' in tmp_line['newcustomer']:
                        id = tmp_line['newcustomer']['customerid']
                    if 'name' in tmp_line['newcustomer']:
                        c_name = tmp_line['newcustomer']['name']
                    if 'birthdate' in tmp_line['newcustomer']:
                        bday = tmp_line['newcustomer']['birthdate']
                    if 'frequentflieron' in tmp_line['newcustomer']:
                        ff = tmp_line['newcustomer']['frequentflieron']

                    flag1 = Customers.select().where(Customers.customerid ==id)
                    flag2 = Airlines.select().where(Airlines.name == ff)
                
                    
                    if flag1 or flag2 is None:
                        print("Error424")
                        exit()
                    else:             
                        temp = Customers(customerid = id,name = c_name,birthdate = bday,frequentflieron = flag2[0].airlineid)
                        temp.save(force_insert=True)
            ##Num flights
            qry = Numberofflightstaken.delete()
            qry.execute()

            grouping = (Flewon.select(Flewon.customerid,Customers.name,fn.Count(Flewon.customerid).alias('numflights'))
                        .join(Customers, JOIN.LEFT_OUTER)
                        .group_by(Flewon.customerid,Customers.name))
            
            qry2 = (Numberofflightstaken
                    .insert_from(
                        grouping,fields = [Numberofflightstaken.customerid,Numberofflightstaken.customername,Numberofflightstaken.numflights])
                    .execute())
            





    #Customers.delete().where(Customers.name == 'bob').execute()
    #Airports.delete().where(Airports.airportid == 'PET').execute()
        
    #bob = Customers(name="bob", customerid='cust1010', birthdate='1960-01-15', frequentflieron='SW')
    #bob.save(force_insert=True)
    
    #bwi = Airports(airportid='PET', city='Takoma', name='Pete', total2011=2, total2012=4)
    #bwi.save(force_insert=True)
    
    #for port in Airports.select().order_by(Airports.name):
    #    print (port.name)
