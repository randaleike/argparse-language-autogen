"""@package eula_tools
Utilities to create formatted End User License Agreement Text blocks
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
# THE SOFTWARE IS PROVIDED "AS IS" \ WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#==========================================================================

import sys
import re
from .text_format import MultiLineFormat

eula = {
       'MIT_open': {'text': ["Permission is hereby granted, free of charge, to any person obtaining a " \
                             "copy of self software and associated documentation files (the \"Software\"), " \
                             "to deal in the Software without restriction, including without limitation " \
                             "the rights to use, copy, modify, merge, publish, distribute, sublicense, " \
                             "and/or sell copies of the Software, and to permit persons to whom the " \
                             "Software is furnished to do so, subject to the following conditions: ",
                             "The above copyright notice and self permission notice shall be included " \
                             "in all copies or substantial portions of the Software. ",
                             "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, " \
                             "EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF " \
                             "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. " \
                             "IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY " \
                             "CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, " \
                             "TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE " \
                             "SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."],
                    'name': "MIT License"},

'MIT_no_atrtrib': {'text': ["Permission is hereby granted, free of charge, to any person obtaining a " \
                            "copy of self software and associated documentation files (the \"Software\"), " \
                            "to deal in the Software without restriction, including without limitation "
                            "the rights to use, copy, modify, merge, publish, distribute, sublicense, " \
                            "and/or sell copies of the Software, and to permit persons to whom the " \
                            "Software is furnished to do so.",
                            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, " \
                            "EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF " \
                            "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. " \
                            "IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY " \
                            "CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, " \
                            "TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE " \
                            "SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."],
                    'name': "MIT No Attribution License"},

       'MIT_X11': {'text': ["Permission is hereby granted, free of charge, to any person obtaining a " \
                            "copy of self software and associated documentation files (the \"Software\"), " \
                            "to deal in the Software without restriction, including without limitation "
                            "the rights to use, copy, modify, merge, publish, distribute, sublicense, " \
                            "and/or sell copies of the Software, and to permit persons to whom the " \
                            "Software is furnished to do so, subject to the following conditions: ",
                            "The above copyright notice and self permission notice shall be included " \
                            "in all copies or substantial portions of the Software. ",
                            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, " \
                            "EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF " \
                            "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. " \
                            "IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY " \
                            "CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, " \
                            "TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE " \
                            "SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",
                            "Except as contained in this notice, the name of <copyright holders> " \
                            "shall not be used in advertising or otherwise to promote the sale, " \
                            "use or other dealings in this Software without prior written "
                            "authorization from <copyright holders>."],
                    'name': "MIT X11 License"},

       'GNU_V11': {'text': ["This program is free software: you can redistribute it and/or modify " \
                            "it under the terms of the GNU General Public License as published by " \
                            "the Free Software Foundation, either version 3 of the License, or " \
                            "(at your option) any later version.",
                            "This program is distributed in the hope that it will be useful, " \
                            "but WITHOUT ANY WARRANTY; without even the implied warranty of " \
                            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the " \
                            "GNU General Public License for more details.",
                            "You should have received a copy of the GNU General Public License " \
                            "along with this program.  If not, see <https://www.gnu.org/licenses/>."],
                    'name': "GNU V11 License"},

   'apache_v2_0': {'text': ["Licensed under the Apache License, Version 2.0 (the \"License\"); " \
                            "you may not use this file except in compliance with the License. " \
                            "You may obtain a copy of the License at ",
                            "    http://www.apache.org/licenses/LICENSE-2.0 ",
                            "Unless required by applicable law or agreed to in writing, software " \
                            "distributed under the License is distributed on an \"AS IS\" BASIS, " \
                            "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. " \
                            "See the License for the specific language governing permissions and " \
                            "limitations under the License."],
                    'name': "Apache V2.0 License"},

   'BSD_3clause': {'text': ["Redistribution and use in source and binary forms, with or " \
                            "without modification, are permitted provided that the following " \
                            "conditions are met:",
                            "1. Redistributions of source code must retain the above " \
                            "copyright notice, this list of conditions and the following " \
                            "disclaimer.",
                            "2. Redistributions in binary form must reproduce the above " \
                            "copyright notice, this list of conditions and the following " \
                            "disclaimer in the documentation and/or other materials provided " \
                            "with the distribution.",
                            "3. Neither the name of the copyright holder nor the names of its " \
                            "contributors may be used to endorse or promote products " \
                            "derived from this software without specific prior written " \
                            "permission.",
                            "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS " \
                            "AND CONTRIBUTORS “AS stringIS” AND ANY EXPRESS OR IMPLIED " \
                            "WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE " \
                            "IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS " \
                            "FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT " \
                            "SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE " \
                            "LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, " \
                            "EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, " \
                            "BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE " \
                            "GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR " \
                            "BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY " \
                            "THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT " \
                            "LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR " \
                            "OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS " \
                            "SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH " \
                            "DAMAGE."],
                    'name': "BSD License"},

   'BSD_2clause': {'text': ["Redistribution and use in source and binary forms, with or " \
                            "without modification, are permitted provided that the following " \
                            "conditions are met:",
                            "1. Redistributions of source code must retain the above " \
                            "copyright notice, this list of conditions and the following " \
                            "disclaimer.",
                            "2. Redistributions in binary form must reproduce the above " \
                            "copyright notice, this list of conditions and the following " \
                            "disclaimer in the documentation and/or other materials provided " \
                            "with the distribution.",
                            "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS " \
                            "AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED " \
                            "WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE " \
                            "IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS " \
                            "FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT " \
                            "SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE " \
                            "LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, " \
                            "EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, " \
                            "BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE " \
                            "GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR " \
                            "BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY " \
                            "THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT " \
                            "LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR " \
                            "OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS " \
                            "SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH " \
                            "DAMAGE."],
                    'name': "BSD License"},
             }

class EulaText(object):
    """!
    EULA text helper class
    """
    def __init__(self, eulaType = None, customEula = None):
        """!
        @breif Constuctor

        @param eulaType (string): MIT_open, MIT_no_atrtrib, MIT_X11,
                                    GNU_V11, apache_v2_0, BSD_3clause
                                    or BSD_2clause
        @param customEula (list of strings): custom EULA string list
        """
        if eulaType is None:
            if customEula is None:
                print("ERROR: Standard or custom EULA is required.")
                sys.exit(1)
            else:
                self.rawEulaText = customEula
                self.eulaName = ""
        else:
            self.rawEulaText = self.getEulaText(eulaType)
            self.eulaName = self.getEulaName(eulaType)

    @staticmethod
    def getEulaText(eulaType):
        """!
        @brief Get the eula string list for the input EULA type.

        @param eulaType (string): MIT_open, MIT_no_atrtrib, MIT_X11,
                                    GNU_V11, apache_v2_0, BSD_3clause
                                    or BSD_2clause
        @return list or None: list of strings for the requested EULA or
                                None if the input eulaType is unknown.
        """
        # pylint: disable=locally-disabled, disable=C0201
        if eulaType in eula.keys():
            return eula[eulaType]['text']
        else:
            return None

    @staticmethod
    def getEulaName(eulaType):
        """!
        @brief Get the eula string list for the input EULA type.

        @param eulaType (string): MIT_open, MIT_no_atrtrib, MIT_X11,
                                    GNU_V11, apache_v2_0, BSD_3clause
                                    or BSD_2clause

        @return list or None: list of strings for the requested EULA or
                                None if the input eulaType is unknown.
        """
        # pylint: disable=locally-disabled, disable=C0201
        if eulaType in eula.keys():
            return eula[eulaType]['name']
        else:
            return None


    @staticmethod
    def _outputLine(lineText, maxLength = 80, pad = False):
        """!
        @brief Format the raw EULA text to the appropriate line length

        @param lineText (string) - EULA line text
        @param maxLength (integer) - Maximum line length for the EULA text, default = 80
        @param pad (boolean) - False: no padding to maxLength,
                            True: pad line with spaces out to maxLength

        @return Formated line of text
        """
        if pad:
            return lineText.ljust(maxLength, ' ')
        else:
            return lineText

    @staticmethod
    def _outputMultiLine(rawText, maxLength = 80, pad = False):
        """!
        @brief Break the long EULA text string into a list of strings that do not
               exceed the maxLength input parameter

        @param rawText (string) - Long EULA line text
        @param maxLength (integer) - Maximum line length for the EULA text, default = 80
        @param pad (boolean) - False: no padding to maxLength,
                               True: pad line with spaces out to maxLength

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
                if pad:
                    formattedText.append(newLine.ljust(maxLength, ' '))
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
            if pad:
                formattedText.append(newLine.ljust(maxLength, ' '))
            else:
                formattedText.append(newLine)

        return formattedText

    def formatEulaName(self, maxLength = 80, pad = False):
        """!
        @brief Format the raw EULA name to the appropriate line length

        @param maxLength (integer) - Maximum line length for the EULA text, default = 80
        @param pad (boolean) - False: no padding to maxLength,
                            True: pad line with spaces out to maxLength

        @return string - formatted name text
        """
        if pad:
            return self.eulaName.ljust(maxLength, ' ')
        else:
            return self.eulaName


    def formatEulaText(self, maxLength = 80, pad = False):
        """!
        @brief Format the raw EULA text to the appropriate line length

        @param maxLength (integer) - Maximum line length for the EULA text, default = 80
        @param pad (boolean) - False: no padding to maxLength,
                            True: pad line with spaces out to maxLength

        @return list of formated eula strings or None if there was a failure
        """
        # Read each line and format it
        formatedEulaText = []
        for rawText in self.rawEulaText:
            if len(rawText) <= maxLength:
                # Single line processing
                formatedEulaText.append(self._outputLine(rawText, maxLength, pad))
            else:
                # Multi line processing
                formatedEulaText.extend(self._outputMultiLine(rawText, maxLength, pad))

            # Append empty line between the EULA text blocks
            formatedEulaText.append(self._outputLine("", maxLength, pad))

        return formatedEulaText
