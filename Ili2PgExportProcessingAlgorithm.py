"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterProviderConnection,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFeatureSink,
                       QgsSettings)
from qgis import processing
from QgisModelBaker.libs.modelbaker.iliwrapper import iliexporter
from QgisModelBaker.libs.modelbaker.iliwrapper.globals import DbIliMode
from QgisModelBaker.libs.modelbaker.iliwrapper.ili2dbconfig import ExportConfiguration


class Ili2PgExportProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    DBSCHEMA = 'DBSCHEMA'
    ILIMODELS = 'ILIMODELS'
    XTFFILE = 'XTFFILE'
    VALID = 'VALID'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Ili2PgExportProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'ili2pgexport'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('ili2pg Export')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('QgisModelBaker')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'qgismodelbaker'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Export a database schema against an INTERLIS model using ili2pg.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterProviderConnection(
                self.INPUT,
                self.tr('Database connection'),
                'postgres'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DBSCHEMA,
                self.tr('Database schema')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.ILIMODELS,
                self.tr('INTERLIS models')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.XTFFILE,
                self.tr('Output XTF File')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the database connection
        dbConnection = self.parameterAsConnectionName(
            parameters,
            self.INPUT,
            context
        )
        
        dbSchema = self.parameterAsString(
           parameters,
            self.DBSCHEMA,
            context
        )
        
        iliModels = self.parameterAsString(
            parameters,
            self.ILIMODELS,
            context
        )
        
        xtfFile = self.parameterAsFile(
            parameters,
            self.XTFFILE,
            context
        )

        s = QgsSettings()
        config = ExportConfiguration()
        config.dbhost = s.value("/PostgreSQL/connections/%s/host" % dbConnection)
        config.dbport = s.value("/PostgreSQL/connections/%s/port" % dbConnection)
        config.dbusr = s.value("/PostgreSQL/connections/%s/username" % dbConnection)
        config.dbpwd = s.value("/PostgreSQL/connections/%s/password" % dbConnection)
        config.database = s.value("/PostgreSQL/connections/%s/database" % dbConnection)
        config.dbschema = dbSchema
        config.ilimodels = iliModels
        config.xtffile = xtfFile
        feedback.pushInfo(os.path.splitext(xtfFile)[0])
        config.logfile_path = "%s.log" % os.path.splitext(xtfFile)[0]
        
        exporter = iliexporter.Exporter()
        exporter.tool = DbIliMode.ili2pg
        exporter.configuration = config

        def _exporter_stdout(txt):
            feedback.pushInfo(txt)        

        def _exporter_stderr(txt):
            feedback.pushInfo(txt)
            
        def _proc_finished(exitCode, c):
            if exitCode == iliexporter.Exporter.SUCCESS:
                feedback.pushInfo("...export done")
                return {'VALID': True}
            else:
                # How to properly cancel a processing algorithm?
                feedback.reportError("...export failed")
                return {}
  
        exporter.stdout.connect(_exporter_stdout)
        exporter.stderr.connect(_exporter_stderr)
        exporter.process_finished.connect(_proc_finished)

        res = exporter.run(None)

        return {}
