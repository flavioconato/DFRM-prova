# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DFRMDialog
                                 A QGIS plugin
 DFRM interface
                             -------------------
        begin                : 2019-08-07
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Greg's Lab
        email                : carlo.gregoretti@unipd.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
from qgis.utils import iface
from qgis.PyQt import QtWidgets
from __builtin__ import False

import os, sys, time,  math
from osgeo import gdal, ogr
from osgeo.gdalconst import *



import numpy as np
import fnmatch
import subprocess
#include <QWidget>


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dfrm_dialog_base.ui'))


class DFRMDialog(QtGui.QDialog, FORM_CLASS):
        
    def __init__(self, iface, parent=None):
        """Constructor."""
        
        super(DFRMDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        #self.setupUi(self)
        
        self.iface = iface
        self.setupUi(self)
        #self.iface.mainWindow().setWindowTitle(u'DFRM - Ciao') 
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'icon2.png'))
               
        global Last_dir;
        Last_dir=os.getcwd();
        global validatorNumeric;
        validatorNumeric = QDoubleValidator(0.0, 5000.0, 2); #[0, 5000] with 2 decimals of precision
        validatorNumeric.setNotation(QDoubleValidator.StandardNotation)
        global validatorNumeric2;
        validatorNumeric2 = QDoubleValidator(0.0, 150000.0, 2); #[0, 5000] with 2 decimals of precision
        validatorNumeric2.setNotation(QDoubleValidator.StandardNotation)
        global validatorUnderUnit;
        validatorUnderUnit = QDoubleValidator(0.0, 1.0, 3);  #[0, 1] with 3 decimals of precision
        validatorUnderUnit.setNotation(QDoubleValidator.StandardNotation)
        
        self.lineEditDurataSim.setValidator(validatorNumeric2)       
        #self.lineEditTimestep.setValidator(validatorNumeric)       
        self.lineEditChezy.setValidator(validatorNumeric)       
        self.lineEditTimestepInterno.setValidator(validatorNumeric2)       
        self.lineEditRoutMinDep.setValidator(validatorNumeric)       
        self.lineEditAngMinDep.setValidator(validatorNumeric)       
        self.lineEditCoeffAngMinDep.setValidator(validatorNumeric)       
        self.lineEditEDMinDepth.setValidator(validatorNumeric)
        self.lineEditKE.setValidator(validatorNumeric)       
        self.lineEditKD.setValidator(validatorNumeric)       
        self.lineEditAngLimDep.setValidator(validatorNumeric)   
        self.lineEditAngLimEros.setValidator(validatorNumeric)    
        self.lineEditVLimDep.setValidator(validatorNumeric)       
        self.lineEditVLimEros.setValidator(validatorNumeric)

              
        self.connect(self.toolButtonDEM, SIGNAL("clicked()"), self.hdrFile)
        self.connect(self.toolButtonIdro, SIGNAL("clicked()"),self.idroFile)
        self.connect(self.toolButtonUsosuolo, SIGNAL("clicked()"),self.landuseFile)
        self.connect(self.toolButtonUsosuoloTxt, SIGNAL("clicked()"),self.landuseTxtFile)
        self.connect(self.toolButtonSezioniIO, SIGNAL("clicked()"), self.sezioniIOFile)
        self.connect(self.toolButtonSezioniInterne, SIGNAL("clicked()"),self.sezioniIntFile)
        #self.connect(self.toolButtonSezioniInterne999, SIGNAL("clicked()"),self.sezioniInt999File)
        self.connect(self.radioButtonConc, SIGNAL("clicked()"), self.radioConc)
        self.connect(self.radioButtonDistr, SIGNAL("clicked()"), self.radioDistr)
        self.connect(self.checkBoxInternalSect, SIGNAL("clicked()"), self.checkInternal)
        self.connect(self.radioButtonFondoFisso, SIGNAL("clicked()"), self.radioFisso)
        self.connect(self.radioButtonFondoMobile, SIGNAL("clicked()"), self.radioMobile)
        #self.connect(self.lineEditCourant, SIGNAL("editingFinished()"), self.checkValueCourant)
        self.connect(self.lineEditCMedia, SIGNAL("editingFinished()"), self.checkValueCMean)
        self.connect(self.lineEditCRest, SIGNAL("editingFinished()"), self.checkValueCRest)
        self.connect(self.lineEditKE, SIGNAL("editingFinished()"), self.checkValueKE)
        self.connect(self.lineEditKD, SIGNAL("editingFinished()"), self.checkValueKD)
        self.connect(self.pushButtonSave, SIGNAL("clicked()"), self.salvaFile)
        self.connect(self.pushButtonLoad, SIGNAL("clicked()"), self.caricaFile)
        self.connect(self.pushButtonExe, SIGNAL("clicked()"), self.executeDFRM)
        self.connect(self.pushButtonCancel, SIGNAL("clicked()"), self.exit)
        #self.connect(self.checkBoxFileERR, SIGNAL("clicked()"), self.fileErr)
        
    def hdrFile(self):
