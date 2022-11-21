set global sql_mode='';
SET SQL_SAFE_UPDATES = 0;

drop schema assignment2;
create schema assignment2;

create table assignment2.diseasetype(
	id integer,
    description varchar(140),
    primary key(id)
);

create table assignment2.country(
	cname varchar(50),
    population bigint,
    primary key(cname)
);

create table assignment2.disease(
	disease_code varchar(50),
    pathogen varchar(20),
    description varchar(140),
    id integer,
    foreign key(id) references diseasetype(id),
    primary key(disease_code)
);

create table assignment2.discover(
	cname varchar(50),
    disease_code varchar(50),
    first_enc_date date,
	foreign key(cname) references country(cname),
    foreign key(disease_code) references disease(disease_code)
);

create table assignment2.users(
	email varchar(60),
    name varchar(30),
    surname varchar(40),
    salary int,
    phone varchar(20),
    cname varchar(50),
	foreign key(cname) references country(cname) on delete cascade, 
    primary key(email)
);

create table assignment2.publicservant(
	email varchar(60),
    department varchar(50),
	foreign key(email) references users(email) on delete cascade
);

create table assignment2.doctor(
	email varchar(60),
	degree varchar(20),
	foreign key(email) references users(email) on delete cascade
);

create table assignment2.specialize(
	id integer,
    email varchar(60),
	foreign key(id) references diseasetype(id),
    foreign key(email) references doctor(email) on delete cascade
);

create table assignment2.record(
    email varchar(60),
    cname varchar(50),
    disease_code varchar(50),
    total_deaths integer,
    total_patients integer,
	foreign key(disease_code) references disease(disease_code),
    foreign key(cname) references country(cname),
    foreign key(email) references publicservant(email) on delete cascade
);

insert into assignment2.diseasetype values 
	(1, "Acute Flaccid Myelitis (AFM)"),
    (2, "genetic diseases"),
    (3, "Alzheimer's Diseases"),
    (4, "respiratory illness"),
    (5, "Chancroid"),
    (6, "virology"),
    (7, "infectious diseases"),
    (8, "Clostridium Difficile"),
    (9, "Creutzfeldt-Jakob Disease"),
    (10, "physiological diseases");
    
insert into assignment2.country values 
	("the USA", 234000),
    ("England", 782999),
    ("China", 12903000),
    ("Taiwan", 1287221 ),
    ("India", 982000),
    ("Chile", 92121),
    ("Spain", 321000),
    ("United Kingdom", 213122),
	("United Arab Emirates", 672920),
	("Russia", 5672099);
    
insert into assignment2.disease values 
	("covid-19", "bacteria", "Brucella Lung", 4),
    ("injury", "Burnetii", "Coxiella", 5),
    ("blooding", "bacteria", "Brucella", 8),
    ("556", "Glanders", "Burkholderia", 6),
    ("877", "Psittacosis", "Chlamydia", 7),
    ("211", "bacteria", "Ricin", 2),
    ("091", "bacteria", "Epsilon", 3),
    ("562", "Enterotoxin", "Staphylococcus", 1),
    ("981", "bacteria", "Coxiella", 9),
    ("991", "Salmonella", "Pathogen", 10);
    
insert into assignment2.users values
	("Amir.Umralin@world.com", "Amir", "Umralin", 23000, "87075242222","China"),
    ("Dulat.Ualiyev@world.com", "Dulat", "Ualiyev", 7800, "87075221212","Taiwan"),
    ("Umral.Kaliyev@world.com", "Umral", "Kaliyev", 21000, "87077770044","the USA"),
    ("Chan.Pen@world.com", "Chanbek", "Pen", 120000, "87075333333","Chile" ),
    ("Mune.Rude@world.com", "Mune", "Rude", 21222, "87079002121","Spain" ),
    ("Cristiano.Ronaldo@world.com", "Cristiano", "Ronaldo", 1200000, "87078990922","United Kingdom"),
    ("Cobalt.Chevrolet@world.com", "Cobalt", "Chevrolet", 9800, "87078779898", "Russia"),
    ("Arman.Murza@world.com", "Arman", "Murza", 12000, "87079002211", "India"),
    ("Meepo.Mepar@world.com", "Meepo", "Mepar", 25000, "87075009211","United Arab Emirates" ),
    ("Huskar.Huskarovich@world.com", "Huskarbek", "Huskarovich", 902222, "87079000000","England" ),
	("Newby.New@world.com", "Newby", "New", 19888, "87075109211","China");
    
    
