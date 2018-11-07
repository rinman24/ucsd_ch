"""
CRUD Manager module.

Functions
---------

- `create_tables` -- Manage construction of tables for a given database.
- `drop_tables` -- Manage destuction of tables for a given database.

"""

import configparser

import mysql.connector

import chamber.utility.ddl as util_ddl


def _get_credentials():
    """
    Use configparser to obtain credentials.

    Returns
    -------
    dict
        Crednetials included in the config.ini file. Keys include: `host`,
        `user`, and `password`.

    Raises
    ------
    FileNotFoundError
        If the config.ini file is not found.
    KeyError
        If any keys are missing from the `MySQL-Server` section of the
        config.ini file.

    Examples
    --------
    >>> creds = _get_credentials()
    >>> type(creds)
    <class 'dict'>

    """
    config_parser = configparser.ConfigParser()

    # config_parser.read() returns a list containing the files read;
    # e.g. ['config.ini'].
    config_result = config_parser.read('config.ini')

    if config_result:  # The config file was read in.
        credentials = dict(config_parser['MySQL-Server'])
        required_key_set = {'host', 'user', 'password'}
        config_key_set = set(credentials.keys())

        if required_key_set.issubset(config_key_set):
            return credentials
        else:
            missing_key_set = required_key_set.difference(config_key_set)
            error_message = (
                'KeyError: config file is missing the following key: {}.'
                .format(missing_key_set.pop())
                )
            raise KeyError(error_message)
    error_message = 'FileNotFoundError: config.ini does not exits.'
    raise FileNotFoundError(error_message)


def _connect(creds, database=None):
    """
    Use credentials to connect to mySQL database.

    Parameters
    ----------
    creds : dict
        Credentials for the mysql database.
    database : str, optional
        Database to connect to. If database is not specified, you must run
        cursor.execute('USE <database>;') to proceed.

    Returns
    -------
    cnx : mysql.connector.MySQLConnection
        MySQL database connection object
    cur : mysql.connector.cursor.MySQLCursor
        MySQL database cursor object corresponding to `cnx`.

    Examples
    --------
    Connect to a host without specifying the database. You will have to run
    cursor.execute('USE <database>;') to proceed.

    >>> creds = dict(host='address', user='me', password='secret')
    >>> cnx, cur = _connect(creds)
    >>> cur.execute('USE schema;')
    >>> cnx.commit()
    >>> cur.close()

    Specifying the optional database can be used to save time.

    >>> cnx, cur = _connect(creds, database='schema')
    >>> cnx.commit()
    >>> cur.close()

    """
    cnx = mysql.connector.connect(**creds)
    cur = cnx.cursor()
    if database:
        cur.execute(
            'USE {};'.format(database)
            )
    return cnx, cur


def _execute_build(database, cursor):
    """
    Use cursor and database name to build tables.

    Parameters
    ----------
    database : str
        Name of the database, which is used to lookup required ddl from
        utility.
    cursor : mysql.connector.cursor.MySQLCursor
        mySQL cursor object

    Returns
    -------
    str
        Message confirming that tables were built for the database.

    Examples
    --------
    >>> _execute_build('schema', cursor)
    'Success.'

    """
    table_order = util_ddl.build_instructions[database, 'table_order']
    ddl = util_ddl.build_instructions[database, 'ddl']

    for table in table_order:
        print('Creating table {}: '.format(table), end='')
        cursor.execute(ddl[table])
        print('OK')
    return 'Successfully built {} tables.'.format(database)


def _execute_drop(database, cursor):
    """
    Use cursor and database name to drop tables.

    Parameters
    ----------
    database : str
        Name of the database, which is used to lookup required table order
        from utility.
    cursor : mysql.connector.cursor.MySQLCursor
        mySQL cursor object

    Returns
    -------
    str
        Message confirming that tables were dropped for the database.

    Examples
    --------
    >>> _execute_drop('schema', cursor)
    'Successfully dropped schema tables.'

    """
    table_order = util_ddl.build_instructions[database, 'table_order']
    reversed_table_order = table_order[::-1]

    for table in reversed_table_order:
        print('Dropping table {}: '.format(table), end='')
        cursor.execute('DROP TABLE {};'.format(table))
        print('OK')
    return 'Successfully dropped {} tables.'.format(database)


def create_tables(database):
    """
    Orchestrate construction of tables for a given database.

    In general, creation of tables occurs most often during creation of the
    schema. As a result, this function attempts to create the database if it
    doesn't already exist.

    Parameters
    ----------
    database : str
        Name of the database (or schema)

    Returns
    -------
    str
        Message confirming that tables were built for the database.

    Examples
    --------
    >>> message = create_tables('schema')
    >>> message
    'Successfully built schema tables.'

    """
    creds = _get_credentials()
    try:
        _, cur = _connect(creds)
    except mysql.connector.Error as err:
        print(err)
        return 'mySQL Error: ' + str(err)
    cur.execute(
        'CREATE DATABASE IF NOT EXISTS {} '
        'DEFAULT CHARACTER SET latin1 ;'
        .format(database)
        )
    cur.execute('USE {};'.format(database))
    message = _execute_build(database, cur)
    return message


def drop_tables(database, drop_db=False):
    """
    Orchestrate destruction of tables for a given database.

    Parameters
    ----------
    database : str
        Name of the database (or schema)
    drop_db : bool, defalut False
        Deault beavior is to leave the schema in place after all tables are
        dropped. If `drop_db` is set to True, the schema is dropped with the
        tables.

    Returns
    -------
    str
        Message confirming that tables were dropped for the database. Will
        also confirm that database was dropped if `drop_db` is True.

    Examples
    --------
    Default behavior is to leave the schema in place.

    >>> message = drop_tables('schema')
    >>> message
    'Successfully dropped schema tables.'

    However, you can also drop the schema with the tables.

    >>> message = drop_tables('schema', drop_db=True)
    >>> message
    'Successfully dropped schema tables. Database also dropped.'

    """
    creds = _get_credentials()
    _, cur = _connect(creds, database=database)
    message = _execute_drop(database, cur)
    if drop_db:
        cur.execute(
            'DROP DATABASE {};'.format(database)
            )
        message += ' Database also dropped.'
    return message
