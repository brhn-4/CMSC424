queries = ["" for i in range(0, 19)]

### 0. Report the votes for the normal (i.e, not special) Senate Election in Maryland in 2018.
### Output column order: candidatename, partyname, candidatevotes
### Order by candidatename ascending
queries[0] = """
select candidatename, partyname, candidatevotes
from sen_state_returns
where specialelections = 'f' and year = 2018 and statecode = 'MD'
order by candidatename asc;
"""

### 1. Write a query to find the maximum, minimum, and average population in 2010 across all states.
### The result will be a single row.
### Truncate the avg population to a whole number using trunc
### Output Columns: max_population, min_population, avg_population
queries[1] = """
select trunc(max(population_2010))as max_population,trunc(min(population_2010)) as min_population, trunc(avg(population_2010))as avg_population
from states;

"""

### 2. Write a query to find the candidate with the maximum votes in the 2008 MI Senate Election. 
### Output Column: candidatename
### Order by: candidatename
queries[2] = """
select candidatename
from sen_state_returns
where statecode = 'MI' and year = 2008 and candidatevotes = 

(select max(candidatevotes)
from sen_state_returns 
where statecode = 'MI' and year = 2008)

"""

### 3. Wite a query to find the number of candidates who are listed in the sen_state_returns table for each senate election held in 2018. 
### Note that there may be two elections in some states, and there should be two tuples in the output for that state.
### 'NA' or '' (empty) should be treated as candidates. 
### Output columns: statecode, specialelections, numcandidates
### Order by: statecode, specialelections
queries[3] = """


select statecode,specialelections,count(candidatename) as numcandidates
from sen_state_returns
where year = 2018
group by statecode, specialelections
order by statecode, specialelections;
"""

### 4. Write a query to find, for the 2008 elections, the number of counties where Barack Obama received strictly more votes 
### than John McCain.
### This will require you to do a self-join, i.e., join pres_county_returns with itself.
## Output columns: num_counties

###select p1.statecode,p1.countyname,p1.candidatename,p1.candidatevotes,p2.candidatename,p2.candidatevotes
##from pres_county_returns p1
##left join pres_county_returns p2
##on p1.countyname = p2.countyname and p2.statecode = p2.statecode and p1.year = p2.year   5505
##where p1.candidatename = 'Barack Obama' and p2.candidatename = 'John McCain' and p1.candidatevotes > p2.candidatevotes;

queries[4] = """
select  count(*)
from pres_county_returns p1
left join pres_county_returns p2
on p1.countyname = p2.countyname and p1.statecode = p2.statecode and p1.year = p2.year
where p1.candidatename = 'Barack Obama' and p2.candidatename = 'John McCain'  and p1.year = 2008 and p1.candidatevotes > p2.candidatevotes
;





"""


### 5. Write a query to find the names of the states with at least 100 counties in the 'counties' table.
### Use HAVING clause for this purpose.
### Output columns: statename, num_counties
### Order by: statename
queries[5] = """
select s.name as statename, count(*) as num_counties
from counties c 
left join states s
on c.statecode = s.statecode
group by statename
having count(c.statecode)>99
order by statename;


;
"""

### 6. Write a query to construct a table:
###     (statecode, total_votes_2008, total_votes_2012)
### to count the total number of votes by state for Barack Obama in the two elections.
###
### Use the ability to "sum" an expression (e.g., the following query returns the number of counties in 'AR')
### select sum(case when statecode = 'AR' then 1 else 0 end) from counties;
###
### Order by: statecode
queries[6] = """
select  statecode,
 sum(case when candidatename = 'Barack Obama' and year = 2008 then candidatevotes else 0 end) as total_votes_2008, 
 sum(case when candidatename = 'Barack Obama' and year = 2012 then candidatevotes else 0 end) as total_votes_2012
from pres_county_returns
group by statecode
order by statecode;
"""

