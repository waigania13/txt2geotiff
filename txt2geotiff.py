##[CSMAP]=group
##Tool for CSMapMaker . Convert txt/csv to GeoTIFF=name
##input_directory=folder
##target_files=selection txt;csv;xyz
##delimiter=selection comma;tab;space
##input_encoding=selection utf-8;shift-jis;eus-jp;ascii
##start_import_at_row=number 1
##field_x=number 1
##field_y=number 2
##field_z=number 3
##crs=crs
##output_directory=folder
##outputDir=output string

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.ProcessingLog import ProcessingLog
import glob, os
import csv
import codecs
import tempfile

def get_encoding( input_encoding ):
    if input_encoding == 0:
        return "utf-8"
    elif input_encoding == 1:
        return "shift-jis"
    elif input_encoding == 2:
        return "euc-jp"
    elif input_encoding == 3:
        return "ascii"
    return "utf-8"
    
def get_delimiter( delimiter ):
    if delimiter == 0:
        return ","
    return None

def get_target_files( target_files ):
    if target_files == 0:
        return "txt"
    elif target_files == 1:
        return "csv"
    elif target_files == 2:
        return "xyz" 
    return "txt"

def txt2geotiff( filename, delimiter, start, field_x, field_y, field_z, crs, output_directory, input_encoding ):
    index_max = max([field_x, field_y, field_z])
    
    fp = codecs.open(file, "r",  input_encoding)
    name, ext = os.path.splitext(os.path.basename(filename))
    output_file = os.path.join(output_directory, name) + ".tif"
    xyz_file = tempfile.NamedTemporaryFile(mode='w+t', delete=False, suffix=".xyz")

    row_num = 0
    for dummy in range(0, start-1):
        fp.readline()
        row_num = row_num + 1
        
    rows = fp.readline()
    while rows:
        row_num = row_num + 1
        row = rows.split(delimiter)

        if len(row) < index_max:
            ProcessingLog().addToLog(ProcessingLog.LOG_INFO, "skip row({0}) : {1}".format(row_num, filename ))
            continue
        xyz_file.write("{0} {1} {2}\n".format(row[field_x-1], row[field_y-1], row[field_z-1]))
        
        rows = fp.readline()
        
    fp.close()
    xyz_file.close()
    
    dem_layer = QgsRasterLayer(xyz_file.name, "temp")
    dem_layer.setCrs(QgsCoordinateReferenceSystem(crs))
    
    extent = dem_layer.extent()
    projwin = "{0},{1},{2},{3}".format(extent.xMinimum(), extent.xMaximum(), extent.yMinimum(), extent.yMaximum())
    
    processing.runalg("gdalogr:translate", dem_layer, 100, True,  "", 0,  crs, projwin, False, 5, 4, 75, 6, 1, False, 0, True, "", output_file)
    #os.remove(xyz_file.name)

if not input_directory or not output_directory:
    raise GeoAlgorithmExecutionException("Please specify both, input directory and output directory.")

if min([field_x, field_y, field_z]) <= 0:
    raise GeoAlgorithmExecutionException("Please check field x/filed y/filed z value.")
if len(set([field_x, field_y, field_z])) != 3:
    raise GeoAlgorithmExecutionException("Please check field x/filed y/filed z value.")

for file in glob.glob( "{0}/*.{1}".format(input_directory, get_target_files(target_files)) ):
    txt2geotiff(file, get_delimiter(delimiter), start_import_at_row, field_x, field_y, field_z, crs, output_directory,  get_encoding(input_encoding) )
    
outputDir = output_directory 
