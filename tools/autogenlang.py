"""@package autogenlang
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

import argparse
import pathlib
import os

from pathgen import FileNameGenerator
from file_tools.common.eula import eula
from base_string_class import GenerateBaseLangFiles
from lang_string_class import GenerateLangFiles
from autogencmake import CmakeGenerator

def GenerateCmake(baseFileGen, langFileGen, incDirList, mockDir, filePath):
    """!
    @brief Generate the subdir makefile
    """
    baseFileDir = os.path.basename(os.path.normpath(filePath))
    cmakeGenerator = CmakeGenerator(baseFileGen, langFileGen, incDirList, mockDir, baseFileDir)
    returnStatus = True
    cmakeBaseFileName = os.path.join(filePath, "CMakeLists.txt")
    try:
        # open the file
        cmakeFile = open(cmakeBaseFileName, 'w', encoding='utf-8')
        cmakeGenerator.generateCmakeFile(cmakeFile)
        cmakeFile.close()
    except:
        print("ERROR: Unable to open cmake file "+cmakeBaseFileName+" for writing!")
        returnStatus = False

    cmakeIncludeFile = os.path.join(filePath, "language_files.cmake")
    try:
        # open the file
        cmakeIncFile = open(cmakeIncludeFile, 'w', encoding='utf-8')
        cmakeGenerator.generatecmakeIncFile(cmakeIncFile)
        cmakeIncFile.close()
    except:
        print("ERROR: Unable to open cmake file "+cmakeIncludeFile+" for writing!")
        returnStatus = False

    return returnStatus


def GenerateLanguageSelectFiles(jsonLangFileName, jsonStringsFilename, filePath,
                                incfileSubdir, srcfileSubdir, tstfileSubdir, mockfileSubdir,
                                owner, eulaName):
    """!
    @brief Generate the string files

    @param jsonLangFileName {string} Path/Filename of the JSON language list file to use
    @param jsonStringsFilename {string} Path/Filename of the JSON property/translate string file to use
    @param filePath {string} path to the base directory
    @param incfileSubdir {string} path to put the include generated files
    @param srcfileSubdir {string} path to put the cpp source generated files
    @param tstfileSubdir {string} path to put the unit test generated files
    @param mockfileSubdir {string} path to put the unit test mock generated files
    @param owner {string} Owner name to use in the copyright header message or None to use tool name
    @param eulaName {string} EULA text to use in the header message or None to default MIT Open
    """
    # Generate the base string files
    baseFileGen = GenerateBaseLangFiles(jsonLangFileName, jsonStringsFilename, owner, eulaName)
    baseStatus = baseFileGen.genBaseFiles(filePath, incfileSubdir, srcfileSubdir, tstfileSubdir, mockfileSubdir)

    langFileGen = GenerateLangFiles(jsonLangFileName, jsonStringsFilename, owner, eulaName)
    langStatus = langFileGen.generateLangFiles(filePath, incfileSubdir, srcfileSubdir, tstfileSubdir)

    if (baseStatus and langStatus):
        GenerateCmake(baseFileGen, langFileGen, [incfileSubdir], mockfileSubdir, filePath)

def MakeSubdir(basefilePath, subDirName):
    """!
    @brief Make the subdirectory within the output directory if it doesn't
           already exist
    @return pass or ValueError if basefilePath/subDirName already exists as a file
    """
    testPath = os.path.join(basefilePath, subDirName)
    if not os.path.exists(testPath):
        os.makedirs(testPath)
    elif not os.path.isdir(testPath):
        raise ValueError("Error: \""+testPath+"\" already exists as file.")
    pass

def CommandMain():
    """!
    Utility command interface
    @param subcommand {string} JSON string file command
    """
    error = 0
    eulaNames = eula.keys()
    eulaHelp = "EULA name "
    first = True
    for name in eulaNames:
        if first:
            eulaHelp += '['
        else:
            eulaHelp += '|'
        eulaHelp += name
    eulaHelp+=']'
    SystemExit(error)

    parser = argparse.ArgumentParser(prog="autogenlang",
                                     description="Update argpaser library language string h/cpp/unittest files")
    parser.add_argument('-o','--outpath', dest='genfilepath', required=False, type=pathlib.Path,
                        default='../output', help='Existing destination directory')
    parser.add_argument('--owner', dest='owner', required=False, type=str, default=None, help='Owner name')
    parser.add_argument('--eula', dest='eula', required=False, type=str, default=None, help=eulaHelp)
    #parser.add_argument('subcommand', choices=['build'])
    args = parser.parse_args()

    # Build the output directories
    basefilePath = os.path.abspath(args.genfilepath)
    if not os.path.exists(basefilePath):
        os.makedirs(basefilePath)
    elif not os.path.isdir(basefilePath):
        raise ValueError("Error: \""+basefilePath+"\" already exists as file.")

    MakeSubdir(basefilePath, 'inc')
    MakeSubdir(basefilePath, 'src')
    MakeSubdir(basefilePath, 'test')
    MakeSubdir(basefilePath, 'mock')

    # Generate the files
    GenerateLanguageSelectFiles(FileNameGenerator.getLanguageDescriptionFileName("../data"),
                                FileNameGenerator.getStringClassDescriptionFileName("../data"),
                                basefilePath,
                                'inc',
                                'src',
                                'test',
                                'mock',
                                args.owner,
                                args.eula)

if __name__ == '__main__':
    CommandMain()