queries = ["" for i in range(0, 17)]

### 0. Report the votes for the normal (i.e, not special) Senate Election in Maryland in 2018.
### Output column order: candidatename, candidatevotes
### Order by candidatename ascending
queries[0] = """
select candidatename, partyname, candidatevotes
from sen_state_returns
where year = 2018 and statecode = 'MD' and specialelections = False
order by candidatename asc;
"""

### 1. Report the number of votes for candidate 'Ben Cardin' across all the senate elections.
### Output Column: year, statecode, specialelections, candidatevotes 
### Order by candidatevotes increasing
queries[1] = """
select year, statecode,specialelections,candidatevotes
from sen_state_returns
where candidatename = 'Ben Cardin'
order by candidatevotes asc;
"""


### 2. Write a query to output the % increase, truncated to whole integer using TRUNC, in the population from 1950 to 2010.
### So for Autauga, the answer would be: 200  (54571-18186)*100/18186 = 200.7 ==> truncated to 200
### There are some counties with 0 population in 1950 -- remove those counties from the answer.
### Output columns: countyname, statecode, percentincrease
### Order output by precentincrease increasing
queries[2] = """
select name, statecode, TRUNC((population_2010-population_1950)*100/population_1950) as percentincrease
from counties
where population_1950 != 0
order by percentincrease asc;
"""

### 3. Select all the "distinct" party names that senate candidates have been affiliated over all
### the elections. 
### Output column: partyname
### Order output by partyname ascending
queries[3] = """
select distinct partyname
from sen_state_returns
order by partyname asc;
"""

### 4. Write a query to output for each state how many years ago it was admitted to the union, assuming the current year is 2020. 
### So if a state was admitted to the union in 1819, the answer would 201 (2020 - 1819). Ignore the specific dates.
### Output columns: name, admittedduration
### Order by admittedduration decreasing
queries[4] = """
select name,(2020- extract(year from admitted_to_union)) as admittedduration
from states
order by admittedduration desc ;
"""

### 5. Write a query to find the states where the increase in population from 1900 to 1950 was lower than the increase in population from 2000 to 2010.
### Output Column: name
### Order by: name increasing
queries[5] = """
select name
from states s
where (s.population_1950-s.population_1900) < (s.population_2010-population_2000)
order by name asc;
"""

### 6. Write a query to find all candidates for senate who satisfy one of the following conditions:
###        - the candidate is a 'democrat' and has more than 750000 votes in Alabama.
###        - the candidate is a 'republican' and has more 1,000,000 votes in Maryland.
###        - the candidate is neither a democrat or nor a republican and has more than 500,000 votes (in any state).
### Some candidates appear under multiple party names. Ignore that for now (in other words, if a democrat has 700,000 votes in AL as a 'democrat' and
### also gets 100,000 votes as something else, that candidate should NOT be in the result
### Also: ignore any party names like 'democratic-farmer-labor' etc.
### Output columns: year, statecode, specialelections, candidatename, partyname
queries[6] = """
(select year, statecode, specialelections, candidatename, partyname
from sen_state_returns s
where s.partyname = 'democrat' and s.statecode = 'AL' and s.candidatevotes >750000)
union
(select year, statecode, specialelections, candidatename, partyname
from sen_state_returns s
where s.partyname = 'republican' and s.statecode = 'MD' and s.candidatevotes >1000000)
union
(select year, statecode, specialelections, candidatename, partyname
from sen_state_returns s
where s.partyname != 'democrat' and s.partyname != 'republican'  and s.candidatevotes >500000);

"""


### 7. Write a query to join the tables states and counties to create a list of county names, county population in 2010, state name, the state
### population in 2010
### Output columns: statename, statepopulation, countyname, countypopulation
### Order first by statename, then by countyname, increasing
queries[7] = """
select s.name as statename,s.population_2010 as 
statepopulation, c.name as countyname , c.population_2010 as countypopulation
from states s, counties c
where c.statecode =s.statecode
order by statename, countyname ASC
;

"""

### 8. Write a query to join the tables states and counties to find the counties that had over
### 50% of the population of the state in 2010
### Output columns: statename, countyname 
### Order by statename, then by countyname, increasing
queries[8] = """
select s.name as statename, c.name as countyname
from counties c
inner join states s
on  s.statecode = c.statecode
where c.population_2010*1.00000000000000000/s.population_2010 > .5
;
"""



