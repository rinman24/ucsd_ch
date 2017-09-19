"""Docstring."""
import numpy as np
import os

import mysql.connector as conn
from mysql.connector import errorcode

import chamber.const as const
#import const
import chamber.sqldb as sqldb
#import sqldb

def connect_sqldb_chamber():
    """Use sqldb.connect_sqldb() to a MySQL server.

    Returns
    -------
    cnx : MySQLConnection
        Returns the MySQL connection object"""
    cnx = sqldb.connect_sqldb("test_chamber")
    return cnx

def connect_sqldb_results():
    """Use sqldb.connect_sqldb() to a MySQL server.

    Returns
    -------
    cnx : MySQLConnection
        Returns the MySQL connection object"""
    cnx = sqldb.connect_sqldb("test_results")
    return cnx



def create_views(cur_re, views):
    """Uses sqldb.create_tables to create tables in the database.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tables : list
        List of table names and DDL query language. For example:
        [('UnitTest',
        "CREATE TABLE UnitTest ("
        "    UnitTestID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "    Number DECIMAL(5,2) NULL,"
        "    String VARCHAR(30) NULL,"
        "  PRIMARY KEY (`UnitTestID`)"
        ");"))]
    """
    sqldb.create_tables(cur_re, views)

def normalized_mass(cur_ch, cur_re, test_id):
    """Use a TestID to calculate and write the normalized mass for a given test.

    This function searches the chamber database for the masses recorded for the given TestID.
    This function then calculates the normalized masses for the test and records the masses in the
    results database.

    Parameters
    ----------
    cur_ch : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    cur_re : MySQLCursor
        Cursor used to interact with the results MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.
    """
    cur_re.execute(const.GET_TEST_ID_NM.format(test_id))
    if not cur_re.fetchall():
        cur_ch.execute(const.GET_MASS.format(test_id))
        mass = np.array([mass[0] for mass in cur_ch.fetchall()])
        norm_mass = (mass-min(mass))/(max(mass)-min(mass))
        nm_id = [(test_id, '{:.7f}'.format(round(mass, 7))) for mass in norm_mass]
        cur_re.executemany(const.ADD_NORM_MASS, nm_id)

def get_mass(cur_ch, test_id):
    """Use a TestID to get the mass observations from a given test.

    This function searches the chamber database for the masses recorded for the given TestID.

    Parameters
    ----------
    cur_ch : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    mass : list of floats
        List of mass observations for the given TestID.
    """
    cur_ch.execute(const.GET_MASS.format(test_id))
    mass = [float(mass[0]) for mass in cur_ch.fetchall()]
    return mass

def get_dew_point(cur_ch, test_id):
    """Use a TestID to get the dew point observations from a given test.

    This function searches the chamber database for the dew points recorded for the given TestID.

    Parameters
    ----------
    cur_ch : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    dew_point : list of floats
        List of dew point observations for the given TestID.
    """
    cur_ch.execute(const.GET_DEW_POINT.format(test_id))
    dew_point = [float(dp[0]) for dp in cur_ch.fetchall()]
    return dew_point

def get_pressure(cur_ch, test_id):
    """Use a TestID to get the pressure observations from a given test.

    This function searches the chamber database for the pressures recorded for the given TestID.

    Parameters
    ----------
    cur_ch : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    pressure : list of floats
        List of pressure observations for the given TestID.
    """
    cur_ch.execute(const.GET_PRESSURE.format(test_id))
    pressure = [float(pa[0]) for pa in cur_ch.fetchall()]
    return pressure

def lin_reg(start, end):
    slope, intercept, r_value, p_value, std_err = stats.linregress(idx[start-end:start+end],mass[start-end:start+end])
    if r_value**2 >= 0.99:
        return slope, r_value**2
