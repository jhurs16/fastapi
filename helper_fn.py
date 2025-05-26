import logging
from os import path
from fastapi import HTTPException
import pandas as pd
import toml
from dotenv import load_dotenv
from app.models.base import Person, Organisation, Questionare
from app.db.database import get_database
from sqlalchemy import text


# Load environment variables
load_dotenv()

lcsBaseDir = path.abspath(path.dirname(__file__))
log_file = path.join(lcsBaseDir, "terramo_importer.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger()


date_formats = ['%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d']


def SQL_connection(query: str):
    """
    This function is used to connect to the database and fetch data from it.
    It accepts a query string as input and returns the result as a list of dictionaries.
    The function raises an HTTPException with status code 500

    """
    try:
        db = get_database()
        with db.get_connection() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
        data = [dict(row._mapping) for row in rows]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def sql_Database_engine():
    """
    This function is used to connect to the database and return the engine object.
    The function raises an HTTPException with status code 500

    """
    try:
        db = get_database()
        return db.get_engine()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




def read_config():
    """
    Reads database configuration from config.toml.
    """
    try:
        config = toml.load("config.toml")
        return config["database"]
    except Exception as e:
        logger.error("Error reading config file: %s", e)
        raise


def read_excel_data(file_name, sheet_index):
    """
    Reads an Excel file and returns a DataFrame.
    """
    try:
        # Open the Excel file
        with pd.ExcelFile(file_name) as xls:
            # Get the number of sheets in the Excel file
            num_sheets = len(xls.sheet_names)

            # Check if the specified sheet_index is valid
            if 0 <= sheet_index < num_sheets:
                # Read the sheet at the specified index
                df = pd.read_excel(
                    xls, sheet_name=xls.sheet_names[sheet_index], header=None
                )
                logger.info(f"Excel file {file_name} with tab {sheet_index} read successfully.")
                return df
            else:
                # Handle the case where the sheet index is out of range
                print(
                    f"Excel file {file_name} with sheet index {sheet_index} is out of range. The file has {num_sheets} sheets."
                )
                return None
    except Exception as e:
        logger.error("Error reading Excel file and/or defined worksheet: %s", e)





def get_person(ivoPerson: Person, engine) -> int:
    """
    Get personID by given person object using MySQL Connector
    """
    try:
        cursor = engine.cursor(dictionary=True)
        query = (
            "SELECT * FROM PERSONS WHERE PERSON_FIRSTNAME = %s "
            "AND PERSON_LASTNAME = %s AND PERSON_GENDER = %s"
        )
        cursor.execute(
            query,
            (
                ivoPerson.person_firstname,
                ivoPerson.person_lastname,
                ivoPerson.person_gender,
            ),
        )
        getData = cursor.fetchone()
        if getData is not None:
            return getData["PERSON_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise
    finally:
        cursor.close()


def bind_organisation_person(
    ivoPerson: Person, ivoOrganisation: Organisation, engine
) -> bool:
    """
    Binding persons and organisations
    """
    try:
        cursor = engine.cursor(dictionary=True)
        query = (
            "SELECT * FROM ORGANISATION_PERSONS WHERE "
            "ORGANISATION_ID = %s AND "
            "PERSON_ID = %s AND "
            "STAKEHOLDER_ID = %s AND "
            "ORGANISATION_PERSON_FUNCTION = %s"
        )
        cursor.execute(
            query,
            (
                ivoOrganisation.organisation_id,
                ivoPerson.person_id,
                ivoPerson.stakeholder_id,
                ivoPerson.person_company_function,
            ),
        )
        getData = cursor.fetchone()
        if getData is None:
            query = (
                "INSERT INTO ORGANISATION_PERSONS "
                "(STAKEHOLDER_ID, ORGANISATION_ID, PERSON_ID, "
                "ORGANISATION_PERSON_FUNCTION, ORGANISATION_PERSON_CREATED_BY) VALUES "
                "(%s, %s, %s, %s, 1)"
            )
            cursor.execute(
                query,
                (
                    ivoPerson.stakeholder_id,
                    ivoOrganisation.organisation_id,
                    ivoPerson.person_id,
                    ivoPerson.person_company_function,
                ),
            )
            engine.commit()
            logger.info("Relationship between person and organisation added.")
            return True
        else:
            return False
    except Exception as e:
        logger.error("Error processing data: %s", e)
        engine.rollback()
        raise
    finally:
        cursor.close()


def add_person(ivoPerson: Person, engine) -> int:
    """
    Add new person an return id
    """
    try:
        cursor = engine.cursor(dictionary=True)
        query = (
            "INSERT INTO PERSONS "
            "(STAKEHOLDER_ID, PERSON_SALUTATION, PERSON_FIRSTNAME, "
            "PERSON_LASTNAME, PERSON_GENDER, PERSON_PHONE, PERSON_MOBILE, "
            "PERSON_MAIL, PERSON_BIRTHDAY, PERSON_STREET, PERSON_ZIP, PERSON_STATE, "
            "PERSON_CITY, PERSON_COUNTRY_ISO, PERSON_CUSTOMER_FLAG, PERSON_COMMENTS, PERSON_CREATED_BY) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)"
        )
        values = (
            ivoPerson.stakeholder_id,
            ivoPerson.person_salutation,
            ivoPerson.person_firstname,
            ivoPerson.person_lastname,
            ivoPerson.person_gender,
            ivoPerson.person_phone,
            ivoPerson.person_mobile,
            ivoPerson.person_mail,
            ivoPerson.person_birthday,
            ivoPerson.person_street,
            ivoPerson.person_zip,
            ivoPerson.person_state,
            ivoPerson.person_city,
            ivoPerson.person_country_iso,
            ivoPerson.person_customer_flag,
            ivoPerson.person_comments,
        )
        cursor.execute(query, values)
        engine.commit()
        logger.info(f"person {ivoPerson.person_firstname} {ivoPerson.person_lastname} added.")
        return cursor.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        engine.rollback()
        raise
    finally:
        cursor.close()


def get_organisation(ivoOrganisation: Organisation, engine) -> int:
    """
    Get organisationID by given company object
    """
    try:
        cursor = engine.cursor(dictionary=True)
        query = "SELECT * FROM ORGANISATIONS WHERE ORGANISATION_NAME = %s"
        cursor.execute(query, (ivoOrganisation.organisation_name,))
        getData = cursor.fetchone()
        if getData is not None:
            return getData["ORGANISATION_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()


def add_organisation(ivoOrganisation: Organisation, engine) -> int:
    """
    Add new organisation an return id
    """
    try:
        cursor = engine.cursor()
        lvsSQL = (
            "INSERT INTO ORGANISATIONS "
            "(ORGANISATION_NAME, ORGANISATION_COUNTRY_ISO, ORGANISATION_CREATED_BY) "
            "VALUES (%s, %s, 1)"
        )
        cursor.execute(
            lvsSQL,
            (
                ivoOrganisation.organisation_name,
                ivoOrganisation.organisation_country_iso,
            ),
        )
        engine.commit()
        logger.info(f"organisation {ivoOrganisation.organisation_name} added.")
        return cursor.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        engine.rollback()
        raise
    finally:
        cursor.close()


def get_country_iso_by_name(ivsCountry: str, engine) -> str:
    """
    Get country ISO code
    """
    try:
        cursor = engine.cursor(dictionary=True)
        query = "SELECT * FROM COUNTRIES WHERE COUNTRY_NAME = %s"
        cursor.execute(query, (ivsCountry,))
        getData = cursor.fetchone()
        if getData is not None:
            return getData["COUNTRY_ISO_CODE"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()


def get_stakeholder_by_name(ivsRoleName: str, engine) -> int:

    """
    Get stakeholder ID by name
    """
    try:
        cursor = engine.cursor(dictionary=True)
        query = "SELECT * FROM STAKEHOLDER_NAMES WHERE STAKEHOLDER_NAME = %s"
        cursor.execute(query, (ivsRoleName,))
        getData = cursor.fetchone()

        if getData is not None:
            return getData["STAKEHOLDER_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise
    finally:
        if cursor:
            cursor.close()


def create_questionaire(
    ivsType: str,
    ivoPerson: Person,
    ivoOrganisation: Organisation,
    ivoQuestionare: Questionare,
    engine,
) -> int:
    """
    Add new questionaire ID and return id
    """

    lvnRelatedOrganisationId = None
    if ivoQuestionare.questionaire_related_company is not None:
        lvnRelatedOrganisationId = ivoQuestionare.questionaire_related_company.organisation_id
    try:
        cursor = engine.cursor(dictionary=True)
        query = (
            "INSERT INTO ESG_QUESTIONAIRES "
            "(QUESTIONAIRE_TYPE, PERSON_ID, ORGANISATION_ID, RELATED_ORGANISATION_ID, "
            "QUESTIONAIRE_COMMENT, QUESTIONAIRE_DATE, ESG_QUESTIONAIRE_ANSWER_CREATED_BY) "
            "VALUES (%s, %s, %s, %s, %s, %s, 1)"
        )
        values = (
            ivsType,
            ivoPerson.person_id,
            ivoOrganisation.organisation_id,
            lvnRelatedOrganisationId,
            ivoQuestionare.questionaire_comments,
            ivoQuestionare.questionaire_date,
        )
        cursor.execute(query, values)
        engine.commit()
        logger.info(f"questionaire {cursor.lastrowid} added.")
        return cursor.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        engine.rollback()
        raise


def add_company_measure_by_name(
    ivnMeasureID: int,
    ivsCountryIsoCode: str,
    ivnStakeholderID: int,
    ivnQuestionaireID: int,
    priority: int,
    status: int,
    comments: str,
    engine,
) -> bool:
    """
    Add measure response
    """

    try:
        cursor = engine.cursor(dictionary=True)
        query = (
            "INSERT INTO ESG_QUESTIONAIRE_ANSWERS "
            "(ESG_QUESTIONAIRE_ID, ESG_MEASURE_ID, STAKEHOLDER_ID, "
            "ESG_QUESTIONAIRE_ANSWER_PRIORITY, ESG_QUESTIONAIRE_ANSWER_STATUS, "
            "ESG_QUESTIONAIRE_ANSWER_COMMENTS, ESG_QUESTIONAIRE_ANSWER_COUNTRY_ISO, "
            "ESG_QUESTIONAIRE_ANSWER_CREATED_BY) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, 1)"
        )
        values = (
            ivnQuestionaireID,
            ivnMeasureID,
            ivnStakeholderID,
            priority,
            status,
            comments,
            ivsCountryIsoCode,
        )
        cursor.execute(query, values)
        engine.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        engine.rollback()
        raise



def get_measure_by_name(ivoRow, engine) -> int:
    """
    Get measure ID by name
    """
    try:
        cursor = engine.cursor(dictionary=True, buffered=True)
        sql = (
            "SELECT EM.ESG_MEASURE_ID FROM ESG_MEASURES EM "
            "INNER JOIN ESG_MEASURE_DESCRIPTIONS EMD ON EM.ESG_MEASURE_ID = EMD.ESG_MEASURE_ID "
            "WHERE ESG_MEASURE_KEY = %s AND EMD.ESG_MEASURE_DESCRIPTION_TOPIC = 0"
        )
        measure = ivoRow[0] if not pd.isna(ivoRow[0]) else None
        cursor.execute(sql, (measure,))
        getData = cursor.fetchone()
        if getData is not None:
            return getData["ESG_MEASURE_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise
    finally:
        cursor.close()


def process_company_perspective(
    df,
    lvoPerson: Person,
    lvoOrganisation: Organisation,
    lvoQuestionare: Questionare,
    engine,
):
    """
    Add questionaire data from company perspective sheet
    """
    # Add questionaire base data

    questionaireID = create_questionaire(
        "company_perspective", lvoPerson, lvoOrganisation, lvoQuestionare, engine
    )

    for index, row in df.iterrows():
        if index >= 7 and not pd.isna(row[0]):
            # Analyse answers and add them
            measureID = get_measure_by_name(row, engine)
            if measureID is not None:
                priority = row[3] if not pd.isna(row[3]) else 0
                status = row[5] if not pd.isna(row[5]) else 0
                comments = row[7] if not pd.isna(row[7]) else None
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    lvoPerson.stakeholder_id,
                    questionaireID,
                    priority,
                    status,
                    comments,
                    engine,
                )


def process_company_stakeholder_perspective(
    df,
    lvoPerson: Person,
    lvoOrganisation: Organisation,
    lvoQuestionare: Questionare,
    engine,
):

    """
    Add questionaire data from company stakeholder perspective sheet
    """
    # Add questionaire base data

    questionaireID = create_questionaire(
        "internal_stakeholder_view", lvoPerson, lvoOrganisation, lvoQuestionare, engine
    )
    for index, row in df.iterrows():
        if index >= 7 and not pd.isna(row[0]):
            # Analyse answers and add them
            measureID = get_measure_by_name(row, engine)
            if measureID is not None:
                # Employees
                priority = row[3] if not pd.isna(row[3]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    1,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )
                # Clients
                priority = row[5] if not pd.isna(row[5]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    2,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )
                # Suppliers
                priority = row[7] if 7 in row and not pd.isna(row[7]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    3,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )
                # Industry Rep.
                # old logic priority = row[9] if not pd.isna(row[9]) else 0
                priority = row[9] if 9 in row and not pd.isna(row[9]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    4,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )
                # Society
                priority = row[11] if 11 in row and not pd.isna(row[11]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    5,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )
                # Banks / Investors
                priority = row[13] if 13 in row and not pd.isna(row[13]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    6,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )
                # Regulation
                priority = row[15] if 15 in row and not pd.isna(row[15]) else 0
                status = 0
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    7,
                    questionaireID,
                    priority,
                    status,
                    None,
                    engine,
                )


def process_stakeholder_perspective(
    df,
    lvoPerson: Person,
    lvoOrganisation: Organisation,
    lvoQuestionare: Questionare,
    engine,
):

    """
    Add questionaire data from stakeholder perspective sheet
    """
    # Add questionaire base data

    questionaireID = create_questionaire(
        "stakeholder_perspective", lvoPerson, lvoOrganisation, lvoQuestionare, engine
    )

    for index, row in df.iterrows():
        if index >= 7 and not pd.isna(row[0]):
            # Analyse answers and add them
            measureID = get_measure_by_name(row, engine)
            if measureID is not None:
                priority = row[3] if not pd.isna(row[3]) else 0
                status = 0
                comments = None
                add_company_measure_by_name(
                    measureID,
                    lvoPerson.person_country_iso,
                    lvoPerson.stakeholder_id,
                    questionaireID,
                    priority,
                    status,
                    comments,
                    engine,
                )