insert into assignment2.discover values
	("China","covid-19", '1983-12-05'), --
    ("Taiwan", "injury", '2002-12-09'),
    ("England", "blooding", '1900-12-09'), --
    ("the USA", "556", '1982-12-07'),
    ("United Kingdom", "877", '2005-12-11'),
    ("Russia", "211", '1890-12-03'), --
    ("Spain", "091", '2007-12-04'),
    ("India", "562", '1845-11-05'),
    ("Chile", "981", '2000-12-05'),
    ("United Arab Emirates", "991", '1899-12-05');

insert into assignment2.publicservant values
	("Amir.Umralin@world.com", "dep1"),
    ("Dulat.Ualiyev@world.com","dep1"),
    ("Umral.Kaliyev@world.com", "dep2"),
    ("Chan.Pen@world.com", "dep2"),
    ("Mune.Rude@world.com", "dep3"),
    ("Cristiano.Ronaldo@world.com", "dep3"),
    ("Cobalt.Chevrolet@world.com", "dep4"),
    ("Arman.Murza@world.com", "dep7"),
    ("Meepo.Mepar@world.com", "dep9"),
    ("Huskar.Huskarovich@world.com", "dep5");

insert into assignment2.doctor values
	("Amir.Umralin@world.com", "Junior"),
    ("Dulat.Ualiyev@world.com","Senior"),
    ("Umral.Kaliyev@world.com", "Professional"),
    ("Chan.Pen@world.com", "Senior"),
    ("Mune.Rude@world.com", "Senior"),
    ("Cristiano.Ronaldo@world.com", "Junior"),
    ("Cobalt.Chevrolet@world.com", "Professional"),
    ("Arman.Murza@world.com", "Junior"),
    ("Meepo.Mepar@world.com", "Professional"),
    ("Huskar.Huskarovich@world.com", "Senior"),
	("Newby.New@world.com", "Junior");


insert into assignment2.specialize values
	(1, "Amir.Umralin@world.com"), #3
    (6, "Amir.Umralin@world.com"), #3 virology
    (2, "Amir.Umralin@world.com"), #3
    (2, "Dulat.Ualiyev@world.com"), #1
    (3, "Umral.Kaliyev@world.com"), #2
    (6, "Umral.Kaliyev@world.com"), #2 virology
    (4, "Chan.Pen@world.com"), #1
    (5, "Mune.Rude@world.com"), #3
	(1, "Mune.Rude@world.com"), #3
	(2, "Mune.Rude@world.com"), #3
    (6, "Cristiano.Ronaldo@world.com"), #1 virology
    (7, "Cobalt.Chevrolet@world.com"), #1
    (8, "Arman.Murza@world.com"), #3
	(9, "Arman.Murza@world.com"), #3
    (10, "Arman.Murza@world.com"), #3
    (9, "Meepo.Mepar@world.com"), #1
    (10, "Huskar.Huskarovich@world.com"), #1
	(6, "Newby.New@world.com");

    
insert into assignment2.record values
	("Amir.Umralin@world.com", "China", "covid-19", 12, 9282), -- dep1
	("Amir.Umralin@world.com", "the USA", "covid-19", 11, 10900), -- dep1
	("Amir.Umralin@world.com", "Taiwan", "covid-19", 11, 190), -- dep1
	("Amir.Umralin@world.com", "United Kingdom", "covid-19", 1, 55), -- dep1
    ("Dulat.Ualiyev@world.com","Taiwan", "covid-19", 15, 175000), -- dep1
	("Dulat.Ualiyev@world.com","China", "covid-19", 11, 786555), -- dep1

    
    ("Umral.Kaliyev@world.com", "England", "blooding", 7, 1092),
    ("Chan.Pen@world.com", "the USA", "556", 8, 9822),
	("Chan.Pen@world.com", "Spain", "blooding", 1, 2222), 

    ("Mune.Rude@world.com", "United Kingdom", "877", 22, 456722),
	("Mune.Rude@world.com", "United Kingdom", "blooding", 22, 12000),

    ("Cristiano.Ronaldo@world.com", "Russia", "covid-19", 92, 120000), -- dep3
	("Cristiano.Ronaldo@world.com", "Spain", "covid-19", 9, 89), -- dep3

    ("Cobalt.Chevrolet@world.com", "Spain", "covid-19", 12000, 109222), -- dep4
	("Cobalt.Chevrolet@world.com", "Chile", "covid-19", 150, 104562), -- dep4
	("Cobalt.Chevrolet@world.com", "India", "covid-19", 140, 18262), -- dep4
	("Cobalt.Chevrolet@world.com", "Taiwan", "covid-19", 110, 1799), -- dep4


    ("Arman.Murza@world.com", "India", "562", 1292, 29999),
	("Arman.Murza@world.com", "Chile", "562", 1291, 2299),
    ("Meepo.Mepar@world.com", "Chile", "covid-19", 21, 15000), -- dep4
    ("Huskar.Huskarovich@world.com", "United Arab Emirates", "991", 25, 21000);
    
    
