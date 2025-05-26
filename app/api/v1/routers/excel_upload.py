from fastapi import UploadFile, File, HTTPException
import pandas as pd
from fastapi.responses import JSONResponse
from io import BytesIO
from datetime import datetime, date
import mysql.connector as conn
import yaml
from app.models.base import Organisation, Person, Questionare
from helper_fn import get_stakeholder_by_name,get_country_iso_by_name,get_organisation,add_organisation,get_person,add_person,bind_organisation_person
from helper_fn import process_company_perspective,process_company_stakeholder_perspective,process_stakeholder_perspective
from app.logging import logger

date_formats = ['%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d']

def read_config():
    try:
        with open("app/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return config["database"]
    except Exception as e:
        logger.error("Error reading config file: %s", e)
        raise FileNotFoundError("Error reading config file.")

def connect_to_database(username, host, database, port):
    try:
        password = read_config()["password"]

        engine = conn.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database
        )

        logger.info("Connected to the MySQL database successfully.")
        return engine
    except Exception as e:
        logger.error("Error connecting to the database: %s", e)
        raise ConnectionError("Error connecting to the database.")

def read_excel_data_from_bytes(data: bytes, sheet_index: int):
    try:
        with pd.ExcelFile(BytesIO(data)) as xls:
            num_sheets = len(xls.sheet_names)
            if 0 <= sheet_index < num_sheets:
                df = pd.read_excel(xls, sheet_name=xls.sheet_names[sheet_index], header=None)
                logger.info("Excel sheet %s read successfully.", sheet_index)
                return df
            else:
                raise ValueError(f"Sheet index {sheet_index} out of range. File has {num_sheets} sheets.")
    except Exception as e:
        logger.error("Error reading Excel file from bytes: %s", e)
        raise ValueError("Error reading Excel file from bytes.")


def parse_date(date_obj, formats):
   
    if isinstance(date_obj, date):
        return date_obj
    else:
        for fmt in formats:
            try:
                if isinstance(date_obj, str):
                    return datetime.strptime(date_obj, fmt).date()
            except ValueError:
                continue
    return None


def process_form_data(df, engine):

    try:
        lvbCustomerFlag = False
        lvsOrganisation = df.iloc[6, 4:6].str.cat(sep=" ")
        lvsRole = df.iloc[6, 10:11].str.cat(sep=" ")
        lviStakeholderId = get_stakeholder_by_name(lvsRole, engine)
        if lviStakeholderId == 2:
            lvbCustomerFlag = True
        lvsSalutation = df.iloc[9, 4] if not pd.isna(df.iloc[9, 4]) else None
        gender_str = df.iloc[10:12, 9:11].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        lvsGender = gender_str if not pd.isna(gender_str) else None
        lvsFirstname = df.iloc[11:13, 4:6].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        lvsLastname = df.iloc[11:13, 10:12].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        yearofbirth = df.iloc[13:15, 4:6].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        lvdYearofBirth = int(yearofbirth) if not pd.isna(yearofbirth) else 1700
        lvsStreet = df.iloc[17:19, 4:6].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        zip = df.iloc[19:21, 4:6].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        lvsZip = str(zip) if not pd.isna(zip) else None
        lvsCity = df.iloc[19:21, 10:12].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        lvsCountry = df.iloc[22:23, 4:6].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1).str.cat(sep=" ")
        lvsCountryIsoCode = get_country_iso_by_name(lvsCountry, engine)
        if lvsCountryIsoCode is None:
            lvsCountryIsoCode = "en"
        lvsPhone = df.iloc[24, 4:6].str.cat(sep=" ")
        lvsMobile = df.iloc[24, 10:12].str.cat(sep=" ")
        lvsMail = df.iloc[26, 4:6].str.cat(sep=" ")
        lvsComments = df.iloc[14, 13:14].str.cat(sep=" ")
        lvsCompanyFunction = df.iloc[8, 4:6].str.cat(sep=" ")
        lvsRelatedCompany = df.iloc[10, 14:15].str.cat(sep=" ")
        lvsQuestionaireDate = parse_date(df.iloc[5, 14], date_formats) if not pd.isna(df.iloc[5, 14]) else datetime.now().date()

        lvoPerson = Person(
            stakeholder_id=lviStakeholderId,
            person_salutation=lvsSalutation,
            person_firstname=lvsFirstname,
            person_lastname=lvsLastname,
            person_gender=lvsGender,
            person_phone=lvsPhone,
            person_mobile=lvsMobile,
            person_mail=lvsMail,
            person_birthday=lvdYearofBirth,
            person_street=lvsStreet,
            person_city=lvsCity,
            person_zip=lvsZip,
            person_country_iso=lvsCountryIsoCode,
            person_customer_flag=lvbCustomerFlag,
            person_comments=lvsComments,
            person_company_function=lvsCompanyFunction,
        )

        lvoOrganisation = Organisation(
            organisation_name=lvsOrganisation, organisation_country_iso=lvsCountryIsoCode
        )

        lvoRelatedOrganisation = Organisation(
            organisation_name=lvsRelatedCompany, organisation_country_iso=lvsCountryIsoCode
        )

        if lvsRelatedCompany is None or lvsRelatedCompany == '':
            lvsRelatedCompany = lvoOrganisation.organisation_name

        lvoOrganisation.organisation_id = get_organisation(lvoOrganisation, engine)
        if lvoOrganisation.organisation_id is None:
            lvoOrganisation.organisation_id = add_organisation(lvoOrganisation, engine)

        lvoRelatedOrganisation.organisation_id = get_organisation(lvoRelatedOrganisation, engine)
        if lvoRelatedOrganisation.organisation_id is None:
            lvoRelatedOrganisation.organisation_id = add_organisation(lvoRelatedOrganisation, engine)

        lvoQuestionare = Questionare(
            questionaire_comments=lvsComments,
            questionaire_date=lvsQuestionaireDate,
            questionaire_related_company=lvoRelatedOrganisation
        )

        lvoPerson.person_id = get_person(lvoPerson, engine)  
        if lvoPerson.person_id is None:
            lvoPerson.person_id = add_person(lvoPerson, engine)

        bind_organisation_person(lvoPerson, lvoOrganisation, engine)
        logger.info("Form data processed successfully.")
        return lvoPerson, lvoOrganisation, lvoQuestionare
    except Exception as e:
        logger.error("Error processing data: %s", e)
        return None, None, None