### 9. The tables were collected from 2 different sources, and there may be some consistency issues across them. 
### Write a query to find all counties (and the corresponding state names) that are present in "pres_county_returns" table, but 
### do not have any correhtforward string equality -- so 'Autauga' and 'Autauga ' (with an extra space) would NOT be considered a match.
### Each county+state combination should only appear once in the output.
### HINT: Use "not in".
### Output Columns: countyname, statename
### Order by name, statecode ascending
queries[9] = """
select distinct c.countyname, s.name as statename
from pres_county_returns c
left join states s
on s.statecode = c.statecode
where countyname not in (select name from counties) and c.statecode in (select statecode from states)
order by c.countyname,statename asc;

"""



### 10. Write a query to join sen_state_returns and sen_elections to find the candidates that received 70% or more of the total vote.
### Output columns: year, statecode, specialelections, candidatename
### Order by percentage of total vote increasing
queries[10] = """
select distinct ss.year,ss.statecode,ss.specialelections,candidatename
from sen_state_returns ss
left join sen_elections se
on se.statecode = ss.statecode and se.year = ss.year
where ss.candidatevotes*1.00000 / se.totalvotes >= .7
 ;

"""


### 11. For the 2012 presidential elections and for 'Barack Obama', write a
### query to combine pres_county_returns and counties so that, to produce a result
### with the following columns:
###     countyname, statecode, candidatevotes, population_2010
### However, for the counties in pres_county_returns that do not have a match in 
### 'counties' table, we want population_2010 to be set to NULL.
### Use a left (or right) outer join to achive this.
### Output: countyname, statecode, candidatevotes, population_2010
### Order by: countyname, statecode ascending
queries[11] = """
select p.countyname,p.statecode,p.candidatevotes,c.population_2010
from pres_county_returns p 
left join counties c
on c.name = p.countyname and c.statecode=p.statecode
where p.year = '2012' and candidatename = 'Barack Obama'
order by countyname, statecode asc
;
"""


### 12. SQL "with" clause can be used to simplify queries. It essentially allows
### specifying temporary tables to be used during the rest of the query. See Section
### 3.8.6 (6th Edition) for some examples.
###
### Below we are providing a part of a query that uses "with" to create a
### temporary table where, for 2000 elections, we are finding the maximum of the
### candidate votes for each county. Join this temporary table with the
### 'pres_county_returns' table to find the winner for each county. 
### This is unfortunately the easiest way to do this task.
###
### You don't need to fully understand what the 'temp' query does to do the join
### -- as provided, the query shows you the result of the "temp" table
### Output columns: countyname, statecode, candidatename
### Order by: countyname, statecode, candidatename
queries[12] = """
with temp as (select countyname, statecode, max(candidatevotes) as maxvotes
        from pres_county_returns
        where year = 2000
        group by countyname, statecode)
select p.countyname, p.statecode, p.candidatename
from pres_county_returns p
left join temp t
on t.countyname = p.countyname and p.statecode = t.statecode 
where p.candidatevotes = t.maxvotes
"""


### 13. List the top ten most common names used for counties across the states. 
###
### Output columns: countyname, num
### Order by num, countyname
queries[13] = """
select name as countyname, count(name) as num
from counties
group by name
order by num desc, countyname 
limit 10;
"""


### 14. Let's create a table showing the vote differences between 2000 and 2016 for
### the democratic presidential candidates in each county. 
### We ONLY want those states/counties for which we have all the information.
### Output: statecode, countyname, votes2000, votes2016
### Order by: statecode, countyname ascending
queries[14] = """
select p1.statecode,p1.countyname, sum(p1.candidatevotes) as votes2000, sum(p2.candidatevotes) as votes2016
from pres_county_returns as p1
inner join pres_county_returns as p2

on p1.statecode = p2.statecode and p1.countyname = p2.countyname
where p1.year = '2000' and p2.year = '2016' and p1.partyname = 'democrat' and p2.partyname = 'democrat'

group by p1.statecode, p1.countyname

order by statecode, countyname asc;
"""


### 15. Write a statement to add a new column to the counties table called 'pop_trend' of type 'string'.
queries[15] = """
alter table counties
add pop_trend varchar;
"""

### 16. The values for the above added column with be empty to begin with. Write an update statement to 
### set it to 'decreased', 'increased somewhat', and 'increased a lot', depending on whether the population decreased,
### increased by less than a factor of 2 (i.e., population_2010 <= 2*population_1950), or increased by a factor of more than 2.
### Use CASE statement to make this easier.
queries[16] = """
update counties
set pop_trend =
case
        when counties.population_2010 < population_1950
                then  'decreased'
        when counties.population_2010 <= 2*population_1950
                then 'increased somewhat'
        when counties.population_2010 >= 2*population_1950
                then  'increased a lot'
        end
;
"""


