"""@package utility
Common utility functions
"""

#==========================================================================
# Copyright (c) 2024 Randal Eike
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of self software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and self permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#==========================================================================

import re

def MultiLineFormat(rawText:str, maxLength:int = 80, padchar:str|None = None)->list:
    """!
    @brief Break the long text string into a list of strings that do not
           exceed the maxLength input parameter

    @param rawText (string) - Long EULA line text
    @param maxLength (integer) - Maximum line length for the EULA text, default = 80
    @param pad (char) - Character to pad the end of the line with or
                        None if no padding is required

    @return list of strings, List of strings broken at the appropriate length
    """

    formattedText = []

    while len(rawText) > maxLength:
        # Find a good breaking point
        currentIndex = maxLength-1
        while (re.match(r'[\s,\.-]',rawText[currentIndex]) is None) and (currentIndex > 0):
            currentIndex -= 1

        if currentIndex == 0:
            # No good break found, just truncate and max length
            formattedText.append(rawText[:maxLength])
            rawText = rawText[maxLength:]
        else:
            # Good break found, truncate to the good location
            # Get the partial text and strip the trailing space if present
            newLine = rawText[:currentIndex]
            newLine.strip()

            # Add the new line to the list
            if padchar is not None:
                formattedText.append(newLine.ljust(maxLength, padchar))
            else:
                formattedText.append(newLine)

            # Strip the preceeding space if present
            while rawText[currentIndex] == ' ':
                currentIndex += 1

            # Get the remaining string
            rawText = rawText[currentIndex:]

    # Strip leading and trailing spaces for the last line
    newLine = rawText.strip()
    if newLine != '':
        # Add the last line to the list
        if padchar is not None:
            formattedText.append(newLine.ljust(maxLength, padchar))
        else:
            formattedText.append(newLine)

    return formattedText
