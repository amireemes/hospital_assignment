from enum import unique
from typing import Any

import uvicorn
from fastapi import FastAPI, Depends, Request, Form
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Date, ForeignKey, extract
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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


class UserScheme(BaseModel):
    email: str
    name: str
    surname: str
    salary: int
    phone: str
    cname: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: str | None
    surname: str | None
    salary: int | None
    phone: str | None
    cname: str | None

    class Config:
        orm_mode = True


class PublicServantScheme(BaseModel):
    email: str
    department: str

    class Config:
        orm_mode = True


class PublicServantUpdate(BaseModel):
    department: str | None

    class Config:
        orm_mode = True


class RecordScheme(BaseModel):
    email: str
    cname: str
    disease_code: str
    total_deaths: int
    total_patients: int

    class Config:
        orm_mode = True
        confirm_deleted_rows = False


class RecordUpdate(BaseModel):
    email: str | None
    cname: str | None
    disease_code: str | None
    total_deaths: int | None
    total_patients: int | None

    class Config:
        orm_mode = True


class DiseaseScheme(BaseModel):
    disease_code: str
    pathogen: str
    description: str

    class Config:
        orm_mode = True
        confirm_deleted_rows = False



class CRUDService:
    def create_user(self, data: UserScheme, db: Session) -> Users:
        obj_in_data = jsonable_encoder(data)
        db_obj = Users(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_users(self, db: Session) -> list[Users]:
        return db.query(Users).all()

    def get_user(self, email: str, db: Session) -> Users:
        return db.query(Users).filter(Users.email == email).first()

    def update_user(self, data_new: UserUpdate, data_old: Users, db: Session) -> Users:
        obj_data = jsonable_encoder(data_old)
        if isinstance(data_new, dict):
            update_data = data_new
        else:
            update_data = data_new.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(data_old, field, update_data[field])
        db.add(data_old)
        db.commit()
        db.refresh(data_old)
        return data_old

    def delete_user(self, email: str, db: Session) -> Users:
        obj = db.query(Users).get(email)
        db.delete(obj)
        db.commit()
        return obj

    def create_publicservant(self, data: PublicServantScheme, db: Session) -> PublicServant:
        obj_in_data = jsonable_encoder(data)
        db_obj = PublicServant(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_publicservants(self, db: Session) -> list[PublicServant]:
        return db.query(PublicServant).all()

    def get_publicservant(self, email: str, db: Session) -> Users:
        return db.query(PublicServant).filter(PublicServant.email == email).first()

    def update_publicservant(self, data_new: PublicServantUpdate, data_old: PublicServant,
                             db: Session) -> PublicServant:
        obj_data = jsonable_encoder(data_old)
        if isinstance(data_new, dict):
            update_data = data_new
        else:
            update_data = data_new.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(data_old, field, update_data[field])
        db.add(data_old)
        db.commit()
        db.refresh(data_old)
        return data_old

    def delete_publicservant(self, email: str, db: Session) -> PublicServant:
        obj = db.query(PublicServant).get(email)
        db.delete(obj)
        db.commit()
        return obj

    def list_records(self, db: Session) -> list[Record]:
        list1 = db.query(Record.email, Record.disease_code, Record.cname, Record.total_deaths, Record.total_patients).all()
        return list1

    def create_record(self, data: RecordScheme, db: Session) -> Record:
        obj_in_data = jsonable_encoder(data)
        db_obj = Record(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_record_email(self, email: str, db: Session) -> list[Record]:
        return db.query(Record).filter(Record.email == email).all()

    def get_record_diseasecode(self, disease_code: str, db: Session) -> list[Record]:
        return db.query(Record).filter(Record.disease_code == disease_code).all()

    def delete_record(self, email: str, db: Session) -> Record:
        obj = db.query(Record).get(email)
        db.delete(obj)
        db.commit()
        return obj

    def update_record(self, data_new: RecordUpdate, data_old: Record,
                      db: Session) -> Record:
        obj_data = jsonable_encoder(data_old)
        if isinstance(data_new, dict):
            update_data = data_new
        else:
            update_data = data_new.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(data_old, field, update_data[field])
        db.add(data_old)
        db.commit()
        db.refresh(data_old)
        return data_old

    def list_diseases(self, db: Session) -> [Record]:
        return db.query(Disease).all()

    def list_disease_types(self, db: Session) -> [Record]:
        return db.query(DiseaseType).all()

    def list_discoveries(self, db: Session) -> [Record]:
        return db.query(Discover).all()

    def list_countries(self, db: Session) -> [Country]:
        return db.query(Country).all()


crud = CRUDService()


@app.post("/user/post", response_model=UserScheme, tags=["User"])  # USER
def post_user(request: Request, email: str = Form(...), name: str = Form(...),
              surname: str = Form(), salary: int = Form(...), phone: str = Form(...), country: str = Form(...),
              db: Session = Depends(get_db)) -> Any:
    user_data = {
        "email": email,
        "name": name,
        "surname": surname,
        "salary": salary,
        "phone": phone,
        "cname": country
    }
    user = UserScheme(**user_data)
    crud.create_user(user, db)
    return RedirectResponse("http://127.0.0.1:8000/users/?message=create", status_code=status.HTTP_302_FOUND)


@app.get("/users", response_model=list[UserScheme], tags=["User"], response_class=HTMLResponse)  # USER
def list_user(request: Request, message: str | None = None, db: Session = Depends(get_db)) -> Any:
    if message == 'update':
        message = "Changes were made successfully"
    if message == 'create':
        message = "User was created"
    if message == 'delete':
        message = "User was deleted"

    return templates.TemplateResponse("all-users.html",
                                      {"request": request, "message": message, "users": crud.list_users(db), "countries": crud.list_countries(db)})


@app.get("/user/get_by_email", response_model=UserScheme, response_class=HTMLResponse, tags=["User"])  # USER
def get_user(email: str, db: Session = Depends(get_db)) -> Any:
    return crud.get_user(email, db)


@app.post("/user/update/{email}", response_model=UserUpdate, tags=["User"])  # USER
def update_user(request: Request, email: str, name: str = Form(...),
                surname: str = Form(...), salary: int = Form(...), phone: str = Form(...), country: str = Form(...),
                db: Session = Depends(get_db)) -> Any:
    item_in_db = crud.get_user(email, db)
    if not item_in_db:
        return {"message": "No such user"}
    updated_user_data = {
        "name": name,
        "surname": surname,
        "salary": salary,
        "phone": phone,
        "cname": country
    }
    new_data = UserUpdate(**updated_user_data)
    updated_user = crud.update_user(new_data, item_in_db, db)
    return RedirectResponse("http://127.0.0.1:8000/users/?message=update", status_code=status.HTTP_302_FOUND)


@app.get("/user/delete/{email}", response_model=UserScheme, tags=["User"])  # USER
def delete_user(email: str, db: Session = Depends(get_db)) -> Any:
    crud.delete_user(email, db)
    return RedirectResponse("http://127.0.0.1:8000/users/?message=delete", status_code=status.HTTP_302_FOUND)


@app.get("/records", response_model=list[RecordScheme], tags=["Record"])  # RECORDS
def all_records(request: Request, message: str | None = None, db: Session = Depends(get_db)) -> Any:
    # return crud.list_records(db)
    if message == 'create':
        message = "Record was created"
    if message == 'delete':
        message = "Record was deleted"

    return templates.TemplateResponse("all-records.html",
                                      {"request": request, "message": message, "records": crud.list_records(db)})


@app.post("/record/post", response_model=RecordScheme, tags=["Record"])
def post_record(request: Request, email: str = Form(...), country: str = Form(...),
                diseasecode: str = Form(), totaldeaths: int = Form(...), totalpatients: str = Form(...),
                db: Session = Depends(get_db)) -> Any:
    record_data = {
        "email": email,
        "cname": country,
        "disease_code": diseasecode,
        "total_deaths": totaldeaths,
        "total_patients": totalpatients
    }
    record = RecordScheme(**record_data)
    crud.create_record(record, db)
    return RedirectResponse("http://127.0.0.1:8000/records/?message=create", status_code=status.HTTP_302_FOUND)


@app.get("/record/delete/{email}", response_model=RecordScheme, tags=["Record"])  # USER
def delete_record(email: str, db: Session = Depends(get_db)) -> Any:
    crud.delete_record(email, db)
    return RedirectResponse("http://127.0.0.1:8000/records/?message=delete", status_code=status.HTTP_302_FOUND)


# @app.get("/user/delete/{email}", response_model=UserScheme, tags=["User"])  # USER
# def delete_user(email: str, db: Session = Depends(get_db)) -> Any:
#     crud.delete_user(email, db)
#     return RedirectResponse("http://127.0.0.1:8000/users/?message=delete", status_code=status.HTTP_302_FOUND)

@app.get("/record/{email}", response_model=RecordScheme, tags=["Record"])  # records
def get_records_by_email_error(email: str, db: Session = Depends(get_db)) -> Any:
    return crud.get_record_email(email, db)


@app.get("/record/{disease_code}", response_model=RecordScheme, tags=["Record"])  # records
def get_records_by_diseasecode_error(disease_code: str, db: Session = Depends(get_db)) -> Any:
    return crud.get_record_diseasecode(disease_code, db)


@app.put("/record/{email}", response_model=RecordScheme, tags=["Record"])  # PUBLICSERVANT
def update_record_error(email: str, data: RecordUpdate, db: Session = Depends(get_db)) -> Any:
    item_in_db = crud.get_record(email, db)
    if not item_in_db:
        return {"message": "No such record found"}
    updated_publicservant = crud.update_record(data, item_in_db, db)
    return updated_publicservant


@app.get("/publicservants", response_model=list[PublicServantScheme], tags=["Public Servant"])  # PUBLICSERVANT
def all_publicservants(request: Request, message: str | None = None, db: Session = Depends(get_db)) -> Any:
    #crud.list_publicservants(db)
    if message == 'update':
        message = "Changes were made successfully"
    if message == 'create':
        message = "Public Servant was created"
    if message == 'delete':
        message = "Public Servant was deleted"
    return templates.TemplateResponse("all-publicservants.html",
                                      {"request": request, "message": message, "publicservants": crud.list_publicservants(db)})


@app.post("/publicservant/post", response_model=PublicServantScheme, tags=["Public Servant"])
def create_publicservant(request: Request, email: str = Form(...), department: str = Form(...), db: Session = Depends(get_db)) -> Any:
    publicservant_data = {
        "email": email,
        "department": department
    }
    publicservant = PublicServantScheme(**publicservant_data)
    crud.create_publicservant(publicservant, db)
    return RedirectResponse("http://127.0.0.1:8000/publicservants/?message=create", status_code=status.HTTP_302_FOUND)


@app.post("/publicservant/update/{email}", response_model=PublicServantScheme, tags=["Public Servant"])  # PUBLICSERVANT
def update_publicservant(request: Request, email: str, department: str = Form(...), db: Session = Depends(get_db)) -> Any:
    item_in_db = crud.get_publicservant(email, db)
    if not item_in_db:
        return {"message": "No such public servant"}
    updated_public_servant = {
        "email": email,
        "department": department
    }
    updated_ps = PublicServantUpdate(**updated_public_servant)
    new_ps = crud.update_publicservant(updated_ps, item_in_db, db)
    return RedirectResponse("http://127.0.0.1:8000/publicservants/?message=update", status_code=status.HTTP_302_FOUND)

@app.get("/publicservant/delete/{email}", response_model=PublicServantScheme, tags=["Public Servant"])  # PUBLICSERVANT
def delete_publicservant(email: str, db: Session = Depends(get_db)) -> Any:
    crud.delete_publicservant(email, db)
    return RedirectResponse("http://127.0.0.1:8000/publicservants/?message=delete", status_code=status.HTTP_302_FOUND)


@app.get("/publicservant/{email}", response_model=PublicServantScheme, tags=["Public Servant"])  # PUBLICSERVANT
def get_publicservant(email: str, db: Session = Depends(get_db)) -> Any:
    return crud.get_publicservant(email, db)


@app.get("/diseases", response_model=list[DiseaseScheme], tags=["Disease"])  # USER
def all_diseases(request: Request, message: str | None = None, db: Session = Depends(get_db)) -> Any:

    return templates.TemplateResponse("all-diseases.html",
                                      {"request": request, "message": message, "diseases": crud.list_diseases(db), "disease_types": crud.list_disease_types(db), "discoveries": crud.list_discoveries(db)})





# @app.get("/first-query", tags=["Queries"])
# def get_first_query(db: Session = Depends(get_db)) -> Any:
#     # 1.	List the disease code and the description of diseases that are caused by “bacteria” (pathogen) and were
#     # discovered before 1990.
#     result = db.execute("select S.disease_code, S.description from assignment2.disease S inner join "
#                         "assignment2.discover D on S.disease_code = D.disease_code where S.pathogen = "
#                         "'bacteria' and D.first_enc_date <= '1990-01-01'")
#     output = []
#
#     for row in result:
#         disease = {
#             "disease_code": row['disease_code'],
#             "description": row['description']
#         }
#         output.append(disease)
#
#     return output


@app.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db)):
    # result = sqlalchemy_engine.execute("select S.disease_code, S.description from assignment2.disease S inner join "
    #                                    "assignment2.discover D on S.disease_code = D.disease_code where S.pathogen = "
    #                                    "'bacteria' and D.first_enc_date <= '1990-01-01'")
    #
    # print("\n\nQuery 1:")
    # for row in result:
    #     print("disease code: " + row["disease_code"] + ", description: " + row["description"])
    #
    # # 2.	List the name, surname and degree of doctors who are not specialized in “infectious diseases
    # result1 = sqlalchemy_engine.execute("select DISTINCT S.name, S.surname, D.degree "
    #                                     "from assignment2.users S "
    #                                     "inner join assignment2.doctor D on S.email = D.email "
    #                                     "inner join assignment2.specialize F on F.email = D.email "
    #                                     "where F.id != 7 ")
    #
    # print("\n\nQuery 2:")
    # for row in result1:
    #     print("Name: " + row["name"] + ", Surname: " + row["surname"], ", Degree: " + row["degree"])
    #
    # # 3.	List the name, surname and degree of doctors who are specialized in more than 2 disease types
    #
    # result2 = sqlalchemy_engine.execute("select S.name, S.surname, D.degree, count(*) as num_diseasetypes "
    #                                     "from assignment2.users S "
    #                                     "inner join assignment2.doctor D on S.email = D.email "
    #                                     "inner join assignment2.specialize F on F.email = D.email "
    #                                     "group by S.name, S.surname, D.degree "
    #                                     "having num_diseasetypes > 2 ")
    #
    # print("\n\nQuery 3:")
    # for row in result2:
    #     print("Name: " + row["name"] + ", Surname: " + row["surname"], ", Degree: " + row["degree"])
    #
    # # 4. For each country list the cname and average salary of doctors who are specialized in “virology"
    # result3 = sqlalchemy_engine.execute("select S.cname, avg(D.salary) as avg_salary "
    #                                     "from assignment2.country S "
    #                                     "inner join assignment2.users D on S.cname = D.cname "
    #                                     "inner join assignment2.specialize F on D.email = F.email "
    #                                     "where F.id = 6 "
    #                                     "group by S.cname ")
    #
    # print("\n\nQuery 4:")
    # for row in result3:
    #     print("Country name: " + row["cname"] + ", Average Salary: " + str(row["avg_salary"]))
    #
    # # 5.	List the departments of public servants who report “covid-19” cases in more than one country and
    # # the number of such public servants who work in these departments. (i.e “Dept1 3” means that in
    # # the “Dept1” department there are 3 such employees.)
    #
    # result4 = sqlalchemy_engine.execute("select distinct S.department, count(distinct S.email) as pub_servants "
    #                                     "from assignment2.publicservant S "
    #                                     "inner join assignment2.record D on S.email = D.email "
    #                                     "where D.disease_code = 'covid-19' "
    #                                     "group by S.department "
    #                                     "having count(distinct D.cname) > 1 ")
    #
    # print("\n\nQuery 5:")
    # for row in result4:
    #     print("Departments: " + row["department"] + ", Number of servants: " + str(row["pub_servants"]))
    #
    # # 6.	Double the salary of public servants who have recorded covid-19 patients more than 3 times
    #
    # result5 = sqlalchemy_engine.execute("update assignment2.users S "
    #                                     "set S.salary = S.salary * 2 "
    #                                     "where S.email in (select r.email from assignment2.record r where "
    #                                     "r.disease_code = 'covid-19' group by r.email "
    #                                     "having count(*) > 3 )")
    #
    # print("\n\nQuery 6:")
    # print("Changes successfully applied")
    #
    # # 7. Delete the users whose name contain the substring “bek” or “gul” (e.g.Alibek, Gulsim)
    #
    # result6 = sqlalchemy_engine.execute(
    #     "delete from assignment2.users S where S.name like '%%bek%%' or S.name like '%%gul%%' ")
    #
    # print("\n\nQuery 7:")
    # print("Changes successfully applied")
    #
    # # 8.	Create an index namely “idx pathogen” on the “pathogen” field.
    #
    # # result7 = sqlalchemy_engine.execute("create index idx_pathogen on assignment2.disease(pathogen)")
    #
    # print("\n\nQuery 8:")
    # print("Index successfully created")
    #
    # # 9. List the email, name, and department of public servants who have created records where the number of
    # # patients is between 100000 and 999999
    #
    # result8 = sqlalchemy_engine.execute("select distinct S.email, S.name, X.department "
    #                                     "from assignment2.users S "
    #                                     "inner join assignment2.record D on S.email = D.email "
    #                                     "inner join assignment2.publicservant X on D.email = X.email "
    #                                     "where D.total_patients between 100000 and 999999 ")
    #
    # print("\n\nQuery 9:")
    # for row in result8:
    #     print("Email: " + row["email"] + ", Name: " + row["name"] + ", Department: " + row["department"])
    #
    # # 10.	 List the top 5 counties with the highest number of total patients recorded.
    #
    # result9 = sqlalchemy_engine.execute("select S.cname, sum(S.total_patients) as total_patients "
    #                                     "from assignment2.record S "
    #                                     "group by S.cname "
    #                                     "order by total_patients desc "
    #                                     "limit 5;")
    # print("\n\nQuery 10:")
    # for row in result9:
    #     print("Country: " + row["cname"] + ", Total_patients: " + str(row["total_patients"]))
    #
    # # 11. Group the diseases by disease type and the total number of patients treated
    #
    # result10 = sqlalchemy_engine.execute(
    #     "select S.disease_code, sum(D.total_patients - D.total_deaths) as 'patients_treated' "
    #     "from assignment2.disease S "
    #     "inner join assignment2.record D on S.disease_code = D.disease_code "
    #     "group by D.disease_code ")
    #
    # print("\n\nQuery 11:")
    # for row in result10:
    #     print("Disease Type: " + row["disease_code"] + ", Patients treated: " + str(row["patients_treated"]))

    return templates.TemplateResponse("index.html", {"request": request, "users": crud.list_users(db)})
