# -*- coding: utf-8 -*-

"""
***************************************************************************
    PolynominalTransformationProcessing.py
    ----------------------------------
    Date                 : January 2022
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

__author__ = 'Adrian Weber'
__date__ = 'January 2022'
__copyright__ = '(C) 2022, Adrian Weber'


from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsWkbTypes)
from qgis import processing


class PolynominalTransformationProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm georeferences vector layers using a polynominal
    transformation provided by GDAL/OGR. The polynominal order is selected based
    on the number of control points, but at least four control points are
    required.
    
    The reference layer is a (Multi-)LineString layer that connects the control
    points from the start system with the control points in the destination
    system. The line direction is always from the start system to the
    destination system.
    
    The layer to transform can be of any geometry type.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    REF_INPUT = 'REF_INPUT'
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
         return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PolynominalTransformationProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'vectorpolynominaltransformation'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Polynominal Transformation')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Vector georeferencing')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'vectorgeoreferencing'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        msg = self.tr("""This algorithm georeferences vector layers using a polynominal transformation provided by GDAL/OGR. The polynominal order is selected based on the number of control points, but at least four control points are required.
        The reference layer is a (Multi-)LineString layer that connects the control points from the start system with the control points in the destination system. The line direction is always from the start system to the destination system.
        The layer to transform can be of any geometry type.""")
        
        return msg

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The reference vector layer must be of type (Multi-)LineString
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.REF_INPUT,
                self.tr('Reference layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        # The layer to transform can be of any type
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Layer to transform'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Transformed layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature sources.
        s = self.parameterAsSource(parameters,
                                   self.REF_INPUT,
                                   context)
        
        sl = self.parameterAsVectorLayer(parameters,
                                         self.INPUT,
                                         context)

        if feedback.isCanceled():
            return {}

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if s is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.REF_INPUT))
        
        # The reference layer must contain at least four ground control points
        if s.featureCount() < 4:
            msg = self.tr("A reference layer requires at least four ground control points.")
            raise QgsProcessingException(msg)
        
        # Check also the layer source to transform
        if sl is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        if feedback.isCanceled():
            return {}
        feedback.setProgressText(self.tr("Read ground control points"))
        
        # Init an empty string to fill in the options
        options = ""
        
        # Loop over all features,
        for f in s.getFeatures():
            # check the geometry type
            if f.geometry().wkbType() == QgsWkbTypes.LineString:
                line = f.geometry().asPolyline()
            elif f.geometry().wkbType() == QgsWkbTypes.MultiLineString:
                line = f.geometry().asMultiPolyline()[0]
            # and write the OGR option in the form documented on
            # https://gdal.org/programs/ogr2ogr.html
            options += "-gcp "
            options += str(line[0].x()) + " " + str(line[0].y()) + " "
            options += str(line[-1].x()) + " " + str(line[-1].y()) + " "
            
        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Transform the vector layer")

        # Run the existing GDAL/OGR vector conversion processing algorithm
        ogr_result = processing.run("gdal:convertformat", {
                'INPUT': parameters['INPUT'],
                'OPTIONS': options,
                'OUTPUT': parameters['OUTPUT']
            },
            is_child_algorithm=True,
            context=context,
            feedback=feedback)

        if feedback.isCanceled():
            return {}

        # Return the results of the algorithm.
        return {'OUTPUT': ogr_result['OUTPUT']}
