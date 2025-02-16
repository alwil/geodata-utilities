# gefreader.py example based on: https://github.com/creepywaterbug/Gef2Open/blob/master/Gef2Open.py

import re
import os


# Hulpfuncties
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def removetrailers(string):
    d = re.sub('^[\t|\ ]*', '', string)
    e = re.sub('\r\n$', '', d)
    return e


class Gef2OpenClass:
    def __init__(self):
        dummy=[]
        
    # Purpose: Of een BORE-Report file is (boring)
    def gbr_is_gbr(self):
        if 'PROCEDURECODE' in self.headerdict:
            if 'GEF-BORE-Report' in self.headerdict['PROCEDURECODE']:
                out = True
            else:
                out = False
        else:
            if 'REPORTCODE' in self.headerdict:
                if 'GEF-BORE-Report' in self.headerdict['REPORTCODE']:
                    out = True
                else:
                    out = False
            else:
                out = False
        try:
            return out
        except:
            return None

    # Purpose: Of een GEF-CPT-Report file is (sondering)
    def gcr_is_gcr(self):
        if 'PROCEDURECODE' in self.headerdict:
            if 'GEF-CPT-Report' in self.headerdict['PROCEDURECODE']:
                out = True
            else:
                out = False
        else:
            if 'REPORTCODE' in self.headerdict:
                if 'GEF-CPT-Report' in self.headerdict['REPORTCODE']:
                    out = True
                else:
                    out = False
            else:
                out = False
        try:
            return out
        except:
            return None

    # Purpose: Of #COMPANYID aanwezig
    def get_companyid_flag(self):
        if 'COMPANYID' in self.headerdict:
            if len(self.headerdict['COMPANYID']) > 0:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft aantal kolommen in het data block
    def get_column(self):
        if 'COLUMN' in self.headerdict:
            if len(self.headerdict['COLUMN']) > 0:
                out = self.headerdict['COLUMN'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #COLUMN aanwezig
    def get_column_flag(self):
        if ('COLUMN' in self.headerdict):
            if len(self.headerdict['COLUMN']) > 0:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft nodata waarde voor geselecteerde kolom
    def get_column_void(self, i_Kol):
        if 'COLUMNVOID' in self.headerdict:
            if len(self.headerdict['COLUMNVOID']) > i_Kol - 1:
                out = self.headerdict['COLUMNVOID'][i_Kol][1]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #COLUMNVOID aanwezig
    def get_column_void_flag(self, i_Kol):
        if 'COLUMNVOID' in self.headerdict:
            if len(self.headerdict['COLUMNVOID']) > i_Kol - 1:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft columninfo terug in een list
    def get_column_info(self, i_Kol):
        if 'COLUMNINFO' in self.headerdict:
            if len(self.headerdict['COLUMNINFO']) > i_Kol - 1:
                out = self.headerdict['COLUMNINFO'][i_Kol]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #COLUMNINFO aanwezig
    def get_column_info_flag(self, i_Kol):
        if 'COLUMNINFO' in self.headerdict:
            if len(self.headerdict['COLUMNINFO']) > i_Kol - 1:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft company naam
    def get_companyid_Name(self):
        if 'COMPANYID' in self.headerdict:
            if len(self.headerdict['COMPANYID']) > 0:
                out = self.headerdict['COMPANYID'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft waarde uit bepaalde cel van data block
    def get_data(self, i_Kol, iRij):
        if 'datablok' in self.headerdict:
            if iRij in self.headerdict['datablok']:
                if len(self.headerdict['datablok'][iRij]) >= i_Kol - 1:
                    out = self.headerdict['datablok'][iRij][i_Kol - 1]
                else:
                    err = 'MissingKol'
            else:
                err = 'MissingRij'
        else:
            err = 'MissingDatablok'
        try:
            return out
        except:
            # return None
            return err

    # TODO continue get_data_iter
    # Purpose: geeft een iterator met alle waarden voor een bepaalde kolom in een data block
    def get_data_iter(self, i_Kol):
        try:
            if 'datablok' in self.headerdict:
                if len(self.headerdict['datablok'][1]) >= i_Kol - 1:
                    void = self.get_column_void(i_Kol)
                    for i_Rij in range(1, 1 + int(self.get_nr_scans())):
                        depth = self.get_data(1, i_Rij)
                        value = self.get_data(i_Kol, i_Rij)
                        if value == void:  #Replace nodata value for None
                            value = None
                        yield (depth, value)
                else:
                    err = 'MissingKol'
            else:
                err = 'MissingDatablok'
        except:
            yield err

    # Purpose: geeft een iterator met alle waarden voor een bepaalde kolom in een data block
    def get_column_iter(self, i_Kol):
        try:
            if 'datablok' in self.headerdict:
                if len(self.headerdict['datablok'][1]) >= i_Kol - 1:
                    void = self.get_column_void(i_Kol)
                    for i_Rij in range(1, 1 + int(self.get_nr_scans())):
                        value = self.get_data(i_Kol, i_Rij)
                        if value == void:  #Replace nodata value for None
                            value = None
                        yield value
                else:
                    err = 'MissingKol'
            else:
                err = 'MissingDatablok'
        except:
            yield err

    def get_data_column(self, i_Kol):
        """extract data from file"""
        value = []
        for a in self.get_column_iter(i_Kol):
            value.append(a)

        column_info = self.get_column_info(i_Kol)
        unit = column_info[1]
        name = column_info[2]

        return value, unit, name

    # Purpose: Of gegeven #MEASUREMENTTEXT index aanwezig
    def get_measurementtext_flag(self, i_Index):
        if 'MEASUREMENTTEXT' in self.headerdict:
            if i_Index in self.headerdict['MEASUREMENTTEXT']:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Of gegeven #MEASUREMENTVAR index aanwezig
    def get_measurementvar_flag(self, i_Index):
        if 'MEASUREMENTVAR' in self.headerdict:
            if i_Index in self.headerdict['MEASUREMENTVAR']:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft measurementtext tekst
    def get_measurementtext_Tekst(self, i_Index):
        if 'MEASUREMENTTEXT' in self.headerdict:
            if i_Index in self.headerdict['MEASUREMENTTEXT']:
                if 1 in self.headerdict['MEASUREMENTTEXT'][i_Index]:
                    out = self.headerdict['MEASUREMENTTEXT'][i_Index][1]  # ??
                else:
                    err = 'MissingValue'
            else:
                err = 'MissingIndex'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft measurementvar value
    def get_measurementvar_Value(self, i_Index):
        if 'MEASUREMENTVAR' in self.headerdict:
            if i_Index in self.headerdict['MEASUREMENTVAR']:
                if len(self.headerdict['MEASUREMENTVAR'][i_Index]) > 0:
                    out = self.headerdict['MEASUREMENTVAR'][i_Index][1]
                else:
                    err = 'MissingValue'
            else:
                err = 'MissingIndex'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft aantal rijen in het data block
    # neem aan waarde achter 'LASTSCAN', maar check dit!
    def get_nr_scans(self):
        if 'LASTSCAN' in self.headerdict:
            if len(self.headerdict['LASTSCAN']) > 0:
                out = self.headerdict['LASTSCAN'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #PARENT aanwezig
    # neeem aan dat er een par 'PARENT' aanwezig moet zijn. Check!
    def get_parent_flag(self):
        if ('PARENT' in self.headerdict):
            if len(self.headerdict['PARENT']) > 0:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None  # test

    # Purpose: Geeft referentie naar de parent, bv bestandsnaam
    def get_parent_reference(self):
        if 'PARENT' in self.headerdict:
            if len(self.headerdict['PARENT']) > 0:
                out = self.headerdict['PARENT'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            return 'Error:%s' % (err)

    # Purpose: Of #PROCEDURECODE aanwezig
    def get_procedurecode_flag(self):
        if 'PROCEDURECODE' in self.headerdict:
            if len(self.headerdict['PROCEDURECODE']) > 0:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft procedurecode code
    def get_procedurecode_Code(self):
        if 'PROCEDURECODE' in self.headerdict:
            if len(self.headerdict['PROCEDURECODE']) > 0:
                out = self.headerdict['PROCEDURECODE'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #PROJECTID aanwezig
    def get_projectid_flag(self):
        if 'PROJECTID' in self.headerdict:
            if len(self.headerdict['PROJECTID']) > 0:
                out = True
            else:
                out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft projectid nummer
    def get_projectid_Number(self):
        if 'PROJECTID' in self.headerdict:
            if len(self.headerdict['PROJECTID']) > 1:
                out = self.headerdict['PROJECTID'][1]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #REPORTCODE aanwezig
    def get_reportcode_flag(self):
        if 'REPORTCODE' in self.headerdict:
            if len(self.headerdict['REPORTCODE']) > 0:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft reportcode code
    def get_reportcode_Code(self):
        if 'REPORTCODE' in self.headerdict:
            if len(self.headerdict['REPORTCODE']) > 0:
                out = self.headerdict['REPORTCODE'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #STARTDATE aanwezig
    def get_startdate_flag(self):
        if 'STARTDATE' in self.headerdict:
            if len(self.headerdict['STARTDATE']) > 2:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft startdate jaar (yyyy)
    def get_startdate_Yyyy(self):
        if 'STARTDATE' in self.headerdict:
            if len(self.headerdict['STARTDATE']) > 2:
                out = int(self.headerdict['STARTDATE'][0])
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft startdate maand (mm)
    def get_startdate_Mm(self):
        if 'STARTDATE' in self.headerdict:
            if len(self.headerdict['STARTDATE']) > 2:
                out = int(self.headerdict['STARTDATE'][1])
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft startdate dag (dd)
    def get_startdate_Dd(self):
        if 'STARTDATE' in self.headerdict:
            if len(self.headerdict['STARTDATE']) > 2:
                out = int(self.headerdict['STARTDATE'][2])
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #XYID aanwezig
    def get_xyid_flag(self):
        if 'XYID' in self.headerdict:
            if len(self.headerdict['XYID']) > 2:
                out = True
            else:
                out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft X coordinaat
    def get_xyid_X(self):
        if 'XYID' in self.headerdict:
            if len(self.headerdict['XYID']) > 0:
                out = self.headerdict['XYID'][1]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft Y coordinaat
    def get_xyid_Y(self):
        if 'XYID' in self.headerdict:
            if len(self.headerdict['XYID']) > 1:
                out = self.headerdict['XYID'][2]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Of #ZID aanwezig
    def get_zid_flag(self):
        if 'ZID' in self.headerdict:
            if len(self.headerdict['ZID']) > 0:
                out = True
            else:
                out = False
        else:
            out = False
        try:
            return out
        except:
            return None

    # Purpose: Geeft Z coordinaat
    def get_zid_Z(self):
        if 'ZID' in self.headerdict:
            if len(self.headerdict['ZID']) > 1:
                out = self.headerdict['ZID'][1]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)

    # Purpose: Geeft testid
    def get_testid(self):
        if ('TESTID' in self.headerdict):
            if len(self.headerdict['TESTID']) > 0:
                out = self.headerdict['TESTID'][0]
            else:
                err = 'MissingValue'
        else:
            err = 'MissingKeyword'
        try:
            return out
        except:
            # return None
            return 'Error:%s' % (err)
        
    # Purpose: Initialiseren interne geheugenstructuur
    # niet nodig
    def init_gef(self):
        succes = True

    def qn2column(self, i_iQtyNumber, get_corrected_depth=False):
        """
        Geeft kolom nummer wat correspondeert met gegeven 'quantity number'.
        Geeft de corrected depth wanneer gevraagd en aanwezig bij opvragen quantity number = 1 (penetration depth)
        :param i_iQtyNumber: quantity number volgens GEF definitie
        :param get_corrected_depth: Wanneer TRUE en i_iQtyNumber = 1 word kolom voor quantity number 11 gezocht
        :return: index van waarde in data blok
        """
        try:
            i_iQtyNumber = int(i_iQtyNumber)
            for key, columninfo in self.headerdict['COLUMNINFO'].iteritems():
                if int(columninfo[3]) == i_iQtyNumber:
                    out = key
                if get_corrected_depth and i_iQtyNumber == 1:
                    if int(columninfo[3]) == 11:
                        out = key
            return int(out)
        except:
            # return None
            return 'Error: Quantity Number niet gevonden in GEF file'

    # Purpose: Leest een gegeven Gef bestand en zet alle info in een dictionary
    def read_gef(self, i_sBestandGef):
        EOH = False
        try:
            multipars = ['COLUMNINFO', 'COLUMNVOID', 'MEASUREMENTTEXT', 'MEASUREMENTVAR', 'SPECIMENVAR', 'SPECIMENTEXT']
            self.headerdict = {}
            f = open(i_sBestandGef, 'r')
            tel = 0
            for line in f.readlines():
                line = re.sub('\r\n', '', line)  # haal alle \r\n aan het einde van de regel weg
                linetmp = re.sub('(^[ \t]*)', '', line)  # remove trailing whitespace
                # if not re.sub('^[\ \t]*$','',line)=='': # lege regels uitsluiten. moet dit in test_gef?
                if not re.sub('^[\ \t]{0,}\n', '', linetmp) == '':  # lege regels uitsluiten. moet dit in test_gef?
                    if 1 == 1:  # test1: begint line1 met '#' en komt '=' minstens 1x voor
                        line = linetmp.split('=', 1)
                        par = re.sub('^#([^ \t]*)[ \t]*$', '\\1', line[0])
                        # start test
                        # if par == 'EOH': deel='data'
                        if EOH is False and not re.sub('^[^#].*', '',
                                                       linetmp) == '':  # er komen regels niet begin met # voor.
                            # einde test
                            if len(line) > 1:
                                keyinfo = line[1]
                                keyinfo = re.sub('(^[ \t]*)', '', keyinfo)  # remove trailing whitespace
                                keyinfo = re.sub('([,])([ \t])+', '\\1', re.sub('([ \t])+([,])', '\\2',
                                                                                keyinfo))  # haal eerst alle witruimte (spaties/tabs) rond de separators (',') weg. 15-10-29
                                if keyinfo != '':
                                    # print 'keyinfo: %s'%(keyinfo)
                                    keyinfo = keyinfo.split(',')
                                else:
                                    keyinfo = None
                            else:
                                keyinfo = None
                            b = keyinfo
                            # print 'b: %s'%(b)
                            if par in multipars:  # tabje hoger gezet zodat conditie alleen geldt als een par bestaat. 2015-10-29
                                if is_number(b[0]):
                                    parno = int(b[0]) # Gewijzigd in int voor eenvoudiger keys in dictionaries
                                else:
                                    parno = b[0]
                                # del keyinfo[0]
                                testpar = 'par1'
                                c = []
                                if keyinfo is not None:
                                    for i in b:
                                        e = removetrailers(i)
                                        if is_number(e):
                                            c.append(float(e))
                                        else:
                                            c.append(e)
                                    if par not in self.headerdict:
                                        self.headerdict[par] = {parno: c}
                                    else:
                                        self.headerdict[par][parno] = c
                                else:
                                    parno = None
                        if par == 'EOH':
                            self.headerdict['datablok'] = {}
                            EOH = True
                            self.headerdict[par] = {}
                        if EOH is True and par != 'EOH':
                            tel = tel + 1
                            data = par
                            data = re.sub(';!', '', data)       # einde dataregel. moet hier een test op?
                            data = re.sub("'", "", data)        # remove '
                            data = re.sub('"', '', data)        # remove "
                            data = data.strip()                 # strip front and trailing spaces
                            data = re.split(';|\ |\t|\n', data) # split up the data 
                            a2 = []
                            for i in data:
                                if is_number(i):
                                    a2.append(float(i))
                                else:
                                    a2.append(i)
                            self.headerdict['datablok'][tel] = a2
                        if (par != 'EOH') and (par not in multipars) and (EOH is not True):
                            testpar = 'par2'
                            c = []
                            if b is not None:
                                for i in b:
                                    e = removetrailers(i)
                                    if is_number(e):
                                        c.append(float(e))
                                    else:
                                        c.append(e)
                                self.headerdict[par] = c

            return True

        except IndexError:
            print (
                "%s Headerdict() in UtlGefOpen.py geef IndexError: fout bij uitlezen gef" % os.path.basename(
                    i_sBestandGef))
            return False
    def test_gef(self):
        # test if COLUMN is in the headerdict
        assert 'REPORTCODE' in self.headerdict, 'REPORTCODE not found'

        if 'GEF-BORE-Report' in self.headerdict['REPORTCODE']:
            return
        
        elif 'GEF-CPT-Report' in self.headerdict['REPORTCODE']:
            # standards according to:
            # https://publicwiki.deltares.nl/display/STREAM/GEF-CPT?preview=/102204318/102334492/GEF-CPT.pdf
            
            # *** test presence of key labels: file tracing ***
            assert 'GEFID' in self.headerdict, 'GEFID not found'
            assert 'COMPANYID' in self.headerdict, 'COMPANYID not found'
            assert 'FILEDATE' in self.headerdict, 'FILEDATE not found'
            assert 'FILEOWNER' in self.headerdict, 'FILEOWNER not found'
            assert 'PROJECTID' in self.headerdict, 'PROJECTID not found'
            assert 'TESTID' in self.headerdict, 'TESTID not found'
            assert 'ZID' in self.headerdict, 'ZID not found'
                        
            # *** test presence of key labels: data descriptive ***
            # test if COLUMN is in the headerdict
            assert 'COLUMN' in self.headerdict, 'COLUMN not found'

            # test if COLUMNINFO is in the headerdict
            assert 'COLUMNINFO' in self.headerdict, 'COLUMNINFO not found'

            # test if COLUMN is in the headerdict
            assert 'COLUMNVOID' in self.headerdict, 'COLUMNVOID not found'

            # test if COLUMN is in the headerdict
            assert 'datablok' in self.headerdict, 'datablok not found'

            # *** test internal logic of the data
            # test if there are as many COLUMNINFO's as you would expect from the field COLUMN
            assert self.headerdict['COLUMN'][0]==len(self.headerdict['COLUMNINFO']), 'COLUMNS does not match the number of COLUMNINFO'

            # test if the LASTSCAN value euqals the lenght of the data block
            assert self.headerdict['LASTSCAN'][0]==len(self.headerdict['datablok']), 'LASTSCAN does not match the length of datablok' 
            
            
            return True
        elif 'GEF-Anker-data' in self.headerdict['REPORTCODE']:
            # *** test presence of key labels ***
            # test if COLUMN is in the headerdict
            assert 'COLUMN' in self.headerdict, 'COLUMN not found'

            # test if COLUMNINFO is in the headerdict
            assert 'COLUMNINFO' in self.headerdict, 'COLUMNINFO not found'

            # test if COLUMN is in the headerdict
            assert 'COLUMNVOID' in self.headerdict, 'COLUMNVOID not found'

            # test if COLUMN is in the headerdict
            assert 'datablok' in self.headerdict, 'datablok not found'

            # *** test internal logic of the data
            # test if there are as many COLUMNINFO's as you would expect from the field COLUMN
            assert self.headerdict['COLUMN'][0]==len(self.headerdict['COLUMNINFO']), 'COLUMNS does not match the number of COLUMNINFO'

            # test if the LASTSCAN value euqals the lenght of the data block
            assert self.headerdict['LASTSCAN'][0]==len(self.headerdict['datablok']), 'LASTSCAN does not match the length of datablok' 
            
            return True