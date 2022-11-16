import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Date, ForeignKey, extract
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.orm import Session

app = FastAPI()


# Database connection
my_database_url = "mysql+pymysql://root:Amir.Ergaliev2@localhost:3306/assignment2"
sqlalchemy_engine = create_engine(my_database_url, isolation_level="READ COMMITTED")
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=sqlalchemy_engine)
Base = declarative_base()


# We need to have an independent database session/connection (SessionLocal) per
# request, use the same session through all the request and
# then close it after the request is finished.
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


class Country(Base):
    __tablename__ = "country"
    cname = Column(String, primary_key=True, index=True)
    population = Column(Integer)

    country_discovers = relationship("Discover", back_populates="country")
    records = relationship("Record", back_populates="country")
    users = relationship("Users", back_populates="country")


class Discover(Base):
    __tablename__ = "discover"
    cname = Column(String, ForeignKey("country.cname"), primary_key=True)
    disease_code = Column(String, ForeignKey("disease.disease_code"), primary_key=True)
    first_enc_date = Column(Date)

    country = relationship("Country", back_populates="country_discovers")
    disease = relationship("Disease", back_populates="disease_discovers")


class Disease(Base):
    __tablename__ = "disease"
    disease_code = Column(String, primary_key=True, index=True)
    pathogen = Column(String)
    description = Column(String)
    id = Column(Integer, ForeignKey("diseasetype.id"))

    disease_discovers = relationship("Discover", back_populates="disease")
    disease_type = relationship("DiseaseType", back_populates="diseases")
    records = relationship("Record", back_populates="disease")


class DiseaseType(Base):
    __tablename__ = "diseasetype"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)

    diseases = relationship("Disease", back_populates="disease_type")
    specializes = relationship("Specialize", back_populates="disease_type")


class Doctor(Base):
    __tablename__ = "doctor"
    email = Column(String, ForeignKey("users.email"), primary_key=True)
    degree = Column(String)

    user = relationship("Users", back_populates="doctor")


class PublicServant(Base):
    __tablename__ = "publicservant"
    email = Column(String, ForeignKey("users.email"), primary_key=True)
    department = Column(String)

    user = relationship("Users", back_populates="public_servant")


class Record(Base):
    __tablename__ = "record"
    email = Column(String, ForeignKey("users.email"), primary_key=True)
    cname = Column(String, ForeignKey("country.cname"))
    disease_code = Column(String, ForeignKey("disease.disease_code"))
    total_deaths = Column(Integer)
    total_patients = Column(Integer)

    user = relationship("Users", back_populates="records")
    country = relationship("Country", back_populates="records")
    disease = relationship("Disease", back_populates="records")


class Specialize(Base):
    __tablename__ = "specialize"
    id = Column(Integer, ForeignKey("diseasetype.id"), primary_key=True)
    email = Column(String, ForeignKey("users.email"))

    disease_type = relationship("DiseaseType", back_populates="specializes")
    user = relationship("Users", back_populates="specializes")