#       "Display file dialog for the DEM header file"
#         self.lineHdr.clear()
        global Last_dir;
        
        outName = QFileDialog.getOpenFileName(self,"DFRM DEM hdr file",Last_dir, "Raster file (*.flt *tif *tiff)")
        #Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
        Last_dir=QFileInfo(outName).absolutePath()
        if QGis.QGIS_VERSION_INT < 10900:        
            if not outName.isEmpty():
                self.lineHdr.clear()
                self.lineHdr.insert(outName)
        else:
            if outName:
                self.lineHdr.clear()
                self.lineHdr.insert(outName)
        return outName   
        
    def idroFile(self):
#        "Display file dialog for the hydrograph file"
#         self.lineEditIdro.clear()
        global Last_dir;
        outName = QFileDialog.getOpenFileName(self, "DFRM hydrograph file",Last_dir, "Txt (*.txt)")
        Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
        if QGis.QGIS_VERSION_INT < 10900:        
            if not outName.isEmpty():
                self.lineEditIdro.clear()
                self.lineEditIdro.insert(outName)
        else:
            if outName:
                self.lineEditIdro.clear()
                self.lineEditIdro.insert(outName)    
        return outName
    
    def landuseFile(self):
#        "Display file dialog for the DEM header file"
#         self.lineEditUsosuoloRaster.clear()
        global Last_dir;
        outName = QFileDialog.getOpenFileName(self,"DFRM landuse raster file",Last_dir, "Raster file (*.flt *tif *tiff)")
        Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
        if QGis.QGIS_VERSION_INT < 10900:        
            if not outName.isEmpty():
                self.lineEditUsosuoloRaster.clear()
                self.lineEditUsosuoloRaster.insert(outName)
        else:
            if outName:
                self.lineEditUsosuoloRaster.clear()
                self.lineEditUsosuoloRaster.insert(outName)    
        return outName   
        
    def landuseTxtFile(self):
#         "Display file dialog for the hydrograph file"
#         self.lineEditUsosuolo.clear()
        global Last_dir;
        outName = QFileDialog.getOpenFileName(self, "DFRM landuse characteristics file",Last_dir, "Txt (*.txt)")
        Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
        if QGis.QGIS_VERSION_INT < 10900:        
            if not outName.isEmpty():
                self.lineEditUsosuolo.clear()
                self.lineEditUsosuolo.insert(outName)
        else:
            if outName:
                self.lineEditUsosuolo.clear()
                self.lineEditUsosuolo.insert(outName)    
        return outName

    def sezioniIOFile(self):
#        "Display file dialog for the DEM header file"
#         self.lineEditSezioniIO.clear()
        global Last_dir;
        outName = QFileDialog.getOpenFileName(self,"DFRM in-Out sections raster file",Last_dir, "Raster file (*.flt *tif *tiff)")
        Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
        if QGis.QGIS_VERSION_INT < 10900:        
            if not outName.isEmpty():
                self.lineEditSezioniIO.clear()
                self.lineEditSezioniIO.insert(outName)
        else:
            if outName:
                self.lineEditSezioniIO.clear()
                self.lineEditSezioniIO.insert(outName)    
        return outName 
    
    def sezioniIntFile(self):
#        "Display file dialog for the DEM header file"
#         self.lineEditSezioniInterne.clear()
        global Last_dir;
        outName = QFileDialog.getOpenFileName(self,"DFRM Internal sections raster file",Last_dir, "Raster file (*.flt *tif *tiff)")
        Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
        if QGis.QGIS_VERSION_INT < 10900:        
            if not outName.isEmpty():
                self.lineEditSezioniInterne.clear()
                self.lineEditSezioniInterne.insert(outName)
        else:
            if outName:
                self.lineEditSezioniInterne.clear()
                self.lineEditSezioniInterne.insert(outName)    
        return outName              

    def radioConc(self): 
        if self.lineEditChezy.isEnabled() == False:
            self.lineEditChezy.setEnabled(True)
            self.labelChezy.setEnabled(True)
            self.labelUsosuolo.setEnabled(False)
            self.labelUsosuoloTxt.setEnabled(False)
            self.lineEditUsosuoloRaster.clear()
            self.lineEditUsosuolo.clear()
            self.lineEditUsosuoloRaster.setEnabled(False)
            self.lineEditUsosuolo.setEnabled(False)
            self.toolButtonUsosuolo.setEnabled(False)
            self.toolButtonUsosuoloTxt.setEnabled(False)
        if self.radioButtonFondoMobile.isChecked():
                        
