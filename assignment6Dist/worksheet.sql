-- createdb tst
-- psql tst

drop table rs;
drop table st;
create table rs (a int, b int);
create table st (b int, c int);

insert into rs values (1, 2);
insert into rs values (1, 2);
insert into rs values (2, 2);
insert into rs values (3, 3);
insert into rs values (4, 3);

insert into st values (2, 1);
insert into st values (2, 2);
insert into st values (5, 1);
insert into st values (6, 2);

-- semi join (wrong)
(SELECT * FROM rs) EXCEPT ((SELECT * FROM rs) EXCEPT (SELECT rs.* FROM rs NATURAL JOIN st));

-- semi join (right)
(SELECT * FROM rs) EXCEPT ALL ((SELECT * FROM rs) EXCEPT (SELECT rs.* FROM rs NATURAL JOIN st));

-- anti join
(SELECT * FROM rs) EXCEPT (SELECT rs.* FROM rs NATURAL JOIN st);

