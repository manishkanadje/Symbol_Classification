from xml.dom import minidom
import pdb

def convertStrokesToCsv(inkml_file):
    xmldoc = minidom.parse(inkml_file)

    itemlist = xmldoc.getElementsByTagName('trace')
    csv_file = inkml_file[:inkml_file.find('.')] + '.csv'
    f = open(csv_file,'w')


    for item in itemlist:
        #pdb.set_trace()
        coordinates = item.firstChild.nodeValue;
        coordinates = coordinates[1:]
        coordinates = coordinates.replace(', ', ',')
        #coordinates = ' '.join(coordinates.split(", "))
        #coordinates = coordinates.split(",")
        #pdb.set_trace()
        _id = item.attributes['id'].value
        #print(_id + "," + coordinates)
        #pdb.set_trace()
        f.write(_id + "," + coordinates)

    f.close()

convertStrokesToCsv('200922-949-211.inkml')
#convertStrokesToCsv('sample.inkml')