### 7. Create a table to list the disparity between the populations listed in 'states' table and those listed in 'counties' table for 1950 and 2010.
### Result should be: 
###        (statename, disparity_1950, disparity_2010)
### So disparity_1950 = state population 1950 - sum of population_1950 for the counties in that state
### Use HAVING to only output those states where there is some disparity (i.e., where at least one of the two is non-zero)
### Order by statename
queries[7] = """
with t1 (statecode,sum_1950,sum_2010) as (select statecode, sum(population_1950),sum(population_2010)
from counties
group by statecode)


select s.name, s.population_1950 - sum_1950 as disparity_1950, s.population_2010 - sum_2010 as disparity_2010
from states s
inner join t1
on t1.statecode = s.statecode
where s.population_1950 - sum_1950 != 0 or  s.population_2010 - sum_2010 != 0;


"""

### 8. Use 'EXISTS' or 'NOT EXISTS' to find the states where no counties have population in 2010 above 500000 (500 thousand).
### Output columns: statename
### Order by statename
queries[8] = """
select name as statename
from states  s
where not exists(
    select s.statecode 
    from counties
    where counties.population_2010 > 500000  and s.statecode = counties.statecode
)  
order by statename
;
"""

### 9. List all counties and their basic information that have a unique name across all states. 
### Use scalar subqueries to simplify the query.
### Output columns: all attributes of counties (name, statecode, population_1950, population_2010)
### Order by name, statecode
queries[9] = """
with temp(name) as(
select name from counties
group by name
having count(*) = 1)

select * from counties 
where counties.name in (select name from temp)
order by name, statecode;



"""

### 10. Identify counties that witnessed a population decline between 1950 - 2010 despite belonging to states that witnessed a population growth in the same period. 
### Ouput columns: name, statecode, population_decline
### Order by: population_decline descending.
### Possible solution:
queries[10] = """
with temp(code,change) as(
    select s.statecode, s.population_2010-s.population_1950 
    from states s
    where s.population_2010-s.population_1950 >0
)
select name,statecode, (counties.population_2010-counties.population_1950)*-1 as population_decline from counties 
where counties.statecode in (select code from temp) and (counties.population_2010-counties.population_1950 <0)
order by  population_decline desc
;

"""

### 11. Use Set Intersection to find the counties that Barack Obama lost in 2008, but won in 2012.
###
### Output columns: countyname, statecode
### Order by countyname, statecode

##year,countyname,statecode,candidatename,candidatevotes,temp1.votes
queries[11] = """
select * from (
(with temp1 (state,county, votes) as (
    select statecode,countyname, max(candidatevotes)
    from pres_county_returns
    where year = 2008
    group by  statecode,countyname 
    
)
(select countyname,statecode
from pres_county_returns p
left join temp1
on temp1.county = p.countyname and temp1.state = p.statecode
where p.year  =2008 and p.candidatename = 'Barack Obama' and p.candidatevotes != temp1.votes
order by countyname,statecode
))

intersect

(with temp2 (state,county, votes) as (
    select statecode,countyname, max(candidatevotes)
    from pres_county_returns
    where year = 2012
    group by  statecode,countyname 
    
)
(select countyname,statecode
from pres_county_returns p2
left join temp2
on temp2.county = p2.countyname and temp2.state = p2.statecode
where p2.year  =2012 and p2.candidatename = 'Barack Obama' and p2.candidatevotes = temp2.votes
order by countyname,statecode
))) as result order by countyname,statecode asc;

"""


### 12. The anti-join of two relations A and B over some predicate P is defined to be the all of the tuples
### A_i of relation A where there is no matching B_j in B such that (A_i, B_j) satisfies P.
### When exploring unknown datasets the anti-join can be useful to identify anomalies or inconsistencies in  
### names and identifiers across tables in the dataset.
### Find the anti-join of `counties` with `pres_county_returns` to identify counties from the `counties` table
### where no votes have been recorded.
### Output columns: statecode, name
### Order by: statecode, name
queries[12] = """
select c.statecode, c.name
from counties c
where not exists(
    select p.candidatevotes
    from pres_county_returns p
    where p.statecode = c.statecode and p.countyname = c.name
)

;
"""

