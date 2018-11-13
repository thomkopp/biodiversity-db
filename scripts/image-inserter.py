#!/usr/bin/python

from __future__ import print_function
import sqlite3
import PythonMagick
import os
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#Database file
dbFile = '../db/geo2_fme.gpkg'
#Table
table = 'co_image'
#Image path column
imagePathColumn = 'file_path'
#Image thumb column
imageThumbColumn = 'content'
#Image thumb max dimension
thumbDimension = 800
#JPG Compression
jpgQuality = 30
#Image folder
imageFolder = '../images'

transformStr = str(thumbDimension) + 'x' + str(thumbDimension)

#Queries
selectQuery = 'SELECT rowid, ' + imagePathColumn + ' FROM ' + table + ' WHERE ' + imageThumbColumn + ' IS NULL'
updateQuery = 'UPDATE ' + table + ' SET ' + imageThumbColumn + ' = ? WHERE rowid = ?'

try:
    conn = sqlite3.connect(dbFile)
except Exception as e:
    eprint(e)
    exit(1)

c = conn.cursor()
c.execute(selectQuery)
rows = c.fetchall()

os.chdir(imageFolder)

i = 1
for row in rows:
    imageFile = row[1].replace('\\','/')
    try:
        img = PythonMagick.Image(imageFile)
    except Exception as e:
        eprint(imageFile + ': ' + e)
        continue
    imageFile = img.fileName()
    if max(img.size().height(), img.size().width()) > thumbDimension :
        try:
            img.transform(transformStr)
        except RuntimeError as e:
            eprint(str(row[0]) + " " + imageFile + ": " + str(e))
    blob = PythonMagick.Blob()
    img.quality(jpgQuality)
    img.write(blob, "jpg")
    #workaround in order the access the data within the blob
    try:
        blobData = blob.data
    except UnicodeDecodeError as e:
        blobData = e.object

    c.execute(updateQuery, (blobData, row[0]))
    if i%10 == 0:
        conn.commit()
    # progress
    print (str(i) + "/" + str(len(rows)) + ': ' + imageFile)
    i = i+1


conn.commit()
conn.close()
