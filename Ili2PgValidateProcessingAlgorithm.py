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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsDataSourceUri,
                       QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingOutputBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterProviderConnection,
                       QgsProcessingParameterFeatureSink,
                       QgsProviderConnectionException,
                       QgsProviderRegistry
                       )
from qgis import processing
from QgisModelBaker.libs.modelbaker.iliwrapper import ilivalidator
from QgisModelBaker.libs.modelbaker.iliwrapper.globals import DbIliMode
from QgisModelBaker.libs.modelbaker.iliwrapper.ili2dbconfig import ValidateConfiguration


class Ili2PgValidateProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    DBSCHEMA = 'DBSCHEMA'
    ILIMODELS = 'ILIMODELS'
    ISVALID = 'ISVALID'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Ili2PgValidateProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'ili2pgvalidate'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('ili2pg Validate')

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
        return self.tr("Validate a database schema against an INTERLIS model using ili2pg.")

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

        self.addOutput(
            QgsProcessingOutputBoolean(
                self.ISVALID,
                self.tr("is valid")
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
        
        # resolve connection details to uri
        try:
            md = QgsProviderRegistry.instance().providerMetadata('postgres')
            conn = md.createConnection(dbConnection)
        except QgsProviderConnectionException:
            raise QgsProcessingException(self.tr('Could not retrieve connection details for {}').format(dbConnection))
        uri = QgsDataSourceUri(conn.uri())

        config = ValidateConfiguration()
        config.dbhost = uri.host()
        config.dbport = uri.port()
        config.dbusr = uri.username()
        config.dbpwd = uri.password()
        config.database = uri.database()
        config.dbschema = dbSchema
        config.ilimodels = iliModels

        if feedback.isCanceled():
            return {}
        
        validator = ilivalidator.Validator()
        validator.tool = DbIliMode.ili2pg
        validator.configuration = config
        
        def _validator_stderr(txt):
            feedback.pushInfo(txt)
            
        #validator.stdout.connect(_validator_stdout)
        validator.stderr.connect(_validator_stderr)
        #validator.process_finished.connect(_proc_finished)

        if feedback.isCanceled():
            return {}

        res = validator.run(None)
        if res != ilivalidator.Validator.SUCCESS:
            raise QgsProcessingException(self.tr("...validate failed"))

        return { self.ISVALID: True }