### 13. Find all presidential candidates listed in pres_county_returns who also ran for senator.
### HINT: Use "intersect" to simplify the query
###
### Every candidate should be reported only once. 
###
### Output columns: candidatename
### Order by: candidatename
queries[13] = """
(select distinct candidatename 
from pres_county_returns
where candidatename != 'Other')
intersect
(select distinct candidatename
from sen_state_returns
where candidatename != 'Other')


;
"""

### 14. Create a table listing the months and the number of states that were admitted to the union (admitted_to_union field) in that month.
### Use 'extract' for operating on dates, and the ability to create a small inline table in SQL. For example, try:
###         select * from (values(1, 'Jan'), (2, 'Feb')) as x;
###
### Output columns: month_no, monthname, num_states_admitted
### month should take values: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
### Order by: month_no
queries[14] = """
with temp1 (month_no,cnt) as (
    select extract(month from admitted_to_union) as month_no, count(*)
    from states
    group by month_no
    order by month_no asc
),
 temp2 (month_no,monthname) as
(select * from (values(1,'Jan'),(2,'Feb'),(3,'Mar'),(4,'Apr'),(5,'May'),(6,'Jun'),(7,'Jul'),(8,'Aug'),(9,'Sep'),(10,'Oct'),(11,'Nov'),(12,'Dec'))as x)


select temp1.month_no, temp2.monthname, cnt as num_states_admitted
from temp1
left join temp2 
on temp1.month_no = temp2.month_no


 ;
"""


### 15. Create a view pres_state_votes with schema (year, statecode, candidatename, partyname, candidatevotes) where we maintain aggregated counts by statecode (i.e.,
### candidatevotes in this view would be the total votes for each state, including states with statecode 'NA'). XX
queries[15] = """
create view pres_state_votes as
select year, statecode, candidatename,partyname,sum(candidatevotes) as candidatevotes
from pres_county_returns
group by year,statecode,candidatename,partyname


;
"""

### 16. Use a single ALTER TABLE statement to add (name, statecode) as primary key to counties, and to add CHECKs that neither of the two populations are less than zero.
### Name the two CHECK constraints nonzero2010 and nonzero1950. XX
queries[16] = """
alter table counties
    add constraint pk primary key (name,statecode),
    add constraint nonzero2010 check (population_2010 >= 0),
    add constraint nonzero1950 check (population_1950 >= 0)

;
"""

### 17. Create a list of percentage each presidential candidate won in each state, in each year, and
### show only the top 10 (among all year and state) in descending order. "totalvotes" should be the total
### votes cast in the presidential election for each year and state. "percentvote" should be a float
### with one digit to the right of the decimal point.
### Output columns: year, statecode, candidatename, candidatevotes, totalvotes, percentvote
### Order by: percentvote desc, year asc, candidatename asc, limit to 10 lines

queries[17] = """
with temp1 (year,statecode,totalvotes) as(
    select year,statecode,sum(candidatevotes)
    from pres_county_returns
    group by year,statecode
)

select p.year,p.statecode,p.candidatename,p.candidatevotes,t.totalvotes, round((candidatevotes*100.0/totalvotes),1 )as percentvote
from pres_state_votes p
left join temp1 t
on p.year = t.year and p.statecode = t.statecode
where totalvotes != 0
order by percentvote desc, year asc, candidatename asc
limit 10;

"""

### 18. Create a list of percentage of people who turned out to vote for each state in the presidential election of 2000
### in descending order. "percentturnout" should be a float with one digit to the right of the decimal point.
### Output columns: statecode, percentturnout
### Order by: percentageturnout desc;
queries[18] = """
with temp1 (statecode,totalvotes) as(
    select statecode,sum(candidatevotes)
    from pres_county_returns
    where year = 2000
    group by year,statecode   
)
select states.statecode, round((totalvotes*100.0/population_2000),1) as percentageturnout
from states
left join temp1
on states.statecode = temp1.statecode
order by percentageturnout desc;
"""