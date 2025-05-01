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
from base_string_class import GenerateBaseLangFiles
from lang_string_class import GenerateLangFiles
from autogencmake import CmakeGenerator

from file_tools.common.eula import eula
from file_tools.string_class_tools import StringClassNameGen
from file_tools.json_data.jsonLanguageDescriptionList import LanguageDescriptionList
from file_tools.json_data.jsonStringClassDescription import StringClassDescription
from file_tools.json_data.param_return_tools import ParamRetDict

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


def GenerateLanguageSelectFiles(languageList:LanguageDescriptionList, classStrings:StringClassDescription,
                                filePath:str, incfileSubdir:str, srcfileSubdir:str, tstfileSubdir:str,
                                mockfileSubdir:str, owner:str, eulaName:str):
    """!
    @brief Generate the string files

    @param languageList {StringClassDescription} JSON language list object
    @param classStrings {LanguageDescriptionList} JSON property/translate string object to use
    @param filePath {string} path to the base directory
    @param incfileSubdir {string} path to put the include generated files
    @param srcfileSubdir {string} path to put the cpp source generated files
    @param tstfileSubdir {string} path to put the unit test generated files
    @param mockfileSubdir {string} path to put the unit test mock generated files
    @param owner {string} Owner name to use in the copyright header message or None to use tool name
    @param eulaName {string} EULA text to use in the header message or None to default MIT Open
    """
    # Generate the base string files
    baseFileGen = GenerateBaseLangFiles(languageList, classStrings, owner, eulaName)
    baseStatus = baseFileGen.genBaseFiles(filePath, incfileSubdir, srcfileSubdir, tstfileSubdir, mockfileSubdir)

    langFileGen = GenerateLangFiles(languageList, classStrings, owner, eulaName)
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