-- Queries start from here
-- #1.	List the disease code and the description of diseases that are caused by “bacteria” (pathogen) and were discovered before 1990.
-- select S.disease_code, S.description
-- from assignment2.disease S
-- inner join assignment2.discover D on S.disease_code = D.disease_code
-- where S.pathogen = "bacteria" and D.first_enc_date <= '1990-01-01';

-- #2.	List the name, surname and degree of doctors who are not specialized in “infectious diseases
-- select DISTINCT S.name, S.surname, D.degree
-- from assignment2.users S
-- inner join assignment2.doctor D on S.email = D.email
-- inner join assignment2.specialize F on F.email = D.email
-- where F.id != 7;

-- #3.	List the name, surname and degree of doctors who are specialized in more than 2 disease types
-- select S.name, S.surname, D.degree, count(*) as num_diseasetypes
-- from assignment2.users S
-- inner join assignment2.doctor D on S.email = D.email
-- inner join assignment2.specialize F on F.email = D.email
-- group by S.name, S.surname, D.degree
-- having num_diseasetypes > 2;

-- #4. For each country list the cname and average salary of doctors who are specialized in “virology"
-- select S.cname, avg(D.salary) as avg_salary
-- from assignment2.country S
-- inner join assignment2.users D on S.cname = D.cname
-- inner join assignment2.specialize F on D.email = F.email
-- where F.id = 6
-- group by S.cname;

-- #5.	List the departments of public servants who report “covid-19” cases in more than one country and 
-- #the number of such public servants who work in these departments. (i.e “Dept1 3” means that in 
-- #the “Dept1” department there are 3 such employees.)

-- select distinct S.department, count(distinct S.email) as pub_servants
-- from assignment2.publicservant S
-- inner join assignment2.record D on S.email = D.email 
-- where D.disease_code = "covid-19"
-- group by S.department
-- having count(distinct D.cname) > 1;

-- #6.	Double the salary of public servants who have recorded covid-19 patients more than 3 times

-- update assignment2.users S
-- set S.salary = S.salary * 2
-- where S.email in (select r.email from assignment2.record r where r.disease_code = "covid-19" group by r.email having count(*) > 3);

-- # 7.	Delete the users whose name contain the substring “bek” or “gul” (e.g. Alibek, Gulsim)-- 

-- delete from assignment2.users S
-- where S.name like '%bek%' or S.name like '%gul%';

-- #8.	Create an index namely “idx pathogen” on the “pathogen” field.

-- create index idx_pathogen on assignment2.disease(pathogen);

-- 9.	#List the email, name, and department of public servants who have created records where the 
-- number of patients is between 100000 and 999999

-- select distinct S.email, S.name, X.department
-- from assignment2.users S
-- inner join assignment2.record D on S.email = D.email
-- inner join assignment2.publicservant X on D.email = X.email
-- where D.total_patients between 100000 and 999999;


-- #10.	 List the top 5 counties with the highest number of total patients recorded.

-- select S.cname, sum(S.total_patients) as total_patients
-- from assignment2.record S
-- group by S.cname
-- order by total_patients desc
-- limit 5;

-- #11. Group the diseases by disease type and the total number of patients treated

-- select S.disease_code, sum(D.total_patients - D.total_deaths) as "patients_treated"
-- from assignment2.disease S
-- inner join assignment2.record D on S.disease_code = D.disease_code
-- group by D.disease_code users
