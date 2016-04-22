
# Script to create the databases
#  - only necessary when you first create the app
#  - make sure you add the mysql cartidge to your app first
#       $ rhc cartridge add mysql-5.5 -a APPNAME

# How to run this script
#  - ssh into your app
#       $ rhc ssh APPNAME
#  - run the script
#       $ mysql DB_NAME < initializeDatabase.sql

# create the "person" table
CREATE TABLE person (
cik bigint NOT NULL,
Name varchar(255),
LP double,
LIHO double,
PRIMARY KEY (cik)
);

# create the "form" table
CREATE TABLE forms (
	id INT NOT NULL AUTO_INCREMENT,
cik bigint NOT NULL,
url varchar(2083) NOT NULL,
date date,
PRIMARY KEY (id),
FOREIGN KEY (cik)
      REFERENCES person(cik)
);

# stored procedure to add a person
DELIMITER //
CREATE PROCEDURE add_person(p_cik VARCHAR(20), p_name VARCHAR(20), p_LP VARCHAR(20), p_LIHO VARCHAR(20))
BEGIN
insert into person (cik, name, LP, LIHO )
values (p_cik, p_name, p_LP, p_LIHO );
END//
DELIMITER ;

# stored procedure to add a forms
DELIMITER //
CREATE PROCEDURE add_form(p_cik bigint, p_url varchar(2083), p_date date)
BEGIN
insert into forms (cik, url, date )
values (p_cik, p_url, p_date );
END//
DELIMITER ;

# stored procedure to select cik, name, lp, form.date, form.url
DELIMITER //
CREATE PROCEDURE getDailyReport(r_date date)
BEGIN
select p.cik, p.Name, p.LP, f.url, f.date 
from person p, forms f
where p.cik = f.cik && f.date = r_date
order by p.lp asc;
END//
DELIMITER ;