#             self.lineEditCoeffAngMinDep.setEnabled(True)
#             self.lineEditAngMinDep.setEnabled(True)  
#             self.labelCoeffAngMinDep.setEnabled(True)
#             self.labelAngMinDep.setEnabled(True)
#             
            self.groupBoxParamConc.setEnabled(True)
            self.labelAngLimEros.setEnabled(True)
            self.labelAngLimDep.setEnabled(True)
            self.labelVLimEros.setEnabled(True)
            self.labelVLimDep.setEnabled(True)
            self.lineEditAngLimEros.setEnabled(True)
            self.lineEditAngLimDep.setEnabled(True)
            self.lineEditVLimEros.setEnabled(True)
            self.lineEditVLimDep.setEnabled(True)

            
                      
        return
    
    def radioDistr(self):
        if self.lineEditChezy.isEnabled() == True:
            self.lineEditChezy.clear()
            self.lineEditChezy.setEnabled(False)
            self.labelChezy.setEnabled(False)
            self.labelUsosuolo.setEnabled(True)
            self.labelUsosuoloTxt.setEnabled(True)
            self.lineEditUsosuoloRaster.clear()
            self.lineEditUsosuolo.clear()
            self.lineEditUsosuoloRaster.setEnabled(True)
            self.lineEditUsosuolo.setEnabled(True)
            self.toolButtonUsosuolo.setEnabled(True)
            self.toolButtonUsosuoloTxt.setEnabled(True)
        if self.radioButtonFondoMobile.isChecked():
            self.lineEditAngLimEros.clear()
            self.lineEditAngLimDep.clear()
            self.lineEditVLimEros.clear()
            self.lineEditVLimDep.clear()
            
            self.groupBoxParamConc.setEnabled(False)
            self.lineEditAngLimEros.setEnabled(False)
            self.lineEditAngLimDep.setEnabled(False)
            self.lineEditVLimEros.setEnabled(False)
            self.lineEditVLimDep.setEnabled(False)  
            self.labelAngLimEros.setEnabled(False)
            self.labelAngLimDep.setEnabled(False)
            self.labelVLimEros.setEnabled(False)
            self.labelVLimDep.setEnabled(False)
            
