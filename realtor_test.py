import unittest
from realtor import *
import os
import sqlalchemy
import myapp

#static json file to use as the test file
#also do one test case to make sure it pulls data property

conn= sqlite3.connect(DBNAME)
cur= conn.cursor()
x= get_property_data_buy('48104')
y= get_property_data_rent('48104')


class TestDataBase(unittest.TestCase):

    def test_data(self):
        conn= sqlite3.connect(DBNAME)
        cur= conn.cursor()
        self.assertEqual('realtor.db', DBNAME)
        self.assertTrue('Buy')
        self.assertTrue('Rent')


class TestZipCodeSearch(unittest.TestCase):

    def test_data_collect(self):
        sql = 'SELECT Address FROM Buy'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn('', DBNAME)
        self.assertIn(' 2023 Seneca-Geddes Ave, Ann Arbor, MI 48104 ', result_list[0])


class TestBuySearch(unittest.TestCase):


    def test_buy_search(self):
        sql = 'SELECT Type FROM Buy'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 48)
        self.assertIn(('House for Sale'), result_list[0])
        self.assertIn(('Condo/Townhome'), result_list[3])
        self.assertIn(('Land'), result_list[25])
        self.assertIn(('Multi-Family Home'), result_list[30])
#
class TestRentSearch(unittest.TestCase):

    def test_rent_search(self):
        sql = 'SELECT Type FROM Rent'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 50)
        self.assertIn(('Apartment for Rent'), result_list[0])
        self.assertIn(('House for Rent'), result_list[5])
        self.assertIn(('Condo/Townhome for Rent'), result_list[8])
        self.assertIn(('Duplex/Triplex for Rent'), result_list[13])

if __name__ == '__main__':
    unittest.main()
