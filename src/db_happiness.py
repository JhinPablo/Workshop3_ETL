import os
import logging
import psycopg2
import pandas as pd

logging.basicConfig(level=logging.INFO)

# Intentar importar las credenciales de la base de datos desde el archivo src/credentials
try:
    from src.credentials import get_database_credentials
except ImportError:
    from credentials import get_database_credentials


class DB:
    """
    A class to manage PostgreSQL database connections, execute queries, and 
    retrieve data as Pandas DataFrames.

    Attributes:
        dbname (str): The name of the database.
        user (str): The username to connect to the database.
        password (str): The password for the database user.
        host (str): The host address of the database server.
        port (str): The port number on which the database server is running.
        conn (psycopg2.extensions.connection or None): The database connection object.
        cursor (psycopg2.extensions.cursor or None): The cursor object for executing queries.

    Methods:
        connect():
            Establishes a connection to the database.

        close():
            Closes the database connection and cursor.

        execute(query_path, fetch_results=True):
            Executes a SQL query from a file and optionally fetches the results.

        fetch_as_dataframe(query_path):
            Executes a SQL query from a file and returns the results as a Pandas DataFrame.

        create_table():
            Creates the table in the database if it doesn't exist.
    """

    def __init__(self):
        """
        Initializes the DB class with database credentials and sets up connection
        and cursor attributes.
        """
        credentials = get_database_credentials()
        self.dbname = credentials['dbname']
        self.user = credentials['user']
        self.password = credentials['password']
        self.host = credentials['host']
        self.port = credentials['port']
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database using the provided credentials.

        Raises:
            Exception: If an error occurs while attempting to connect to the database.
        """
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            logging.info("✔ Connected to database")
        except Exception as e:
            logging.error(f"✖ Error connecting to database: {e}")
            raise

    def close(self):
        """
        Closes the database cursor and connection, if they are open.
        """
        if self.cursor:
            self.cursor.close()
            logging.info("✔ Cursor closed")
        if self.conn:
            self.conn.close()
            logging.info("✔ Connection closed")

    def execute_query_file(self, query_path, fetch_results=True):
        """
        Executes a SQL query from a file and commits the transaction.

        Args:
            query_path (str): The file path to the SQL query.
            fetch_results (bool, optional): Whether to fetch and return the query results.
                                            Defaults to True.

        Returns:
            list or None: A list of tuples representing the query results if `fetch_results`
                        is True, otherwise None.

        Raises:
            Exception: If an error occurs during query execution or result fetching.
        """
        try:
            with open(query_path, 'r') as file:
                query = file.read()
            self.connect()
            self.cursor.execute(query)
            self.conn.commit()
            logging.info("✔ Query executed")

            if fetch_results:
                return self.cursor.fetchall()
            return None
        except Exception as e:
            logging.error(f"✖ Error executing query: {e}")
            self.conn.rollback()
            raise
        finally:
            self.close()

    def execute_in_batches(self, query_path, batch_size=50000):
        """
        Executes a SQL query in batches from a file.

        Args:
            query_path (str): The file path to the SQL query.
            batch_size (int, optional): Number of records to process per batch. Defaults to 50000.

        Raises:
            Exception: If an error occurs during query execution.
        """
        try:
            self.connect()
            with open(query_path, 'r') as file:
                batch = []
                for line in file:
                    batch.append(line)
                    # If we've reached the batch size, execute the batch
                    if len(batch) == batch_size:
                        try:
                            self.cursor.execute(''.join(batch))
                            self.conn.commit()
                            logging.info(f"✔ Executed a batch of {batch_size} records")
                        except Exception as e:
                            logging.error(f"✖ Error executing batch: {e}")
                            logging.error(f"Batch content: {''.join(batch)}")
                            self.conn.rollback()
                            raise
                        batch = []  # Reset the batch list

                # Execute any remaining lines that didn't fill up a complete batch
                if batch:
                    try:
                        self.cursor.execute(''.join(batch))
                        self.conn.commit()
                        logging.info(f"✔ Executed the final batch of {len(batch)} records")
                    except Exception as e:
                        logging.error(f"✖ Error executing final batch: {e}")
                        logging.error(f"Batch content: {''.join(batch)}")
                        self.conn.rollback()
                        raise
        except Exception as e:
            logging.error(f"✖ Error executing batches: {e}")
            raise
        finally:
            self.close()

    def fetch_as_dataframe(self, query):
        """
        Executes a SQL query from a file and returns the results as a Pandas DataFrame.

        Args:
            query_path (str): The file path to the SQL query.

        Returns:
            pandas.DataFrame: A DataFrame containing the query results.

        Raises:
            Exception: If an error occurs during query execution or DataFrame creation.
        """
        try:
            self.connect()
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            colnames = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(rows, columns=colnames)
            logging.info("✔ Data loaded into DataFrame")
            return df
        except Exception as e:
            logging.error(f"✖ Error loading data into DataFrame: {e}")
            raise
        finally:
            self.close()

    def execute_query(self, query, fetch_results=True):
        try:
            self.connect()
            self.cursor.execute(query)
            self.conn.commit()
            logging.info("✔ Query executed")

            if fetch_results:
                rows = self.cursor.fetchall()
                colnames = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(rows, columns=colnames)
                return df
            return None
        except Exception as e:
            logging.error(f"✖ Error executing query: {e}")
            self.conn.rollback()
            raise
        finally:
            self.close()

    def create_table(self):
        """
        Creates a table if it doesn't already exist. Modify this query as necessary for your table schema.

        Example: Creating a table 'users' with columns 'id', 'name', and 'age'.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS happiness_data (
            id SERIAL PRIMARY KEY,
            country VARCHAR(255),
            score DECIMAL,
            gdp_per_capita DECIMAL,
            healthy_life_expectancy DECIMAL,
            freedom DECIMAL
        );
        """
        try:
            self.connect()
            self.cursor.execute(create_table_query)
            self.conn.commit()
            logging.info("✔ Table created successfully")
        except Exception as e:
            logging.error(f"✖ Error creating table: {e}")
            self.conn.rollback()
            raise
        finally:
            self.close()
