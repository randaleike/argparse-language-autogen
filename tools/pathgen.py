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

import os
from file_tools.string_name_generator import StringClassNameGen

class FileNameGenerator(object):
    jsonFileDir = "../data"
    outputFileDir = "../output"

    """!
    @brief Helper static class for generating consistent ParserStringInterface names across multiple files
    """
    def __init__(self):
        pass

    @staticmethod
    def getLanguageDescriptionBaseFileName()->str:
        """!
        @brief Get the default language description file name
        @return string Default file name of the language description JSON file
        """
        return StringClassNameGen.getNamespaceName()+"-lang-list.json"

    @staticmethod
    def getLanguageDescriptionFileName(directory = None)->str:
        """!
        @brief Get the default language description file name
        @param directory {path} - Path to the file location
        @return string Default file name and path of the language description JSON file
        """
        if directory is None:
            return os.path.join(FileNameGenerator.jsonFileDir, FileNameGenerator.getLanguageDescriptionBaseFileName())
        else:
            FileNameGenerator.jsonFileDir = directory
            return os.path.join(directory, FileNameGenerator.getLanguageDescriptionBaseFileName())

    @staticmethod
    def getStringClassDescriptionBaseFileName()->str:
        """!
        @brief Get the default string class description file name
        @return string Default file name of the string class description JSON file
        """
        return StringClassNameGen.getNamespaceName()+"-strclass-def.json"

    @staticmethod
    def getStringClassDescriptionFileName(directory = None)->str:
        if directory is None:
            return os.path.join(FileNameGenerator.jsonFileDir, FileNameGenerator.getStringClassDescriptionBaseFileName())
        else:
            FileNameGenerator.jsonFileDir = directory
            return os.path.join(directory, FileNameGenerator.getStringClassDescriptionBaseFileName())

    @staticmethod
    def buildOutputFileName(baseName, ext, subdir = None)->str:
        """!
        @brief Build the output filename
        @param baseName {string} Base file name to build
        @param ext {string} File name extention to build
        @param subdir {string} Subdirectory path
        @return string File name and path/subdir
        """
        fileName = baseName+"."+ext
        if subdir is not None:
            return os.path.join(FileNameGenerator.outputFileDir, subdir, fileName)
        else:
            return os.path.join(FileNameGenerator.outputFileDir, fileName)
