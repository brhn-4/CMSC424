# EXPLANATION: The given left-join query fails because our intended conditional (name like william%) is inside the 'on' clause, which is used 
# to match columns for the left join. Not to give conditionals that is why we return an unintended output. Additionally when we count(*) we 
# count each row from customers which includes the entries with name like william but do not appear in flewon. To correct this, we will count(f.flight id)
# which appears for each person for each flight (i.e wont appear under custid that have not flown). Now we will show each name like william but our count for each 
# of those will be based on their appearance in flewon

# Below is the correct query
#
#
queryWilliam = """
select c.customerid, c.name, count(f.flightid)
from customers c left outer join flewon f on (c.customerid = f.customerid ) 
where c.name like 'William%'
group by c.customerid, c.name
order by c.customerid;

"""


# NOTE:  This trigger is both INCORRECT and INCOMPLETE. You need to find and fix the bugs, and ensure
# that it will correctly update NumberOfFlightsTaken on both insertions and deletions from "flewon".
queryTrigger = """

CREATE OR REPLACE FUNCTION updateStatusCount() RETURNS trigger AS $updateStatus$
		DECLARE
			old_flight_count integer;
            c_name varchar(250);
		BEGIN
            
                
            IF (TG_OP = 'INSERT') THEN
                IF EXISTS (SELECT customerid FROM NumberOfFlightsTaken WHERE customerid = NEW.customerid) THEN
                    UPDATE NumberOfFlightsTaken
                    SET numflights = numflights + 1
                    WHERE customerid = NEW.customerid;
                ELSE
                    select name into c_name
                    from customers
                    where customerid = NEW.customerid;

                    INSERT into NumberOfFlightsTaken(customerid,customername,numflights)
                    values(NEW.customerid,c_name,1);
                    
                END IF;
            ELSEIF (TG_OP = 'DELETE') then
                select numflights into old_flight_count 
                from NumberOfFlightsTaken
                where customerid = OLD.customerid;

                IF(old_flight_count != 1) then
                    UPDATE NumberOfFlightsTaken
                    SET numflights = numflights - 1
                    WHERE customerid = OLD.customerid;
                ELSE
                    DELETE from NumberOfFlightsTaken
                    where customerid = OLD.customerid;
                END IF;
            END IF;
        RETURN NULL;
        
		END;
$updateStatus$ LANGUAGE plpgsql;

CREATE TRIGGER update_num_status AFTER 
INSERT OR DELETE ON flewon
FOR EACH ROW EXECUTE PROCEDURE updateStatusCount();
END;
"""
