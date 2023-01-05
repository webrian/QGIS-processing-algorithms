# -*- coding: utf-8 -*-

"""
***************************************************************************
    FtpUploadProcessing.py
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
                              QIODevice,
                              QFile,
                              QFileInfo,
                              QUrl)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (QgsBlockingNetworkRequest,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber)


class FtpUploadProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm takes any file and uploads it to a FTP server
    using plain FTP.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    INPUT = 'INPUT'
    FTP_HOST = 'FTP_HOST'
    FTP_PORT = 'FTP_PORT'
    FTP_USER = 'FTP_USER'
    FTP_PASSWORD = 'FTP_PASSWORD'

    def __init__(self):
        super().__init__()
        self.url = QUrl()

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FtpUploadProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'ftpuploadfile'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('FTP Upload File')

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
        parameters and outputs associated with it.
        """
        msg = self.tr("""Upload a file to a FTP file server using the plain FTP protocol.
        Plain FTP is not secure since the password is sent in plain text!""")
        return msg

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The input file source. It can be any kind of file type.
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('File to upload')
            )
        )

        # The server URL in the form ftp://ftp.yourdomain.com/
        self.addParameter(
            QgsProcessingParameterString(
                self.FTP_HOST,
                self.tr('FTP Host in the form <i>ftp://ftp.yourdomain.com/</i>'),
                defaultValue='ftp://'
            )
        )

        # The FTP port
        self.addParameter(
            QgsProcessingParameterNumber(
                self.FTP_PORT,
                self.tr('FTP Port'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=21,
                minValue=0,
                maxValue=65536
            )
        )

        # The FTP username
        self.addParameter(
            QgsProcessingParameterString(
                self.FTP_USER,
                self.tr('Username')
            )
        )

        # The FTP password
        self.addParameter(
            QgsProcessingParameterString(
                self.FTP_PASSWORD,
                self.tr('Password')
            )
        )

    def onFinished(self):
        if feedback.isCanceled():
            return {}

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the path to the file to upload.
        filepath: str = self.parameterAsFile(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if filepath is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Check if the file exists
        file = QFile(filepath)
        if not file.exists():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Retrieve the FTP host as string
        ftphost: str = self.parameterAsString(
            parameters,
            self.FTP_HOST,
            context
        )

        # Get the correct FTP server port
        ftpport: int = self.parameterAsInt(
            parameters,
            self.FTP_PORT,
            context
        )

        # Get the FTP username
        ftpuser: str = self.parameterAsString(
            parameters,
            self.FTP_USER,
            context
        )

        # Get the FTP password
        ftppassword: str = self.parameterAsString(
            parameters,
            self.FTP_PASSWORD,
            context
        )

        # Define the QUrl with host, port, username and password
        self.url.setUrl(ftphost)
        self.url.setScheme('ftp')
        self.url.setPort(ftpport)
        self.url.setUserName(ftpuser)
        self.url.setPassword(ftppassword)
        self.url.setPath(QFileInfo(file).fileName())
        
        if feedback.isCanceled():
            return {}

        # Try to open the file in read-only mode
        if file.open(QIODevice.ReadOnly):
            # Create a new blocking network request
            req = QgsBlockingNetworkRequest()
            req.finished.connect(self.onFinished)

            # Start the network request
            code = req.put(QNetworkRequest(self.url), file, feedback)
            # Check if upload was successful
            if code != QgsBlockingNetworkRequest.NoError:
                raise QgsProcessingException(req.errorMessage())

        else:
            raise QgsProcessingException(self.tr("File cannot be opened for reading"))

        # Return the result of the algorithm. Since this algorithm does not
        # return anything as a result, just an empty dict is returned. In
        # case the upload failed an exception is thrown.
        return {}
