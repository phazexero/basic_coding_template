import psycopg2
from psycopg2 import sql, OperationalError, pool
import os
from contextlib import contextmanager
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                            logging.FileHandler("app.log"),  # Log to a file
                            logging.StreamHandler()  # Log to the console
                        ]
                    )
logger = logging.getLogger(__name__)

# Database connection configuration (modify with your own settings)
DB_USER = os.getenv("DB_USER")
ENCODED_DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Define the connection pool with a minimum of 1 connection and a maximum of 10
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=DB_USER,
    password=ENCODED_DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

class Database:
    def __init__(self):
        self.connection = None

    def log_connection_status(self):
        """
        Logs the current number of active and available connections in the pool.
        """
        active_connections = connection_pool._used  # Number of used connections
        total_connections = connection_pool.maxconn  # Maximum number of connections

        logger.info(f"Active connections: {active_connections}, Total connections allowed: {total_connections}")

    def connect(self, retries=3, delay=2):
        """
        Establishes a connection to the database from the pool. Retries the connection
        a few times if OperationalError is encountered.
        """
        for attempt in range(retries):
            try:
                if not self.connection or self.connection.closed != 0:
                    self.connection = connection_pool.getconn()  # Get a connection from the pool
                logger.info("Database connection established.")
                self.log_connection_status()  # Log connection status
                return  # Exit the loop on successful connection
            except OperationalError as e:
                logger.error(f"Database connection failed: {e}")
                if attempt < retries - 1:
                    logger.info(f"Retrying connection in {delay} seconds...")
                    time.sleep(delay)  # Wait before retrying
                else:
                    logger.critical("All retry attempts failed. Raising exception.")
                    raise e  # Raise exception if all retries fail

    def disconnect(self):
        if self.connection:
            connection_pool.putconn(self.connection)  # Return the connection to the pool
            logger.info("Database connection returned to pool.")
            self.log_connection_status()  # Log connection status after disconnecting
            self.connection = None

    @contextmanager
    def get_cursor(self):
        """
        Context manager to manage cursor open and close.
        It ensures the cursor is closed after its use.
        """
        cursor = self.connection.cursor()
        logger.info("Cursor opened.")
        try:
            yield cursor
        finally:
            cursor.close()
            logger.info("Cursor closed.")

    def execute_query(self, query, params=None, retry=False):
        """
        Executes a query, with automatic reconnect and retry in case of connection failure.
        Automatically closes the connection after the transaction.
        """
        try:
            # Ensure the connection is established before executing the query
            if not self.connection or self.connection.closed != 0:
                self.connect()

            with self.get_cursor() as cursor:
                logger.debug(f"Executing query: {query}")
                cursor.execute(query, params)

                # Check if the query is a SELECT statement
                if query.strip().upper().startswith("SELECT"):
                    # Fetch and return all results for SELECT queries
                    result = cursor.fetchall()
                    logger.debug(f"Query result: {result}")
                    return result
                else:
                    # Commit the transaction for non-SELECT queries (INSERT, UPDATE, DELETE)
                    self.connection.commit()
                    logger.info(f"Query executed successfully, rows affected: {cursor.rowcount}")
                    return cursor.rowcount
        except OperationalError as e:
            logger.error(f"Query execution failed: {e}")
            if not retry:
                logger.info("Reconnecting and retrying the query...")
                self.connect()  # Reconnect to the database
                # Retry the query after reconnecting
                return self.execute_query(query, params, retry=True)
            else:
                logger.error("Query retry failed after reconnecting.")
                raise
        finally:
            # Ensure the connection is closed after the transaction
            self.disconnect()

    def execute_many(self, query, params_list, retry=False):
        """
        Executes a query multiple times for different parameters using executemany, with retry mechanism.
        Automatically closes the connection after the batch transaction.
        """
        try:
            # Ensure the connection is established before executing the query
            if not self.connection or self.connection.closed != 0:
                self.connect()

            with self.get_cursor() as cursor:
                logger.debug(f"Executing batch query: {query} with {len(params_list)} sets of parameters.")
                cursor.executemany(query, params_list)

                # Commit the transaction for non-SELECT queries (INSERT, UPDATE, DELETE)
                self.connection.commit()
                logger.info(f"Batch query executed successfully, total rows affected: {cursor.rowcount}")
                return cursor.rowcount
        except OperationalError as e:
            logger.error(f"Batch query execution failed: {e}")
            if not retry:
                logger.info("Reconnecting and retrying the batch query...")
                self.connect()  # Reconnect to the database
                # Retry the query after reconnecting
                return self.execute_many(query, params_list, retry=True)
            else:
                logger.error("Batch query retry failed after reconnecting.")
                raise
        finally:
            # Ensure the connection is closed after the transaction
            self.disconnect()


# Create a singleton instance of the Database
database_instance = Database()

# Functions to connect and disconnect (to be used in main.py)
def connect_to_db():
    database_instance.connect()

def disconnect_from_db():
    database_instance.disconnect()
