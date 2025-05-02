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

# Common tools import
from file_tools.common.eula import eula

# Json tools import
from file_tools.json_data.jsonLanguageDescriptionList import LanguageDescriptionList
from file_tools.json_data.jsonStringClassDescription import StringClassDescription

# File generator tools import
from pathgen import FileNameGenerator
from base_string_class import GenerateBaseLangFiles
from lang_string_class import GenerateLangFiles
from autogencmake import CmakeGenerator

# Command line default function import
from json_default import CreateDefaultLanguageListFile
from json_default import CreateDefaultStringFile

##################################
##################################
# Generate the cmake files
##################################
##################################
def GenerateCmake(baseFileGen:GenerateBaseLangFiles, langFileGen:GenerateLangFiles,
                  incDirList:list, mockDir:str, filePath:str,
                  jsonStringFile:StringClassDescription):
    """!
    @brief Generate the subdir makefile
    @param baseFileGen {GenerateBaseLangFiles} Object used to generate the base interface files
    @param langFileGen {GenerateLangFiles} Object used to generate the language specific interface files
    @param incDirList {list of strings} Include directory paths relative to the file base directory
    @param mockDir {string} Mock file output directory
    @param filePath {string} Base directory name
    @param jsonStringFile {StringClassDescription} Class description file
    """
    baseFileDir = os.path.basename(os.path.normpath(filePath))
    dynamicCompileSwitch = jsonStringFile.getDynamicCompileSwitch()
    cmakeGenerator = CmakeGenerator(baseFileGen, langFileGen, incDirList, mockDir, baseFileDir, jsonStringFile)
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

##################################
##################################
# Generate the source files
##################################
##################################
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
        GenerateCmake(baseFileGen, langFileGen, [incfileSubdir], mockfileSubdir, filePath, classStrings)

def MakeSubdir(basefilePath, subDirName):
    """!
    @brief Make the subdirectory within the output directory if it doesn't
           already exist
    @return Subdirectory path or ValueError if basefilePath/subDirName already exists as a file
    """
    testPath = os.path.join(basefilePath, subDirName)
    if not os.path.exists(testPath):
        os.makedirs(testPath)
    elif not os.path.isdir(testPath):
        raise ValueError("Error: \""+testPath+"\" already exists as file.")
    return testPath

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

    parser = argparse.ArgumentParser(prog="autogenlang subcommand",
                                     description="Update argpaser library language string h/cpp/unittest files")
    parser.add_argument('-j','--json', dest='jsonPath', required=False, type=pathlib.Path, default='../data',
                        help="Path to the json files, default = ../data")

    subcommands= parser.add_subparsers(title='subcommand', dest='subcommand', help='Options: build, langjson, classjson')

    buildParser = subcommands.add_parser('build', help='Build Help')
    buildParser.add_argument('-o','--outpath', dest='genfilepath', required=True, type=pathlib.Path,
                             default='../output', help='Existing destination directory for source and data files')
    buildParser.add_argument('--owner', dest='owner', required=False, type=str, default=None, help='Owner name')
    buildParser.add_argument('--eula', dest='eula', required=False, type=str, default=None, help=eulaHelp)

    langJsonParser = subcommands.add_parser('langjson', help='Language JSON File Commands Help')
    langJsonParser.add_argument('langcommand', choices=['createdefault', 'add'])

    classJsonParser = subcommands.add_parser('classjson', help='Strings Class JSON File Commands Help')
    classJsonParser.add_argument('stringscommand', choices=['createdefault', 'addtranslate','addproperty', 'languageupdate'])

    args = parser.parse_args()

    # Open the data files
    languageList = LanguageDescriptionList(FileNameGenerator.getLanguageDescriptionFileName(args.jsonPath))
    classStrings = StringClassDescription(FileNameGenerator.getStringClassDescriptionFileName(args.jsonPath))

    # Process the subcommand
    if args.subcommand == 'build':
        # Build the output directories
        basefilePath = os.path.abspath(args.genfilepath)
        if not os.path.exists(basefilePath):
            os.makedirs(basefilePath)
        elif not os.path.isdir(basefilePath):
            raise ValueError("Error: \""+basefilePath+"\" already exists as file.")

        # Generate the source and cmake files
        MakeSubdir(basefilePath, 'inc')
        MakeSubdir(basefilePath, 'src')
        MakeSubdir(basefilePath, 'test')
        MakeSubdir(basefilePath, 'mock')
        print ("Building source and cmake files")
        GenerateLanguageSelectFiles(languageList, classStrings, basefilePath,
                                    'inc', 'src', 'test', 'mock',
                                    args.owner, args.eula)

    elif args.subcommand == 'classjson':
        if args.stringscommand == 'createdefault':
            # Build the default methods definitions file
            print ("Updating Class Strings JSON file")
            CreateDefaultStringFile(languageList, classStrings, True)
        elif args.stringscommand == 'addtranslate':
            # Add a translation method to the strings file
            commit = classStrings.newTranslateMethodEntry(languageList)
            if commit:
                print ("Updating Class Strings JSON file")
                classStrings.update()
        elif args.stringscommand == 'addproperty':
            # Add a translation method to the strings file
            commit = classStrings.newPropertyMethodEntry()
            if commit:
                print ("Updating Class Strings JSON file")
                classStrings.update()
        elif args.stringscommand == 'languageupdate':
            # Build the default language list definitions file
            print ("Updating Class Strings JSON file")
            classStrings.updateTranlations(languageList)
            classStrings.update()
        else:
            raise ValueError("Error: Unknown JSON string file command: "+args.stringscommand)

    elif args.subcommand == 'langjson':
        if args.langcommand == 'createdefault':
            # Build the default language list definitions file
            print ("Updating Language JSON file")
            CreateDefaultLanguageListFile(languageList)
        elif args.langcommand == 'add':
            # Add a new language and update the class strings with the new language
            commit = languageList.newLanguage()
            if commit:
                print ("Updating Language JSON file")
                languageList.update()

                classStrings.updateTranlations(languageList)
                classStrings.update()
        else:
            raise ValueError("Error: Unknown JSON language file command: "+args.langcommand)
    else:
        raise ValueError("Error: Unknown subcommand: "+args.subcommand)


if __name__ == '__main__':
    CommandMain()