# -*- coding: utf-8 -*-

"""
***************************************************************************
    UnzipArchiveProcessing.py
    ----------------------------------
    Date                 : December 2022
    Copyright            : (C) 2022 by Adrian Weber
    Email                : aweber at qgis dot ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import (QCoreApplication,
                              QDir,
                              QFile)
from qgis.core import (QgsProcessing,
                       QgsProcessingOutputString,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFolderDestination,
                       QgsZipUtils)


class UnzipArchiveProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm unzip a ZIP archive and stores the uncompressed
    files to a specified directory.

    It has been developped to use in combination with the download
    file processing algorithm.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return UnzipArchiveProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'unziparchive'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Unzip archive')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('File tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'filetools'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Unzip a ZIP archive to specified destination folder.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The ZIP archive to extract
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('Input ZIP Archive'),
                extension='zip'
            )
        )
        
        # The destination folder where the archive is extracted to
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Output directory')
            )
        )
        
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsFile(
            parameters,
            self.INPUT,
            context
        )
        
        dest = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT_FOLDER,
            context
        )
        
        if feedback.isCanceled():
            return {}
        
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Check if the input ZIP archive exists
        if not QFile.exists(source):
            raise QgsProcessingException(self.tr('Input is not a valid ZIP archive'))
        
        # Check if the output folder exists
        if not QDir(dest).exists():
            raise QgsProcessingException(self.tr('Output folder does not exist'))
        
        feedback.setProgressText(self.tr('Start extraction'))
        
        # Extract the ZIP archive
        (success, fileList) = QgsZipUtils.unzip(source, dest)
        
        # Return the results of the algorithm if the extraction was successful.
        # A list of extracted files and the output folder is returned.
        if not success:
            raise QgsProcessingException(self.tr('Archive extraction failed'))
            
        return { self.OUTPUT_FOLDER: dest,
                 self.OUTPUT: fileList }
