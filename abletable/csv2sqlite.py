#!/usr/bin/env python
#
# A simple Python script to convert csv files to sqlite (with type guessing)
#
# @author: Rufus Pollock
# Placed in the Public Domain
# Bug fixes by Simon Heimlicher <sh@nine.ch> marked by `shz:'

from __future__ import print_function


import sys
import argparse
import csv
import sqlite3
import bz2
import gzip
from six import string_types, text_type

if sys.version_info[0] > 2:
    read_mode = 'rt'
else:
    read_mode = 'rU'

import time

def convert(filepath_or_fileobj, dbpath, table, headerspath_or_fileobj=None, compression=None, typespath_or_fileobj=None):
    t = time.time()

    if isinstance(filepath_or_fileobj, string_types):
        if compression is None:
            fo = open(filepath_or_fileobj, mode=read_mode)
        elif compression == 'bz2':
            try:
                fo = bz2.open(filepath_or_fileobj, mode=read_mode)
            except AttributeError:
                fo = bz2.BZ2File(filepath_or_fileobj, mode='r')
        elif compression == 'gzip':
            fo = gzip.open(filepath_or_fileobj, mode=read_mode)
    else:
        fo = filepath_or_fileobj

    try:
        dialect = csv.Sniffer().sniff(fo.readline())
    except TypeError:
        dialect = csv.Sniffer().sniff(str(fo.readline()))
    fo.seek(0)

    print("\n 1. Time Taken: %.3f sec" % (time.time()-t) )

    # get the headers
    header_given = headerspath_or_fileobj is not None
    if header_given:
        if isinstance(headerspath_or_fileobj, string_types):
            ho = open(headerspath_or_fileobj, mode=read_mode)
        else:
            ho = headerspath_or_fileobj
        header_reader = csv.reader(ho, dialect)
        headers = [header.strip() for header in next(header_reader)]
        ho.close()
    else:
        reader = csv.reader(fo, dialect)
        headers = [header.strip() or "column__%d"%i for i, header in enumerate(next(reader))]
        fo.seek(0)

    print("\n 2. Time Taken: %.3f sec" % (time.time()-t) )

    # get the types
    if typespath_or_fileobj is not None:
        if isinstance(typespath_or_fileobj, string_types):
            to = open(typespath_or_fileobj, mode=read_mode)
        else:
            to = typespath_or_fileobj
        type_reader = csv.reader(to, dialect)
        types = [_type.strip() for _type in next(type_reader)]
        to.close()
    else:
        # guess types
        type_reader = csv.reader(fo, dialect)
        if not header_given: next(type_reader)
        types = _guess_types(type_reader, len(headers))
        fo.seek(0)

    print("\n 3. Time Taken: %.3f sec" % (time.time()-t) )

    # now load data
    _columns = ','.join(
        ['"%s" %s' % (header, _type) for (header,_type) in zip(headers, types)]
        )

    reader = csv.reader(fo, dialect)
    if not header_given: # Skip the header
        next(reader)

    print("\n 4. Time Taken: %.3f sec" % (time.time()-t) )

    conn = sqlite3.connect(dbpath)
    conn.isolation_level = None
    # shz: fix error with non-ASCII input
    conn.text_factory = str
    c = conn.cursor()

    try:
        create_query = 'CREATE TABLE %s (%s)' % (table, _columns)
        c.execute(create_query)
    except:
        pass

    _insert_tmpl = 'INSERT INTO %s VALUES (%s)' % (table,
        ','.join(['?']*len(headers)))

    print("\n 5. Time Taken: %.3f sec" % (time.time()-t) )

    try:
        # c.execute('.separator "%s"' % dialect.delimiter)    
        # c.execute('.import %s base' % filepath_or_fileobj)
        import os
        csv_file_name = os.path.abspath(filepath_or_fileobj).replace('\\','/')
        os.system('sqlite3 {db} ".separator \'{sep}\'" ".import {csv} base"'.format(
            db=dbpath, csv=csv_file_name, sep=(dialect.delimiter or "\t")
        ))
        # os.system('sqlite3 {db} ".import {csv} base"'.format(
        #     db=dbpath, csv=csv_file_name
        # ))
        print("\n 6. Time Taken: %.3f sec" % (time.time()-t) )
        conn.commit()
        c.close()

        return dialect
    except:
        raise
        pass

    # line = 0
    for line, row in enumerate(reader, 1):
        # line += 1
        if len(row) == 0:
            continue

        do_start_trans = line % 25000 == 1
        do_commit = line % 25000 == 0
        if do_start_trans:
            # also yield?
            print("chunk", line // 25000)
            c.execute('BEGIN TRANSACTION')

        if len(row) > len(headers):
            new_headers = ["column__%d"%i for i in range(len(headers), len(row))] 
            for extra in new_headers:
                c.execute('''ALTER TABLE TableName ADD COLUMN ''' + extra + ''' INTEGER''')
            headers += new_headers
        # we need to take out commas from int and floats for sqlite to
        # recognize them properly ...
        try:
            row = [
                None if x == ''
                else float(x.replace(',', '')) if y == 'real'
                else int(x) if y == 'integer'
                else x for (x,y) in zip(row, types) ]
            c.execute(_insert_tmpl, row)
        except ValueError as e:
            print("Unable to convert value '%s' to type '%s' on line %d" % (x, y, line), file=sys.stderr)
        except Exception as e:
            # raise
            print(e)
            print("Error on line %d: %s" % (line, e), file=sys.stderr)

        if do_commit:
            c.execute('COMMIT')

    print("\n 6. Time Taken: %.3f sec" % (time.time()-t) )

    conn.commit()
    c.close()

    return dialect

def _guess_types(reader, number_of_columns, max_sample_size=100):
    '''Guess column types (as for SQLite) of CSV.
    :param fileobj: read-only file object for a CSV file.
    '''
    # we default to text for each field
    types = ['text'] * number_of_columns
    # order matters
    # (order in form of type you want used in case of tie to be last)
    options = [
        ('text', text_type),
        ('real', float),
        ('integer', int)
        # 'date',
        ]
    # for each column a set of bins for each type counting successful casts
    perresult = {
        'integer': 0,
        'real': 0,
        'text': 0
        }

    results = [ dict(perresult) for x in range(number_of_columns) ]
    sample_counts = [ 0 for x in range(number_of_columns) ]

    for row_index,row in enumerate(reader):
        if row_index > max_sample_size*10:
            break
        for column,cell in enumerate(row):
            cell = cell.strip()
            if len(cell) == 0:
                continue

            # replace ',' with '' to improve cast accuracy for ints and floats
            if(cell.count(',') > 0):
               cell = cell.replace(',', '')
               if(cell.count('E') == 0):
                  cell = cell + "E0"

            for data_type,cast in options:
                try:
                    cast(cell)
                    results[column][data_type] += 1
                    sample_counts[column] += 1
                except ValueError:
                    pass

        have_max_samples = True
        for column,cell in enumerate(row):
            if sample_counts[column] < max_sample_size:
                have_max_samples = False

        if have_max_samples:
            break

    for column,colresult in enumerate(results):
        for _type, _ in options:
            if colresult[_type] > 0 and colresult[_type] >= colresult[types[column]]:
                types[column] = _type

    return types


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
Convert a CSV file to a table in a SQLite database.
The database is created if it does not yet exist.
''')
    parser.add_argument('csv_file', type=str, help='Input CSV file path')
    parser.add_argument('sqlite_db_file', type=str, help='Output SQLite file')
    parser.add_argument('table_name', type=str, nargs='?', help='Name of table to write to in SQLite file', default='data')
    parser.add_argument('--headers', type=str, nargs='?', help='Headers are read from this file, if provided.', default=None)
    parser.add_argument('--types', type=list, nargs='?', help='Types are read from this file, if provided.', default=None)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--bz2', help='Input csv file is compressed using bzip2.', action='store_true')
    group.add_argument('--gzip', help='Input csv file is compressed using gzip.', action='store_true')

    args = parser.parse_args()

    compression = None
    if args.bz2:
        compression = 'bz2'
    elif args.gzip:
        compression = 'gzip'

    convert(args.csv_file, args.sqlite_db_file, args.table_name, args.headers, compression, args.types)