#             self.lineEditCoeffAngMinDep.setEnabled(False)
#             self.lineEditAngMinDep.setEnabled(False)  
#             self.labelCoeffAngMinDep.setEnabled(False)
#             self.labelAngMinDep.setEnabled(False)
        return
    
    def radioFisso(self):
        if self.lineEditEDMinDepth.isEnabled() == True:
            self.lineEditEDMinDepth.clear()
            self.lineEditCMedia.clear()
            self.lineEditCRest.clear()
            self.lineEditKD.clear()
            self.lineEditKE.clear()
            self.lineEditAngLimEros.clear()
            self.lineEditAngLimDep.clear()
            self.lineEditVLimEros.clear()
            self.lineEditVLimDep.clear()
            self.lineEditCoeffAngMinDep.clear()
            self.lineEditAngMinDep.clear()
            
            self.lineEditEDMinDepth.setEnabled(False)
            self.lineEditCMedia.setEnabled(False)
            self.lineEditCRest.setEnabled(False)
            self.lineEditKD.setEnabled(False)
            self.lineEditKE.setEnabled(False)
            self.lineEditAngLimEros.setEnabled(False)
            self.lineEditAngLimDep.setEnabled(False)
            self.lineEditVLimEros.setEnabled(False)
            self.lineEditVLimDep.setEnabled(False)          
            self.labelEDMinDepth.setEnabled(False)
            self.labelCMedia.setEnabled(False)
            self.labelCRest.setEnabled(False)
            self.labelKD.setEnabled(False)
            self.labelKE.setEnabled(False)
            self.labelAngLimEros.setEnabled(False)
            self.labelAngLimDep.setEnabled(False)
            self.labelVLimEros.setEnabled(False)
            self.labelVLimDep.setEnabled(False)
            self.groupBoxParamConc.setEnabled(False)
            self.lineEditCoeffAngMinDep.setEnabled(False)
            self.lineEditAngMinDep.setEnabled(False)  
            self.labelCoeffAngMinDep.setEnabled(False)
            self.labelAngMinDep.setEnabled(False)
            
        return
    
    def radioMobile(self):
        if self.lineEditEDMinDepth.isEnabled() == False:
            self.lineEditEDMinDepth.clear()
            self.lineEditCMedia.clear()
            self.lineEditCRest.clear()
            self.lineEditKD.clear()
            self.lineEditKE.clear()
            self.lineEditAngLimEros.clear()
            self.lineEditAngLimDep.clear()
            self.lineEditVLimEros.clear()
            self.lineEditVLimDep.clear()
            self.lineEditEDMinDepth.setEnabled(True)
            self.lineEditCMedia.setEnabled(True)
            self.lineEditCRest.setEnabled(True)
            self.lineEditKD.setEnabled(True)
            self.lineEditKE.setEnabled(True)
            self.labelEDMinDepth.setEnabled(True)
            self.labelCMedia.setEnabled(True)
            self.labelCRest.setEnabled(True)
            self.labelKD.setEnabled(True)
            self.labelKE.setEnabled(True)
            self.lineEditCoeffAngMinDep.setEnabled(True)
            self.lineEditAngMinDep.setEnabled(True)  
            self.labelCoeffAngMinDep.setEnabled(True)
            self.labelAngMinDep.setEnabled(True)
            if self.radioButtonConc.isChecked():
                self.groupBoxParamConc.setEnabled(True)
                self.lineEditAngLimEros.setEnabled(True)
                self.lineEditAngLimDep.setEnabled(True)
                self.lineEditVLimEros.setEnabled(True)
                self.lineEditVLimDep.setEnabled(True)  
                self.labelAngLimEros.setEnabled(True)
                self.labelAngLimDep.setEnabled(True)
                self.labelVLimEros.setEnabled(True)
                self.labelVLimDep.setEnabled(True)
            else:
                self.groupBoxParamConc.setEnabled(False)
                self.lineEditAngLimEros.setEnabled(False)
                self.lineEditAngLimDep.setEnabled(False)
                self.lineEditVLimEros.setEnabled(False)
                self.lineEditVLimDep.setEnabled(False)  
                self.labelAngLimEros.setEnabled(False)
                self.labelAngLimDep.setEnabled(False)
                self.labelVLimEros.setEnabled(False)
                self.labelVLimDep.setEnabled(False)
        return
    
    
    def checkInternal(self):
        if self.lineEditTimestepInterno.isEnabled() == True:
            self.lineEditTimestepInterno.clear()
            self.lineEditSezioniInterne.clear()
            #self.lineEditSezioniInterne999.clear()
            self.lineEditTimestepInterno.setEnabled(False)
            #self.lineEditSezioniInterne999.setEnabled(False)
            self.lineEditSezioniInterne.setEnabled(False)
            self.labelTimestepInterno.setEnabled(False)
            #self.labelSezioniInterne999.setEnabled(False)
            self.labelSezioniInterne.setEnabled(False)
            self.toolButtonSezioniInterne.setEnabled(False)
            #self.toolButtonSezioniInterne999.setEnabled(False)

        else:
            self.lineEditTimestepInterno.setEnabled(True)
            #self.lineEditSezioniInterne999.setEnabled(True)
            self.lineEditSezioniInterne.setEnabled(True)
            self.labelTimestepInterno.setEnabled(True)
            #self.labelSezioniInterne999.setEnabled(True)
            self.labelSezioniInterne.setEnabled(True)
            self.toolButtonSezioniInterne.setEnabled(True)
            #self.toolButtonSezioniInterne999.setEnabled(True)
        return
    
    def exit(self):
        self.close()
    
    def executeDFRM(self):
        try:
            file_name=self.salvaFile();

            if not file_name=="":
                file_nameBAT=file_name[:len(file_name)-4]+".bat"
                f=open(file_nameBAT,"w");
                os.chdir(os.path.dirname(__file__))
                f.write("cmd /c start "+os.getcwd()+"/DFRM.exe "+file_name)
                f.close();
                proc1=subprocess.call([file_nameBAT])
                os.remove(file_nameBAT)
                self.exit();
            else:
                
                return False
        except:
            return False
        return True


    def check(self):
        
        try:
            f=open(self.lineHdr.text(),"r");
        except:
            QMessageBox.warning(self.iface.mainWindow(), "DEM", "Controlla il file DEM")
            return False;
        f.close();
        
        try:
            f=open(self.lineEditIdro.text(),"r");
        except:
            QMessageBox.warning(self.iface.mainWindow(), "Idrogrammi", "Controlla il file idrogramma")
            return False;
        f.close();
        try:
            f=open(self.lineEditSezioniIO.text(),"r");
        except:
            QMessageBox.warning(self.iface.mainWindow(), "Sezioni I/O", "Controlla il raster Sezioni Ingresso/uscita")
            return False;
        f.close();
        
        state=validatorNumeric2.validate(self.lineEditDurataSim.text(), 0)
        if not state[0]== QtGui.QValidator.Acceptable:
            QMessageBox.warning(self.iface.mainWindow(), "Durata Simulazione", "Controlla la durata della simulazione")
            return False;
        
