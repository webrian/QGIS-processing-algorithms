# -*- coding: utf-8 -*-

"""
***************************************************************************
    HelmertTransformationProcessing.py
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
                       QgsProcessingParameterFileDestination,
                       QgsWkbTypes)
from qgis import processing
import numpy as np

class HelmertTransformationProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This algorithm georeferences vector using a 4-parameter helmert
    transformation. At least four control points are required. The parameters
    are estimated using the least square method.
    
    The reference layer is a (Multi-)LineString layer that connects the control
    points from the start system with the control points in the destination
    system. The line direction is always from the start system to the
    destination system.
    
    The layer to transform can be of any geometry type.
    
    The residuals are reported in the log to review the control points used.
    Large absolute values of residuals indicate gross errors or show that this 
    transformation does not fit the distortions in the start system.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    REF_INPUT = 'REF_INPUT'
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    OUTPUT_HTML_FILE = 'OUTPUT_HTML_FILE'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return HelmertTransformationProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'vectorhelmerttransformation'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Helmert Transformation')

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
        msg = self.tr("""This algorithm georeferences vector using a 4-parameter helmert transformation. At least four control points are required. The parameters are estimated using the least square method.
        The reference layer is a (Multi-)LineString layer that connects the control points from the start system with the control points in the destination system. The line direction is always from the start system to the destination system.
        The layer to transform can be of any geometry type.
        The residuals are reported in the log to review the control points used. Large absolute values of residuals indicate gross errors or show that this transformation does not fit the distortions in the start system.""")
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
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_HTML_FILE,
                self.tr('Transformation report'),
                self.tr('HTML files (*.html)'),
                None,
                True
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

        # Init two empty arrays
        source = []
        dest = []

         # Loop over all features,
        for f in s.getFeatures():
            # check the geometry type,
            if f.geometry().wkbType() == QgsWkbTypes.LineString:
                line = f.geometry().asPolyline()
            elif f.geometry().wkbType() == QgsWkbTypes.MultiLineString:
                line = f.geometry().asMultiPolyline()[0]
            # write the coordinates from the start system in an array,
            source.append([line[0].x(), line[0].y()])
            # and write the coordinates from the destination systen in another array
            dest.append([line[-1].x(), line[-1].y()])
            
        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Calculate centroids")
        
        # The formulas strictly follow a lecture notes of the University of
        # Applied Sciences and Arts Northwestern Switzerland from 2012. The 
        # parameters are estimated using linear algebra formulas. The four
        # unknown parameters of the transformation are estimated by the least-squares 
        # method. To improve the stability of the numerical calculations, the
        # control points are reduced to the centroid in their system.

        # Init numpy arrays from the Pyhton lists
        source = np.array(source)
        dest = np.array(dest)
        # Calculate the centroid of the control points in the start system
        xs = np.sum(source[:,:1]) / (source.size/2)
        ys = np.sum(source[:,1:2]) / (source.size/2)
        msg = "Centroid start system:\n" + str(xs) + ", " + str(ys)
        feedback.pushInfo(msg)
        # Reduce the start control points to the centroid
        x_strich = source[:,:1] - xs
        y_strich = source[:,1:] - ys
        # Calculate the centroid of the control points in the destination system
        Xs = np.sum(dest[:,:1]) / (dest.size/2)
        Ys = np.sum(dest[:,1:2]) / (dest.size/2)
        msg = "Centroid destination system:\n" + str(Xs) + ", " + str(Ys)
        feedback.pushInfo(msg)
        # Reduce the destination control points to the centroid
        X_strich = dest[:,:1] - Xs
        Y_strich = dest[:,1:2] - Ys
        msg = str(X_strich) + ", " + str(Y_strich)
        
        # Get the translation in X and Y direction
        dX = Xs - xs
        dY = Ys - ys
        
        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Calculate the least squares")
        
        # Calculate the auxiliary variable D
        D = np.sum(x_strich * x_strich) + np.sum(y_strich * y_strich)

        # Calculate the auxiliary variable a and b
        a = (np.sum(x_strich * X_strich) + np.sum(y_strich * Y_strich)) / D
        b = (np.sum(x_strich * Y_strich) - np.sum(y_strich * X_strich)) / D
        
        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Calculate residuals")

        # Calculate the residuals
        XT = Xs + a * x_strich - b * y_strich
        YT = Ys + b * x_strich + a * y_strich
        Xr = XT - dest[:,:1]
        Yr = YT - dest[:,1:2]
        msg = "Residuals X:\n " + str(Xr)
        feedback.pushInfo(msg)
        msg = "Residuals Y:\n " + str(Yr)
        feedback.pushInfo(msg)

        # Calculate the scale
        m = np.sqrt(a*a + b*b)
        msg = "Scale: " + str(m)
        feedback.pushInfo(msg)
        # Calculate the rotation angle (in radians)
        phi = np.arctan2(b,a)
        # Convert the rotation angle to degrees
        phi_grad = (phi * 180 / np.pi) * (-1)
        msg = "Rotation (degrees): " + str(phi_grad)
        feedback.pushInfo(msg)

        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Translate the layer to the origin")
        
        # Translate the layer to the origin
        zero_result = processing.run("native:translategeometry", {
                'INPUT': parameters['INPUT'],
                'DELTA_X': float(xs) * (-1),
                'DELTA_Y': float(ys) * (-1),
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            },
            is_child_algorithm=True,
            context=context,
            feedback=feedback)

        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Scale and rotate layer")

        # In the origin the scale and rotation are applied
        scale_result = processing.run("native:affinetransform", {
                'INPUT': zero_result['OUTPUT'],
                'SCALE_X': float(m),
                'SCALE_Y': float(m),
                'ROTATION_Z': float(phi_grad) * (-1),
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            },
            is_child_algorithm=True,
            context=context,
            feedback=feedback)

        if feedback.isCanceled():
            return {}
        feedback.setProgressText("Translate the layer to the destination centroid")
        
        results = {}

        # Translate the layer to the centroid of the destination system
        trans_result = processing.run("native:translategeometry", {
                'INPUT': scale_result['OUTPUT'],
                'DELTA_X': float(Xs),
                'DELTA_Y': float(Ys),
                'OUTPUT': parameters['OUTPUT']
            },
            is_child_algorithm=True,
            context=context,
            feedback=feedback)
            
        results[self.OUTPUT] = trans_result['OUTPUT']

        if feedback.isCanceled():
            return {}

        output_file = self.parameterAsFileOutput(parameters,
                                                 self.OUTPUT_HTML_FILE,
                                                 context)

        def createHtmlReport(out_file):
            with open(out_file, 'w') as f:
                f.write('<html><head>')
                f.write('<meta http-equiv="Content-Type" content="text/html; \
                         charset=utf-8" /></head><body>')
                f.write('<h1>' + self.tr('Transformation report') + '</h1>')
                # Write table with translations
                f.write('<h2>' + self.tr('Translation') + '</h2>')
                f.write('<table border="1" width="700px">')
                f.write('<tr><th>dX</th><th>dY</th></tr>')
                f.write('<tr><td>' + "%.4f" % dX + '</td><td>' + "%.4f" % dY + '</td></tr>')
                f.write('</table>')
                # Write table with scale and rotation
                f.write('<h2>' + self.tr('Scale and rotation') + '</h2>')
                f.write('<table border="1" width="700px">')
                f.write('<tr><th>Scale</th><th>Rotation (in degrees)</th></tr>')
                f.write('<tr><td>' + "%.6f" % m + '</td><td>' + "%.6f" % phi_grad + '</td></tr>')
                f.write('</table>')
                # Write table with control points and residuals
                f.write('<h2>' + self.tr('Residuals') + '</h2>')
                f.write('<table border="1" width="700px">')
                f.write('<tr><th>Start X</td><th>Start Y</th><th>Dest X</th><th>Dest Y</th><th>Residuals X</th><th>Residuals Y</th></tr>')
                for i in range(s.featureCount()):
                    f.write('<tr>')
                    for c in [ source[i][0], source[i][1], dest[i][0], dest[i][1]]:
                        f.write("<td>%.4f</td>" % c)
                    for r in [ Xr[i][0], Yr[i][0]]:
                        f.write("<td>%.5f</td>" % r)
                    f.write('</tr>')
                f.write('<table>')
                f.write('</body></html>')
                
            return out_file
                
        if output_file:
            results[self.OUTPUT_HTML_FILE] = createHtmlReport(output_file)

        # Return the results of the algorithm.
        return results
