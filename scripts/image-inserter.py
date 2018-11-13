#!/usr/bin/python

import sqlite3
import PythonMagick
import os

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
#Image folder
imageFolder = '../images'

os.chdir(imageFolder)

transformStr = str(thumbDimension) + 'x' + str(thumbDimension)

#Queries
selectQuery = 'SELECT rowid, ' + imagePathColumn + ' FROM ' + table
updateQuery = 'UPDATE ' + table + ' SET ' + imageThumbColumn + ' = ? WHERE rowid = ?'

conn = sqlite3.connect(dbFile)
c = conn.cursor()
c.execute(selectQuery)
rows = c.fetchall()
for row in rows:
    imageFile = row[1].replace('\\','/')
    img = PythonMagick.Image(imageFile)
    if max(img.size().height(), img.size().width()) > thumbDimension :
        img.transform(transformStr)
    blob = PythonMagick.Blob()
    img.quality(30)
    img.write(blob, "jpg")
    try:
        blobData = blob.data
    except UnicodeDecodeError as e:
        blobData = e.object

    c.execute(updateQuery, (blobData, row[0]))

conn.commit()
conn.close()