#         state=validatorNumeric.validate(self.lineEditTimestep.text(), 0)
#         if not state[0]== QtGui.QValidator.Acceptable:
#             QMessageBox.warning(self.iface.mainWindow(), "Time Step", "Controlla il time step di output")
#             return False;
        
        if self.radioButtonDistr.isChecked():
            try:
                f=open(self.lineEditUsosuoloRaster.text(),"r");
            except:
                QMessageBox.warning(self.iface.mainWindow(), "Uso Suolo", "Controlla il raster Uso Suolo")
                return False;
            f.close();
            
            try:
                f=open(self.lineEditUsosuolo.text(),"r");
            except:
                QMessageBox.warning(self.iface.mainWindow(), "Parametri dell'uso suolo", "Controlla il file parametri dell'uso suolo")
                return False;
            f.close();
        else:
            state=validatorNumeric.validate(self.lineEditChezy.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Conduttanza", "Controlla il coefficiente di conduttanza")
                return False;
        
        if self.checkBoxInternalSect.isChecked():
            try:
                f=open(self.lineEditSezioniInterne.text(),"r");
            except:
                QMessageBox.warning(self.iface.mainWindow(), "Sezioni Interne", "Controlla il raster Sezioni Interne")
                return False;
            f.close();
            
#             try:
#                 f=open(self.lineEditSezioniInterne999.text(),"r");
#             except:
#                 QMessageBox.warning(self.iface.mainWindow(), "Sezioni Interne di valle", "Controlla il raster Sezioni Interne di valle")
#                 return False;
#             f.close();
            
            state=validatorNumeric2.validate(self.lineEditTimestepInterno.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Time Step sezioni interne", "Controlla il time step interno di output")
                return False;
            
            if float(self.lineEditTimestepInterno.text())>=float(self.lineEditDurataSim.text()):
                QMessageBox.warning(self.iface.mainWindow(), "Time Step sezioni interne", "Il time step interno di output non puo` essere superiore alla durata della simulazione")
                return False;
            
        state=validatorNumeric.validate(self.lineEditRoutMinDep.text(), 0)
        if not state[0]== QtGui.QValidator.Acceptable:
            QMessageBox.warning(self.iface.mainWindow(), "Profondita` minima di propagazione", "Controlla il valore di profondita` minima di propagazione")
            return False;
                       
        if self.radioButtonFondoMobile.isChecked():
            state=validatorUnderUnit.validate(self.lineEditCMedia.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Concentrazione media", "Controlla il valore della concentrazione solida media")
                return False;
            state=validatorUnderUnit.validate(self.lineEditCRest.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Concentrazione di riposo", "Controlla il valore della concentrazione solida di riposo")
                return False;
            state=validatorNumeric.validate(self.lineEditEDMinDepth.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Profondita` minima per Erosione/Deposito", "Controlla il valore di profondita` minima per Erosione/Deposito")
                return False;
            if float(self.lineEditEDMinDepth.text())<float(self.lineEditRoutMinDep.text()):
                QMessageBox.warning(self.iface.mainWindow(), "Profondita` minima per Erosione/Deposito", "Il valore di profondita` minima per Erosione/Deposito non puo` essere inferiore al valore di profondita` minima per la propagazione")
                return False;
            state=validatorNumeric.validate(self.lineEditKE.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Coefficiente KE", "Controlla il Coefficiente KE")
                return False;
            state=validatorNumeric.validate(self.lineEditKD.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Coefficiente KD", "Controlla il Coefficiente KD")
                return False;
            state=validatorNumeric.validate(self.lineEditAngMinDep.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Angolo limite per deposito agevolato", "Controlla l'angolo limite per deposito agevolato")
                return False;
            state=validatorNumeric.validate(self.lineEditCoeffAngMinDep.text(), 0)
            if not state[0]== QtGui.QValidator.Acceptable:
                QMessageBox.warning(self.iface.mainWindow(), "Coefficiente velocita` per deposito agevolato", "Controlla il coefficiente di velocita` limite per deposito agevolato")
                return False;

            
            if self.radioButtonConc.isChecked():
                state=validatorNumeric.validate(self.lineEditAngLimEros.text(), 0)
                if not state[0]== QtGui.QValidator.Acceptable:
                    QMessageBox.warning(self.iface.mainWindow(), "Angolo limite di Erosione", "Controlla l'Angolo limite di Erosione")
                    return False;
                state=validatorNumeric.validate(self.lineEditAngLimDep.text(), 0)
                if not state[0]== QtGui.QValidator.Acceptable:
                    QMessageBox.warning(self.iface.mainWindow(), "Angolo limite di Deposito", "Controlla l'Angolo limite di Deposito")
                    return False;
                state=validatorNumeric.validate(self.lineEditVLimEros.text(), 0)
                if not state[0]== QtGui.QValidator.Acceptable:
                    QMessageBox.warning(self.iface.mainWindow(), "Velocita` limite di Erosione", "Controlla la Velocita` limite di Erosione")
                    return False;
                state=validatorNumeric.validate(self.lineEditVLimDep.text(), 0)
                if not state[0]== QtGui.QValidator.Acceptable:
                    QMessageBox.warning(self.iface.mainWindow(), "Velocita` limite di Deposito", "Controlla la Velocita` limite di Deposito")
                    return False;
            
        return True
    
    def salvaFile(self):
        global Last_dir;
        if self.check():
            try:
                outName = QFileDialog.getSaveFileName(self, "CLM file",Last_dir, "DFRM Command file (*.clm)")
                Last_dir=QFileInfo(outName).absoluteDir().absolutePath()
                f=open(outName,"w");
                
                #TIF o FLT ed eventuale trasformazione
                fileTIF=self.lineHdr.text()
                fileTIF=fileTIF.replace("/","\\")
                estensione=fileTIF[fileTIF.rfind('.')+1:len(fileTIF)]
                if estensione!='flt' and estensione!='hdr':
                    #self.GTiffToFloat(fileTIF[0:fileTIF.rfind('/')], fileTIF[fileTIF.rfind('/')+1:len(fileTIF)])
                    self.GTiffToFloat(fileTIF[0:fileTIF.rfind('\\')], fileTIF[fileTIF.rfind('\\')+1:len(fileTIF)])
                    
                #self.lineHdr.setText(fileTIF[0:fileTIF.rfind('.')]+'.hdr')
                    
                f.write("{0:30s}{1}\n".format("Header File:",fileTIF[0:fileTIF.rfind('.')]+'.hdr')) 
                f.write("{0:30s}{1}\n".format("Input hydrographs file:",self.lineEditIdro.text()))
                if self.radioButtonDistr.isChecked():
                    a=1.0;
                    f.write("{0:35s}{1:10.2f}\n".format("Distribution control flag number:",a))
                    
                    #TIF o FLT ed eventuale trasformazione
                    fileTIF=self.lineEditUsosuoloRaster.text()
                    fileTIF=fileTIF.replace("/","\\")
                    estensione=fileTIF[fileTIF.rfind('.')+1:len(fileTIF)]
                    if estensione!='flt':
                        self.GTiffToFloat(fileTIF[0:fileTIF.rfind('\\')], fileTIF[fileTIF.rfind('\\')+1:len(fileTIF)])
                        self.lineEditUsosuoloRaster.setText(fileTIF[0:fileTIF.rfind('.')]+'.flt')
                    
                    f.write("{0:30s}{1}\n".format("Land Use File:",self.lineEditUsosuoloRaster.text())) 
                    f.write("{0:30s}{1}\n".format("Land Characteristic file:",self.lineEditUsosuolo.text()))
                else:
                    a=2.0;
                    f.write("{0:35s}{1:10.2f}\n".format("Distribution control flag number:",a)) 
                    f.write("{0:35s}{1:10.2f}\n".format("Chezy coefficient:",float(self.lineEditChezy.text())))
                    
                if self.checkBoxInternalSect.isChecked():    
                    f.write("{0:35s}{1:10.1f}\n".format("Internal Output (1):",1.0))
                    
                    #TIF o FLT ed eventuale trasformazione
                    fileTIF=self.lineEditSezioniInterne.text()
                    fileTIF=fileTIF.replace("/","\\")
                    estensione=fileTIF[fileTIF.rfind('.')+1:len(fileTIF)]
                    if estensione!='flt':
                        self.GTiffToFloat(fileTIF[0:fileTIF.rfind('\\')], fileTIF[fileTIF.rfind('\\')+1:len(fileTIF)])
                        self.lineEditSezioniInterne.setText(fileTIF[0:fileTIF.rfind('.')]+'.flt')
                    
                    f.write("{0:30s}{1}\n".format("Internal Outputs File:",self.lineEditSezioniInterne.text())) 
                    f.write("{0:30s}{1}\n".format("Second Internal Outputs:",self.lineEditSezioniInterne.text()[:len(self.lineEditSezioniInterne.text())-4]+"_999.flt"))
                    if float(self.lineEditTimestepInterno.text())>15.0:
                        f.write("{0:36s}{1:15.1f}\n".format("Internal Output Time Step (seconds):",float(self.lineEditTimestepInterno.text())))
                    else:
                        f.write("{0:36s}{1:15.1f}\n".format("Internal Output Time Step (seconds):",15.0))                        
                else:
                    f.write("{0:35s}{1:10.1f}\n".format("Internal Output (1):",0.0))
        
                f.write("{0:35s}{1:15.2f}\n".format("Simulation time:",float(self.lineEditDurataSim.text())))
                if self.radioButtonFondoMobile.isChecked():
                    f.write("{0:35s}{1:10.3f}\n".format("Depos. Coeff. for Limit Angle:",float(self.lineEditCoeffAngMinDep.text())))
                    f.write("{0:49s}{1:10.2f}\n".format("Inferior Limit Angle (°) for debris flow routing:",float(self.lineEditAngMinDep.text())))
                else:
                    f.write("{0:35s}{1:10.3f}\n".format("Depos. Coeff. for Limit Angle:",5.0))
                    f.write("{0:49s}{1:10.2f}\n".format("Inferior Limit Angle (°) for debris flow routing:",5.0))

                f.write("{0:35s}{1:10.3f}\n".format("Courant number:",0.95))
                f.write("{0:35s}{1:10.5f}\n".format("Minimum Flow Depth for Routing (m):",float(self.lineEditRoutMinDep.text())))
                if self.radioButtonFondoMobile.isChecked():
                    f.write("{0:35s}{1:10.2f}\n".format("Erosion flag number:",1.0))
                    if a==2.0:
                        f.write("{0:35s}{1:10.3f}\n".format("Erosion inferior velocity (m/s):",float(self.lineEditVLimEros.text())))
                        f.write("{0:35s}{1:10.3f}\n".format("Erosion inferior angle (°):",float(self.lineEditAngLimEros.text())))
                        f.write("{0:35s}{1:10.4f}\n".format("Superior deposit velocity (m/s):",float(self.lineEditVLimDep.text())))
                        f.write("{0:35s}{1:10.5f}\n".format("Superior deposit angle (°):",float(self.lineEditAngLimDep.text())))
                    f.write("{0:34s}{1:10.2f}\n".format("Egashira erosion coefficient:",float(self.lineEditKE.text())))
                    f.write("{0:34s}{1:10.2f}\n".format("Egashira deposition coefficient:",float(self.lineEditKD.text())))
                    f.write("{0:35s}{1:10.5f}\n".format("Minimum Flow Depth for Eros/Dep(m):",float(self.lineEditEDMinDepth.text())))
                    f.write("{0:35s}{1:10.3f}\n".format("Mean solid concentration:",float(self.lineEditCMedia.text())))
                    f.write("{0:35s}{1:10.3f}\n".format("Rest solid concentration:",float(self.lineEditCRest.text())))
                
                else:
                    f.write("{0:35s}{1:10.2f}\n".format("Erosion flag number:",2.0))
                
                f.write("{0:33s}{1:10.3f}\n".format("Output time step (seconds):",float(self.lineEditDurataSim.text())/2.))
                
                #TIF o FLT ed eventuale trasformazione
                fileTIF=self.lineEditSezioniIO.text()
                fileTIF=fileTIF.replace("/","\\")
                estensione=fileTIF[fileTIF.rfind('.')+1:len(fileTIF)]
                if estensione!='flt':
                    self.GTiffToFloat(fileTIF[0:fileTIF.rfind('\\')], fileTIF[fileTIF.rfind('\\')+1:len(fileTIF)])
                    self.lineEditSezioniIO.setText(fileTIF[0:fileTIF.rfind('.')]+'.flt')
                             
                f.write("{0:30s}{1}\n".format("Inlet Outlet condition file:",self.lineEditSezioniIO.text()))
                f.write("{0:30s}{1}\n".format("Error file:",int(self.checkBoxFileERR.isChecked())))
                
                f.close()
            except:
                return ""
        else:
            return ""
         
        return outName
        

    def caricaFile(self):
        global Last_dir;
        try:
            fileName = QFileDialog.getOpenFileName(self, "CLM file",Last_dir, "DFRM Command file (*.clm)")
            Last_dir=QFileInfo(fileName).absoluteDir().absolutePath()
            f=open(fileName,"r");
            stringa=f.readline()
            self.lineHdr.setText(stringa[30:stringa.rfind('.')]+'.flt')
            stringa=f.readline()
            self.lineEditIdro.setText(stringa[30:len(stringa)-1])
            stringa=f.readline()
            if float(stringa[35:])==1:
                self.radioButtonDistr.click();
                stringa=f.readline()
                self.lineEditUsosuoloRaster.setText(stringa[30:len(stringa)-1])
                stringa=f.readline()
                self.lineEditUsosuolo.setText(stringa[30:len(stringa)-1])
            else:   
                self.radioButtonConc.click();
                self.lineEditChezy.setText(str(float(f.readline()[35:])))
            
            stringa=f.readline()
            if float(stringa[35:])==1:
                if not self.checkBoxInternalSect.isChecked():
                    self.checkBoxInternalSect.click()
                    
                stringa=f.readline()
                self.lineEditSezioniInterne.setText(stringa[30:len(stringa)-1])
                stringa=f.readline()
                #self.lineEditSezioniInterne999.setText(stringa[30:len(stringa)-1])        
                self.lineEditTimestepInterno.setText(str(float(f.readline()[36:])))
            else:
                if self.checkBoxInternalSect.isChecked():
                    self.checkBoxInternalSect.click()
                
            
            self.lineEditDurataSim.setText(str(float(f.readline()[35:])))
            
            b=f.readline()[35:]
            a=f.readline()[50:]

            f.readline()
            #self.lineEditCourant.setText(str(float(f.readline()[35:])))
            self.lineEditRoutMinDep.setText(str(float(f.readline()[35:])))
            stringa=f.readline()
            if float(stringa[35:])==1:
                self.radioButtonFondoMobile.click();
                if self.radioButtonConc.isChecked():
                    self.lineEditVLimEros.setText(str(float(f.readline()[35:])))
                    self.lineEditAngLimEros.setText(str(float(f.readline()[35:])))
                    self.lineEditVLimDep.setText(str(float(f.readline()[35:])))
                    self.lineEditAngLimDep.setText(str(float(f.readline()[35:])))
                self.lineEditKE.setText(str(float(f.readline()[34:])))
                self.lineEditKD.setText(str(float(f.readline()[34:])))
                self.lineEditEDMinDepth.setText(str(float(f.readline()[35:])))
                self.lineEditCMedia.setText(str(float(f.readline()[35:])))
                self.lineEditCRest.setText(str(float(f.readline()[35:])))
                self.lineEditCoeffAngMinDep.setText(str(float(b)))
                self.lineEditAngMinDep.setText(str(float(a)))
            else:
                self.radioButtonFondoFisso.click();
            f.readline()[34:]
            #self.lineEditTimestep.setText(str(float(f.readline()[34:])))
            stringa=f.readline()
            self.lineEditSezioniIO.setText(stringa[30:len(stringa)-1])
            try:
                stringa=f.readline()
                if int(stringa[30:])==0:
                    if self.checkBoxFileERR.isChecked():
                        self.checkBoxFileERR.click()
                else:
                    if not self.checkBoxFileERR.isChecked():
                        self.checkBoxFileERR.click()
            
            except:
                if not self.checkBoxFileERR.isChecked():
                    self.checkBoxFileERR.click()
            f.close()
        except:
            return False
        return True


    def checkValueCMean(self):
        state=validatorUnderUnit.validate(self.lineEditCMedia.text(), 0);
  
        if  not state[0] == QtGui.QValidator.Acceptable:
            QMessageBox.warning(self.iface.mainWindow(), "Attenzione",("Il valore del parametro deve variare tra 0 e 1"))
            self.lineEditCMedia.clear();
            return False
        else:
            return True
        
    def checkValueCRest(self):
        state=validatorUnderUnit.validate(self.lineEditCRest.text(), 0);
  
        if  not state[0] == QtGui.QValidator.Acceptable:
            QMessageBox.warning(self.iface.mainWindow(), "Attenzione",("Il valore del parametro deve variare tra 0 e 1"))
            self.lineEditCRest.clear();
            return False
        else:
            return True
        
        
    def checkValueKE(self):
        state=validatorUnderUnit.validate(self.lineEditKE.text(), 0);
  
        if  not state[0] == QtGui.QValidator.Acceptable:
            QMessageBox.warning(self.iface.mainWindow(), "Attenzione",("Il valore del parametro deve variare tra 0 e 1"))
            self.lineEditKE.clear();
            return False
        else:
            return True
    
    def GTiffToFloat(self,directoryPath, GTiff):
        os.chdir(directoryPath)
        inDs=gdal.Open(GTiff)
        if inDs is None:
            raise RuntimeError("Unable to open the input raster dataset")
        inBand = inDs.GetRasterBand(1)
        noDataValue=inBand.GetNoDataValue()
        driver = gdal.GetDriverByName("EHdr")
        nomeFile = GTiff[0:GTiff.rfind('.')]
        outDs=driver.Create(nomeFile+".flt",inBand.XSize,inBand.YSize,1,gdal.GDT_Float32)#inBand.DataType)
        outDs.SetProjection(inDs.GetProjection())
        outDs.SetGeoTransform(inDs.GetGeoTransform())
        outBand=outDs.GetRasterBand(1)
        inData=inBand.ReadAsArray()
        condizione=inData==np.float32(noDataValue)
        inData=np.where(condizione,-9999.0,inData)
        outBand.WriteArray(inData)
        outBand.SetNoDataValue(-9999.0)
        outBand.FlushCache()
        outBand.ComputeBandStats(False)
        header="ncols {}\n".format(outBand.XSize)
        header+="nrows {}\n".format(outBand.YSize)
        header+="xllcorner {}\n".format(outDs.GetGeoTransform()[0])
        header+="yllcorner {}\n".format(outDs.GetGeoTransform()[3]-(outBand.YSize*outDs.GetGeoTransform()[1]))
        header+="cellsize {}\n".format(outDs.GetGeoTransform()[1])
        header+="NODATA_value -9999.0\n"
        header+="byteorder LSBFIRST"
        del outBand
        del outDs
        with open(nomeFile+".hdr","w") as headerFile:
            headerFile.write(header)
        return
        
    def checkValueKD(self):
        state=validatorUnderUnit.validate(self.lineEditKD.text(), 0);
  
        if  not state[0] == QtGui.QValidator.Acceptable:
            QMessageBox.warning(self.iface.mainWindow(), "Attenzione",("Il valore del parametro deve variare tra 0 e 1"))
            self.lineEditKD.clear();
            return False
        else:
            return True