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

from file_tools.json_data.jsonLanguageDescriptionList import LanguageDescriptionList
from file_tools.json_data.jsonStringClassDescription import StringClassDescription
from file_tools.json_data.param_return_tools import ParamRetDict

######################################
######################################
# Create default langauge list JSON file
######################################
######################################
def AddEnglish(languages:LanguageDescriptionList):
    """!
    @brief Add the english language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "en"
    linuxRegionList = ["AU","BZ","CA","CB","GB","IE","JM","NZ","PH","TT","US","ZA","ZW"]
    winLanID = [0x09]
    winLanIDList = [3081,10249,4105,9225,2057,16393,6153,8201,5129,13321,7177,11273,1033,12297]
    languages.addLanguage("english", linuxEnv, linuxRegionList, winLanID, winLanIDList, "en", "ENGLISH_ERRORS")

def AddSpanish(languages:LanguageDescriptionList):
    """!
    @brief Add the spanish language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "es"
    linuxRegionList = ["AR","BO","CL","CO","CR","DO","EC","ES","GT","HN",
                       "MX","NI","PA","PE","PR","PY","SV","UY","VE"]
    winLanID = [0x0A]
    winLanIDList = [11274,16394,13322,9226,5130,7178,12298,17418,4106,18442,2058,19466,6154,15370,10250,20490,1034,14346,8202]
    languages.addLanguage("spanish", linuxEnv, linuxRegionList, winLanID, winLanIDList, "es", "SPANISH_ERRORS")

def AddFrench(languages:LanguageDescriptionList):
    """!
    @brief Add the french language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "fr"
    linuxRegionList = ["BE","CA","CH","FR","LU","MC"]
    winLanID = [0x0C]
    winLanIDList = [2060,11276,3084,9228,12300,1036,5132,13324,6156,14348,10252,4108,7180]
    languages.addLanguage("french", linuxEnv, linuxRegionList, winLanID, winLanIDList, "fr", "FRENCH_ERRORS")

def AddSimplifiedChinese(languages:LanguageDescriptionList):
    """!
    @brief Add the simplified chinese language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "zh"
    linuxRegionList = ["CN","HK","MO","SG","TW"]
    winLanID = [0x04]
    winLanIDList = [2052,3076,5124,4100,1028]
    languages.addLanguage("SimplifiedChinese", linuxEnv, linuxRegionList, winLanID, winLanIDList, "zh", "CHINESE_ERRORS")

def CreateDefaultLanguageListFile(languages:LanguageDescriptionList):
    """!
    @brief Create base default LanguageDescriptionList json file
    @param languages (LanguageDescriptionList) - Object to create
    """
    AddEnglish(languages)
    AddSpanish(languages)
    AddFrench(languages)
    AddSimplifiedChinese(languages)
    languages.setDefault("english")
    languages.update()

######################################
######################################
# Create default strings json file
######################################
######################################
def CreateDefaultStringFile(languageList:LanguageDescriptionList, classStrings:StringClassDescription, forceUpdate:bool = False):
    """!
    @brief Add a function to the self.langJsonData data
    @param languageList {LanguageDescriptionList} List of languages to translate
    @param classStrings {StringClassDescription} Object to create/update
    @param forceUpdate {boolean} True force the update without user intervention,
                                 False request update confermation on all methods
    """
    classStrings.setBaseClassName("ParserStringInterface")
    classStrings.setNamespaceName("argparser")
    classStrings.setDynamicCompileSwitch("DYNAMIC_INTERNATIONALIZATION")
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