def CreateDefaultStringFile(languageList:LanguageDescriptionList, classStrings:StringClassDescription, forceUpdate:bool = False):
    """!
    @brief Add a function to the self.langJsonData data
    @param languageList {LanguageDescriptionList} List of languages to translate
    @param classStrings {StringClassDescription} Object to create/update
    @param forceUpdate {boolean} True force the update without user intervention,
                                 False request update confermation on all methods
    """
    classStrings.setBaseClassName(StringClassNameGen.getBaseClassName())
    classStrings.addPropertyMethodEntry("isoCode", override = forceUpdate)

    # General argument parsing messages
    classStrings.addTranslateMethodEntry("getNotListTypeMessage", "Return non-list varg error message",
                                         [ParamRetDict.buildParamDictWithMod("nargs", "integer", "input nargs value")],
                                         ParamRetDict.buildReturnDict("string", "Non-list varg error message"),
                                         "en",
                                         "Only list type arguments can have an argument count of @nargs@",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getUnknownArgumentMessage", "Return unknown parser key error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Unknown key")],
                                         ParamRetDict.buildReturnDict("string", "Unknown parser key error message"),
                                         "en",
                                         "Unknown argument: @keyString@",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getInvalidAssignmentMessage", "Return varg invalid assignment error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key")],
                                         ParamRetDict.buildReturnDict("string", "Varg key invalid assignment error message"),
                                         "en",
                                         "\"@keyString@\" invalid assignment",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getAssignmentFailedMessage", "Return varg assignment failed error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key"),
                                          ParamRetDict.buildParamDictWithMod("valueString", "string", "Assignment value")],
                                         ParamRetDict.buildReturnDict("string", "Varg key assignment failed error message"),
                                         "en",
                                         "\"@keyString@\", \"@valueString@\" assignment failed",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getMissingAssignmentMessage", "Return varg missing assignment error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key")],
                                         ParamRetDict.buildReturnDict("string", "Varg key missing value assignment error message"),
                                         "en",
                                         "\"@keyString@\" missing assignment value",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getMissingListAssignmentMessage", "Return varg missing list value assignment error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key"),
                                          ParamRetDict.buildParamDictWithMod("nargsExpected", "size", "Expected assignment list length"),
                                          ParamRetDict.buildParamDictWithMod("nargsFound", "size", "Input assignment list length")],
                                         ParamRetDict.buildReturnDict("string", "Varg key input value list too short error message"),
                                         "en",
                                         "\"@keyString@\" missing assignment value(s). Expected: @nargsExpected@ found: @nargsFound@ arguments",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getTooManyAssignmentMessage", "Return varg missing list value assignment error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key"),
                                          ParamRetDict.buildParamDictWithMod("nargsExpected", "size", "Expected assignment list length"),
                                          ParamRetDict.buildParamDictWithMod("nargsFound", "size", "Input assignment list length")],
                                          ParamRetDict.buildReturnDict("string", "Varg key input value list too long error message"),
                                         "en",
                                         "\"@keyString@\" too many assignment values. Expected: @nargsExpected@ found: @nargsFound@ arguments",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getMissingArgumentMessage", "Return required varg missing error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key")],
                                         ParamRetDict.buildReturnDict("string", "Required varg key missing error message"),
                                         "en",
                                         "\"@keyString@\" required argument missing",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getArgumentCreationError", "Return parser add varg failure error message",
                                         [ParamRetDict.buildParamDictWithMod("keyString", "string", "Error key")],
                                         ParamRetDict.buildReturnDict("string", "Parser varg add failure message"),
                                         "en",
                                         "Argument add failed: @keyString@",
                                         override = forceUpdate,
                                         languageList = languageList)

    # Command Line parser messages
    classStrings.addTranslateMethodEntry("getUsageMessage", "Return usage help message",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "Usage help message"),
                                         "en",
                                         "Usage:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getPositionalArgumentsMessage", "Return positional argument help message",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "Positional argument help message"),
                                         "en",
                                         "Positional Arguments:",
                                         override = forceUpdate,
                                         languageList = languageList)


    classStrings.addTranslateMethodEntry("getSwitchArgumentsMessage", "Return optional argument help message",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "Optional argument help message"),
                                         "en",
                                         "Optional Arguments:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getHelpString", "Return default help switch help message",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "Default help argument help message"),
                                         "en",
                                         "show this help message and exit",
                                         override = forceUpdate,
                                         languageList = languageList)

    # Environment parser messages
    classStrings.addTranslateMethodEntry("getEnvArgumentsMessage", "Return environment parser argument help header",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "Environment parser argument help header message"),
                                         "en",
                                         "Defined Environment values:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getEnvironmentNoFlags", "Return environment parser add flag varg failure error message",
                                         [ParamRetDict.buildParamDictWithMod("envKeyString", "string", "Flag key")],
                                         ParamRetDict.buildReturnDict("string", "Environment parser add flag varg failure message"),
                                         "en",
                                         "Environment value @envKeyString@ narg must be > 0",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getRequiredEnvironmentArgMissing", "Return environment parser required varg missing error message",
                                         [ParamRetDict.buildParamDictWithMod("envKeyString", "string", "Flag key")],
                                         ParamRetDict.buildReturnDict("string", "Environment parser required varg missing error message"),
                                         "en",
                                         "Environment value @envKeyString@ must be defined",
                                         override = forceUpdate,
                                         languageList = languageList)


    # JSON file parser messages
    classStrings.addTranslateMethodEntry("getJsonArgumentsMessage", "Return json parser argument help header",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "JSON parser argument help header message"),
                                         "en",
                                         "Available JSON argument values:",
                                         override = forceUpdate,
                                         languageList = languageList)

    # XML file parser messages
    classStrings.addTranslateMethodEntry("getXmlArgumentsMessage", "Return xml parser argument help header",
                                         [],
                                         ParamRetDict.buildReturnDict("string", "XML parser argument help header message"),
                                         "en",
                                         "Available XML argument values:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.update()

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

    parser = argparse.ArgumentParser(prog="autogenlang [options] subcommand",
                                     description="Update argpaser library language string h/cpp/unittest files")
    parser.add_argument('subcommand', choices=['build','createdefaultstrings'])
    parser.add_argument('-o','--outpath', dest='genfilepath', required=False, type=pathlib.Path,
                        default='../output', help='Existing destination directory')
    parser.add_argument('--owner', dest='owner', required=False, type=str, default=None, help='Owner name')
    parser.add_argument('--eula', dest='eula', required=False, type=str, default=None, help=eulaHelp)
    args = parser.parse_args()

    # Open the data files
    languageList = LanguageDescriptionList(FileNameGenerator.getLanguageDescriptionFileName("../data"))
    classStrings = StringClassDescription(FileNameGenerator.getStringClassDescriptionFileName("../data"))

    if args.subcommand == 'build':
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
        GenerateLanguageSelectFiles(languageList, classStrings, basefilePath,
                                    'inc', 'src', 'test', 'mock',
                                    args.owner, args.eula)
    elif args.subcommand == 'createdefaultstrings':
        # Rebuild the default methos definitions file
        CreateDefaultStringFile(languageList, classStrings, True)

if __name__ == '__main__':
    CommandMain()