import logging
from fastapi import HTTPException
from helper_fn import SQL_connection
logger = logging.getLogger(__name__)
async def customers():
    """
    Get all customers.
    return: List[Dict]
    """
    try:

        customer_dict = SQL_connection("select * from terramodb.customers")
    
    except Exception as e:
        logger.error(f"Database connection error: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Database connection error.")

    return {'response':customer_dict}



async def get_customer_by_id(id: int):
    """
    Get customer by ID.
    :param customer_id: int
    return: Dict
    """
    try:
        QUERY = f"SELECT * FROM customers WHERE id = {customer_id}"
        org_dict = SQL_connection(QUERY)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error.")

    if customer_dict is None:
        raise HTTPException(status_code=404, detail="Customer not found.")

    return customer_dict[0]
