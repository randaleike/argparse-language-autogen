"""@package argparselangautogen
Utility to automatically generate language strings using google translate api
for the argparse libraries
"""

#==========================================================================
# Copyright (c) 2025 Randal Eike
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

class StringClassNameGen(object):
    projectNameSpace = "argparser"

    """!
    @brief Helper static class for generating consistent ParserStringInterface names across multiple files
    """
    def __init__(self):
        pass

    @staticmethod
    def getNamespaceName():
        """!
        @brief Return the project namespace name
        @return string Project namespace name
        """
        return StringClassNameGen.projectNameSpace

    @staticmethod
    def getBaseClassName():
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        return "ParserStringListInterface"

    @staticmethod
    def getLangClassName(languageName:str|None)->str:
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        if languageName is None:
            return StringClassNameGen.getBaseClassName()
        else:
            return StringClassNameGen.getBaseClassName()+languageName.capitalize()

    @staticmethod
    def getParserStringType():
        return "parserstr"

    @staticmethod
    def getParserCharType():
        return "parserchar"

    @staticmethod
    def getParserStrStreamType():
        return "parser_str_stream"

    @staticmethod
    def getDynamicCompileswitch():
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        return "DYNAMIC_INTERNATIONALIZATION"