class Users(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    name = Column(String)
    surname = Column(String)
    salary = Column(Integer)
    phone = Column(String)
    cname = Column(String, ForeignKey("country.cname"))

    doctor = relationship("Doctor", back_populates="user")
    public_servant = relationship("PublicServant", back_populates="user")
    records = relationship("Record", back_populates="user")
    specializes = relationship("Specialize", back_populates="user")
    country = relationship("Country", back_populates="users")

@app.get("/")
def root(db: Session = Depends(get_db)):

    # 1.	List the disease code and the description of diseases that are caused by “bacteria” (pathogen) and were discovered before 1990.
    result = sqlalchemy_engine.execute("select S.disease_code, S.description from assignment2.disease S inner join "
                                       "assignment2.discover D on S.disease_code = D.disease_code where S.pathogen = "
                                       "'bacteria' and D.first_enc_date <= '1990-01-01'")

    print("\n\nQuery 1:")
    for row in result:
        print("disease code: " + row["disease_code"] + ", description: " + row["description"])

    # 2.	List the name, surname and degree of doctors who are not specialized in “infectious diseases
    result1 = sqlalchemy_engine.execute("select DISTINCT S.name, S.surname, D.degree "
                                        "from assignment2.users S "
                                        "inner join assignment2.doctor D on S.email = D.email "
                                        "inner join assignment2.specialize F on F.email = D.email "
                                        "where F.id != 7 ")

    print("\n\nQuery 2:")
    for row in result1:
        print("Name: " + row["name"] + ", Surname: " + row["surname"], ", Degree: " + row["degree"])

    # 3.	List the name, surname and degree of doctors who are specialized in more than 2 disease types

    result2 = sqlalchemy_engine.execute("select S.name, S.surname, D.degree, count(*) as num_diseasetypes "
                                        "from assignment2.users S "
                                        "inner join assignment2.doctor D on S.email = D.email "
                                        "inner join assignment2.specialize F on F.email = D.email "
                                        "group by S.name, S.surname, D.degree "
                                        "having num_diseasetypes > 2 ")

    print("\n\nQuery 3:")
    for row in result2:
        print("Name: " + row["name"] + ", Surname: " + row["surname"], ", Degree: " + row["degree"])

    # 4. For each country list the cname and average salary of doctors who are specialized in “virology"
    result3 = sqlalchemy_engine.execute ("select S.cname, avg(D.salary) as avg_salary "
                                        "from assignment2.country S "
                                        "inner join assignment2.users D on S.cname = D.cname "
                                        "inner join assignment2.specialize F on D.email = F.email "
                                        "where F.id = 6 "
                                        "group by S.cname ")

    print("\n\nQuery 4:")
    for row in result3:
        print("Country name: " + row["cname"] + ", Average Salary: " + str(row["avg_salary"]))

    # 5.	List the departments of public servants who report “covid-19” cases in more than one country and
    # the number of such public servants who work in these departments. (i.e “Dept1 3” means that in
    # the “Dept1” department there are 3 such employees.)

    result4 = sqlalchemy_engine.execute("select distinct S.department, count(distinct S.email) as pub_servants "
                                        "from assignment2.publicservant S "
                                        "inner join assignment2.record D on S.email = D.email "
                                        "where D.disease_code = 'covid-19' "
                                        "group by S.department "
                                        "having count(distinct D.cname) > 1 ")

    print("\n\nQuery 5:")
    for row in result4:
        print("Departments: " + row["department"] + ", Number of servants: " + str(row["pub_servants"]))


    # 6.	Double the salary of public servants who have recorded covid-19 patients more than 3 times

    result5 = sqlalchemy_engine.execute("update assignment2.users S "
                                        "set S.salary = S.salary * 2 "
                                        "where S.email in (select r.email from assignment2.record r where "
                                        "r.disease_code = 'covid-19' group by r.email "
                                        "having count(*) > 3 )")

    print("\n\nQuery 6:")
    print("Changes successfully applied")

    #7. Delete the users whose name contain the substring “bek” or “gul” (e.g.Alibek, Gulsim)

    result6 = sqlalchemy_engine.execute("delete from assignment2.users S where S.name like '%%bek%%' or S.name like '%%gul%%' ")

    print("\n\nQuery 7:")
    print("Changes successfully applied")

    # 8.	Create an index namely “idx pathogen” on the “pathogen” field.

    # result7 = sqlalchemy_engine.execute("create index idx_pathogen on assignment2.disease(pathogen)")

    print("\n\nQuery 8:")
    print("Changes successfully applied")

    # 9. List the email, name, and department of public servants who have created records where the number of
    # patients is between 100000 and 999999

    result8 = sqlalchemy_engine.execute("select distinct S.email, S.name, X.department "
                                        "from assignment2.users S "
                                        "inner join assignment2.record D on S.email = D.email "
                                        "inner join assignment2.publicservant X on D.email = X.email "
                                        "where D.total_patients between 100000 and 999999 ")


    print("\n\nQuery 9:")
    for row in result8:
        print("Email: " + row["email"] + ", Name: " + row["name"] + ", Department: " + row["department"])

    # 10.	 List the top 5 counties with the highest number of total patients recorded.

    result9 = sqlalchemy_engine.execute("select S.cname, sum(S.total_patients) as total_patients "
                                        "from assignment2.record S "
                                        "group by S.cname "
                                        "order by total_patients desc "
                                        "limit 5;")
    print("\n\nQuery 10:")
    for row in result9:
        print("Country: " + row["cname"] + ", Total_patients: " + str(row["total_patients"]))

    # 11. Group the diseases by disease type and the total number of patients treated

    result10 = sqlalchemy_engine.execute("select S.disease_code, sum(D.total_patients - D.total_deaths) as 'patients_treated' "
                                        "from assignment2.disease S "
                                        "inner join assignment2.record D on S.disease_code = D.disease_code "
                                        "group by D.disease_code ")

    print("\n\nQuery 11:")
    for row in result10:
        print("Disease Type: " + row["disease_code"] + ", Patients treated: " + str(row["patients_treated"]))