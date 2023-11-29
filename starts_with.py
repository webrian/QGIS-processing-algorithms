from qgis.core import *
from qgis.gui import *

@qgsfunction(args='auto', group='String', referenced_columns=[])
def starts_with(input_string, compare_string, feature, parent):
    """
    Checks if the input string starts with the comparison string
    <h4>Syntax</h4><br/>
    <code>starts_with(input_string, compare_string)</code>

    <h4>Arguments</h4><br/>
    <code>input_string</code> - is string. The string.
    <br>
    <code>compare_string</code> - is string. The string to compare.

    <h4>Example</h4><br/>
    <code>starts_with('Hello World', 'H') -> True</code>
    """
    return str(input_string).startswith(compare_string)