async def upload_excel(file: UploadFile = File(...)):
    """
    Upload an Excel file.
    :param file: UploadFile
    return: JSONResponse
    """
    try:
        data = await file.read()
        # data = open("tools/data/uploaded/Sascha Riedler.xlsx", "rb").read() #localtesting
        dfFormData = read_excel_data_from_bytes(data, 1)
    except Exception as e:
        logger.error("Error reading uploaded file: %s", e)
        raise HTTPException(status_code=400, detail="Invalid Excel file.")

    try:
        # Setup database connection
        db_config = read_config()
        engine = connect_to_database(
                username = db_config["username"],
                host = db_config["dsn"].split("/")[0].split(":")[0],
                database = db_config["dsn"].split("/")[1],
                port = db_config["dsn"].split("/")[0].split(":")[1]       
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    # Process form data
    print("Processing form data")
    lvoPerson, lvoOrganisation, lvoQuestionare = process_form_data(dfFormData, engine)

    if lvoPerson is None or lvoOrganisation is None:
        raise HTTPException(status_code=500, detail="Error processing form data.")

    try:
        if lvoPerson.stakeholder_id == 8:

            dfCompanyPerspectiveData = read_excel_data_from_bytes(data, 2)
            process_company_perspective(
                dfCompanyPerspectiveData, lvoPerson, lvoOrganisation, lvoQuestionare, engine
            )

            dfCompStakeholderPerspectiveData = read_excel_data_from_bytes(data, 3)
            process_company_stakeholder_perspective(
                dfCompStakeholderPerspectiveData, lvoPerson, lvoOrganisation, lvoQuestionare, engine
            )
        else:

            dfStakeholderPerspectiveData = read_excel_data_from_bytes(data, 2)
            process_stakeholder_perspective(
                dfStakeholderPerspectiveData, lvoPerson, lvoOrganisation, lvoQuestionare, engine
            )
    except Exception as e:
        logger.error("Error processing additional sheets: %s", e)
        raise HTTPException(status_code=500, detail="Error processing questionnaire data.")

    return JSONResponse(content={"message": "File processed successfully."})