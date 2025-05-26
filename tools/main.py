import logging
import os
from os import path
from datetime import datetime, date
import pandas as pd
import toml
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from models.base import Organisation, Person, Questionare

# Load environment variables
load_dotenv()

lcsBaseDir = path.abspath(path.dirname(__file__))
log_file = path.join(lcsBaseDir, "terramo_importer.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger()


date_formats = ['%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d']

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


def connect_to_database(username, host, database, port):
    """
    Establishes a connection to the MySQL database.
    """
    try:
        password = os.getenv("DB_PASSWORD")
        #mysql+pymysql://root:D34dC4lm@127.0.0.1:3306/terramo_data
        #f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(
            f"mysql+mysqldb://{username}:{password}@{host}:{port}/{database}"
        )
        logger.info("Connected to the MySQL database successfully.")
        return engine
    except Exception as e:
        logger.error("Error connecting to the database: %s", e)
        raise


def get_person(ivoPerson: Person, engine) -> int:
    """
    Get personID by given person object
    """
    try:
        with engine.connect() as connection:
            lvsSQL = text(
                "SELECT * FROM PERSONS WHERE PERSON_FIRSTNAME = "
                ":firstname AND PERSON_LASTNAME = :lastname "
                "AND PERSON_GENDER = :gender"
            )
            getData = connection.execute(
                lvsSQL,
                {
                    "firstname": ivoPerson.person_firstname,
                    "lastname": ivoPerson.person_lastname,
                    "gender": ivoPerson.person_gender,
                },
            ).fetchone()
            if getData is not None:
                dataDict = getData._asdict()
                return dataDict["PERSON_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise


def bind_organisation_person(
    ivoPerson: Person, ivoOrganisation: Organisation, engine
) -> bool:
    """
    Binding persons and organisations
    """
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            lvsSQL = text(
                "SELECT * FROM ORGANISATION_PERSONS WHERE "
                "ORGANISATION_ID = :organisation AND "
                "PERSON_ID = :person AND "
                "STAKEHOLDER_ID = :stakeholder AND "
                "ORGANISATION_PERSON_FUNCTION = :function"
            )
            getData = connection.execute(
                lvsSQL,
                {
                    "organisation": ivoOrganisation.organisation_id,
                    "person": ivoPerson.person_id,
                    "stakeholder": ivoPerson.stakeholder_id,
                    "function":ivoPerson.person_company_function,
                },
            ).fetchone()
            if getData is None:
                lvsSQL = text(
                    "INSERT INTO ORGANISATION_PERSONS "
                    "(STAKEHOLDER_ID, ORGANISATION_ID, PERSON_ID, "
                    "ORGANISATION_PERSON_FUNCTION, ORGANISATION_PERSON_CREATED_BY) VALUES "
                    "(:stakeholder, :organisation, :person, :function, 1)"
                )
                getData = connection.execute(
                    lvsSQL,
                    {
                        "stakeholder": ivoPerson.stakeholder_id,
                        "organisation": ivoOrganisation.organisation_id,
                        "person": ivoPerson.person_id,
                        "function":ivoPerson.person_company_function,
                    },
                )
                if getData is not None:
                    trans.commit()
                    logger.info("relationsship between person and organisation added.")
                return True
            else:
                return False
    except Exception as e:
        logger.error("Error processing data: %s", e)
        trans.rollback()
        raise


def add_person(ivoPerson: Person, engine) -> int:
    """
    Add new person an return id
    """
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            lvsSQL = text(
                "INSERT INTO PERSONS "
                "(STAKEHOLDER_ID, PERSON_SALUTATION, PERSON_FIRSTNAME,"
                "PERSON_LASTNAME, PERSON_GENDER, PERSON_PHONE, PERSON_MOBILE, "
                "PERSON_MAIL, PERSON_BIRTHDAY, PERSON_STREET, PERSON_ZIP, PERSON_STATE,"
                "PERSON_CITY, PERSON_COUNTRY_ISO, PERSON_CUSTOMER_FLAG, PERSON_COMMENTS, PERSON_CREATED_BY)"
                " VALUES (:stakeholder, :salutation, :firstname, :lastname,"
                ":gender, :phone, :mobile, :mail, :birthday, :street, :zip, :state, :city,"
                ":country, :customer, :comments, 1)"
            )
            getData = connection.execute(
                lvsSQL,
                {
                    "stakeholder": ivoPerson.stakeholder_id,
                    "salutation": ivoPerson.person_salutation,
                    "firstname": ivoPerson.person_firstname,
                    "lastname": ivoPerson.person_lastname,
                    "mail": ivoPerson.person_mail,
                    "phone": ivoPerson.person_phone,
                    "mobile": ivoPerson.person_mobile,
                    "gender": ivoPerson.person_gender,
                    "birthday": ivoPerson.person_birthday,
                    "street": ivoPerson.person_street,
                    "zip": ivoPerson.person_zip,
                    "state": ivoPerson.person_state,
                    "city": ivoPerson.person_city,
                    "country": ivoPerson.person_country_iso,
                    "customer": ivoPerson.person_customer_flag,
                    "comments": ivoPerson.person_comments,
                },
            )
            if getData is not None:
                trans.commit()
                logger.info(f"person {ivoPerson.person_firstname} {ivoPerson.person_lastname} added.")
                return getData.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        trans.rollback()
        raise


def get_organisation(ivoOrganisation: Organisation, engine) -> int:
    """
    Get organisationID by given company object
    """
    try:
        with engine.connect() as connection:
            lvsSQL = text(
                "SELECT * FROM ORGANISATIONS WHERE ORGANISATION_NAME = :organisation"
            )
            getData = connection.execute(
                lvsSQL,
                {"organisation": ivoOrganisation.organisation_name},
            ).fetchone()
            if getData is not None:
                dataDict = getData._asdict()
                return dataDict["ORGANISATION_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise


def add_organisation(ivoOrganisation: Organisation, engine) -> int:
    """
    Add new organisation an return id
    """
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            lvsSQL = text(
                "INSERT INTO ORGANISATIONS "
                "(ORGANISATION_NAME, ORGANISATION_COUNTRY_ISO, "
                "ORGANISATION_CREATED_BY) VALUES (:name,:iso,1)"
            )
            getData = connection.execute(
                lvsSQL,
                {
                    "name": ivoOrganisation.organisation_name,
                    "iso": ivoOrganisation.organisation_country_iso,
                },
            )
            if getData is not None:
                trans.commit()
                logger.info(f"organisation {ivoOrganisation.organisation_name} added.")
                return getData.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        trans.rollback()
        raise


def get_country_iso_by_name(ivsCountry: str, engine) -> str:
    """
    Get country ISO code
    """
    try:
        with engine.connect() as connection:
            lvsSQL = text("SELECT * FROM COUNTRIES WHERE COUNTRY_NAME = :country")
            getData = connection.execute(
                lvsSQL,
                {"country": ivsCountry},
            ).fetchone()
            if getData is not None:
                dataDict = getData._asdict()
                return dataDict["COUNTRY_ISO_CODE"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise


def get_stakeholder_by_name(ivsRoleName: str, engine) -> int:
    """
    Get stakeholder ID by name
    """
    try:
        with engine.connect() as connection:
            lvsSQL = text(
                "SELECT * FROM STAKEHOLDER_NAMES WHERE STAKEHOLDER_NAME = :stakeholder"
            )
            getData = connection.execute(
                lvsSQL,
                {"stakeholder": ivsRoleName},
            ).fetchone()
            if getData is not None:
                dataDict = getData._asdict()
                return dataDict["STAKEHOLDER_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise


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
        with engine.connect() as connection:
            trans = connection.begin()
            lvsSQL = text(
                "INSERT INTO ESG_QUESTIONAIRES "
                "(QUESTIONAIRE_TYPE, PERSON_ID, ORGANISATION_ID, RELATED_ORGANISATION_ID, "
                "QUESTIONAIRE_COMMENT ,QUESTIONAIRE_DATE,ESG_QUESTIONAIRE_ANSWER_CREATED_BY) "
                "VALUES (:type,:person,:organisation,:related_organisation,:comment,:date,1)"
            )
            getData = connection.execute(
                lvsSQL,
                {
                    "type": ivsType,
                    "person": ivoPerson.person_id,
                    "organisation": ivoOrganisation.organisation_id,
                    "related_organisation": lvnRelatedOrganisationId,
                    "comment": ivoQuestionare.questionaire_comments,
                    "date": ivoQuestionare.questionaire_date,
                },
            )
            if getData is not None:
                trans.commit()
                logger.info(f"questionaire {getData.lastrowid} added.")
                return getData.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        trans.rollback()
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
        with engine.connect() as connection:
            trans = connection.begin()
            lvsSQL = text(
                "INSERT INTO ESG_QUESTIONAIRE_ANSWERS (ESG_QUESTIONAIRE_ID, ESG_MEASURE_ID, STAKEHOLDER_ID,"
                "ESG_QUESTIONAIRE_ANSWER_PRIORITY, ESG_QUESTIONAIRE_ANSWER_STATUS,"
                "ESG_QUESTIONAIRE_ANSWER_COMMENTS, ESG_QUESTIONAIRE_ANSWER_COUNTRY_ISO,"
                "ESG_QUESTIONAIRE_ANSWER_CREATED_BY) VALUES (:questionaire_id, :measure, :stakeholder, "
                ":priority, :status, :comments, :language, 1)"
            )

            addData = connection.execute(
                lvsSQL,
                {
                    "questionaire_id": ivnQuestionaireID,
                    "measure": ivnMeasureID,
                    "stakeholder": ivnStakeholderID,
                    "priority": priority,
                    "status": status,
                    "comments": comments,
                    "language": ivsCountryIsoCode,
                },
            )
            if addData is not None:
                trans.commit()
                return addData.lastrowid
    except Exception as e:
        logger.error("Error processing data: %s", e)
        trans.rollback()
        raise


def get_measure_by_name(ivoRow, engine) -> int:
    """
    Get measure ID by name
    """
    try:
        with engine.connect() as connection:
            lvsSQL = text(
                "SELECT * FROM ESG_MEASURES EM INNER JOIN ESG_MEASURE_DESCRIPTIONS EMD "
                "ON EM.ESG_MEASURE_ID=EMD.ESG_MEASURE_ID WHERE ESG_MEASURE_KEY "
                "= :measure AND EMD.ESG_MEASURE_DESCRIPTION_TOPIC=0"
            )
            measure = ivoRow[0] if not pd.isna(ivoRow[0]) else None
            getData = connection.execute(
                lvsSQL,
                {"measure": measure},
            ).fetchone()
            if getData is not None:
                dataDict = getData._asdict()
                return dataDict["ESG_MEASURE_ID"]
    except Exception as e:
        logger.error("Error processing data: %s", e)
        raise


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
                priority = row[7] if not pd.isna(row[7]) else 0
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
                priority = row[9] if not pd.isna(row[9]) else 0
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
                priority = row[11] if not pd.isna(row[11]) else 0
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
                priority = row[13] if not pd.isna(row[13]) else 0
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
                priority = row[15] if not pd.isna(row[15]) else 0
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
    """
    Process the DataFrame and update the database.
    """
    try:
        # Get all form data information
        lvbCustomerFlag = False
        lvsOrganisation = df.iloc[6, 4:6].str.cat(sep=" ")
        lvsRole = df.iloc[6, 10:11].str.cat(sep=" ")
        lviStakeholderId = get_stakeholder_by_name(lvsRole, engine)
        if lviStakeholderId == 2:
            lvbCustomerFlag = True
        lvsSalutation = df.iloc[10, 4] if not pd.isna(df.iloc[10, 4]) else None
        lvsGender = df.iloc[10, 10] if not pd.isna(df.iloc[10, 10]) else None
        lvsFirstname = df.iloc[12, 4:6].str.cat(sep=" ")
        lvsLastname = df.iloc[12, 10:12].str.cat(sep=" ")
        lvdYearofBirth = int(df.iloc[14, 4]) if not pd.isna(df.iloc[14, 4]) else 1700
        lvsStreet = df.iloc[15, 4:6].str.cat(sep=" ")
        lvsZip = str(df.iloc[20, 4]) if not pd.isna(df.iloc[20, 4]) else None
        lvsCity = df.iloc[20, 10:12].str.cat(sep=" ")
        lvsCountry = df.iloc[22, 4:6].str.cat(sep=" ")
        lvsCountryIsoCode = get_country_iso_by_name(lvsCountry, engine)
        if lvsCountryIsoCode is None:
            lvsCountryIsoCode = "en"
        lvsPhone = df.iloc[24, 4:6].str.cat(sep=" ")
        lvsMobile = df.iloc[24, 10:12].str.cat(sep=" ")
        lvsMail = df.iloc[26, 4:6].str.cat(sep=" ")
        lvsComments = df.iloc[14, 13:14].str.cat(sep=" ")
        lvsCompanyFunction = df.iloc[8, 4:6].str.cat(sep=" ")
        lvsRelatedCompany = df.iloc[10, 14:15].str.cat(sep=" ")
        lvsQuestionaireDate = parse_date(df.iloc[6, 15], date_formats) if not pd.isna(df.iloc[6, 15]) else datetime.now().date()

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

        # add data for organisation, identified by organisation name
        lvoOrganisation.organisation_id = get_organisation(lvoOrganisation, engine)
        if lvoOrganisation.organisation_id is None:
            lvoOrganisation.organisation_id = add_organisation(lvoOrganisation, engine)

        # add data for related organisation, identified by organisation name
        lvoRelatedOrganisation.organisation_id = get_organisation(lvoRelatedOrganisation, engine)
        if lvoRelatedOrganisation.organisation_id is None:
            lvoRelatedOrganisation.organisation_id = add_organisation(lvoRelatedOrganisation, engine)


        lvoQuestionare = Questionare(
            questionaire_comments=lvsComments,
            questionaire_date=lvsQuestionaireDate,
            questionaire_related_company=lvoRelatedOrganisation
        )


        # check personID & add person if required
        lvoPerson.person_id = get_person(lvoPerson, engine)
        if lvoPerson.person_id is None:
            lvoPerson.person_id = add_person(lvoPerson, engine)

        # bind person to organisation

        bind_organisation_person(lvoPerson, lvoOrganisation, engine)

        logger.info("Form data processed successfully.")

        return lvoPerson, lvoOrganisation, lvoQuestionare
    except Exception as e:
        logger.error("Error processing data: %s", e)
        return None, None, None


def main():
    newQuest = "data/new/"
    completedQuest = "data/uploaded/"
    errorQuest = "data/error/"

    # Read database configuration
    db_config = read_config()

    # Connect to the database
    engine = connect_to_database(
        db_config["username"],
        db_config["host"],
        db_config["database"],
        db_config["port"],
    )

    for getQuestionaires in os.listdir(path.join(lcsBaseDir, newQuest)):
        questStack = os.fsdecode(getQuestionaires)
        if questStack.endswith(".xlsx"):
            # Read Excel files from directory            
            dfFormData = read_excel_data(path.join(lcsBaseDir, newQuest, questStack), 1)

            lvoPerson, lvoOrganisation, lvoQuestionare = process_form_data(
                dfFormData, engine
            )

            # Process data
            if lvoPerson is not None and lvoOrganisation is not None:
                if lvoPerson.stakeholder_id == 8:
                    dfCompanyPerspectiveData = read_excel_data(
                        path.join(lcsBaseDir, newQuest, questStack), 2
                    )
                    process_company_perspective(
                        dfCompanyPerspectiveData,
                        lvoPerson,
                        lvoOrganisation,
                        lvoQuestionare,
                        engine,
                    )

                    dfCompStakeholderPerspectiveData = read_excel_data(
                        path.join(lcsBaseDir, newQuest, questStack),
                        3,
                    )
                    process_company_stakeholder_perspective(
                        dfCompStakeholderPerspectiveData,
                        lvoPerson,
                        lvoOrganisation,
                        lvoQuestionare,
                        engine,
                    )
                else:
                    dfStakeholderPerspectiveData = read_excel_data(
                        path.join(lcsBaseDir, newQuest, questStack),
                        2,
                    )
                    process_stakeholder_perspective(
                        dfStakeholderPerspectiveData,
                        lvoPerson,
                        lvoOrganisation,
                        lvoQuestionare,
                        engine,
                    )
                # move to done
                os.replace(
                    path.join(lcsBaseDir, newQuest, questStack),
                    path.join(lcsBaseDir, completedQuest, questStack),
                )
            else:
                # move to error
                os.replace(
                    path.join(lcsBaseDir, newQuest, questStack),
                    path.join(lcsBaseDir, errorQuest, questStack),
                )


if __name__ == "__main__":
    main()
