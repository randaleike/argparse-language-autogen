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

import re
import json

from pathgen import FileNameGenerator

class LanguageDescriptionList(object):
    """!
    Language description list data
    """
    def __init__(self, langListFileName = None):
        """!
        @brief LanguageDescriptionList constructor

        @param langListFileName (string) - Name of the json file containing
                                           the language description data
        """
        if langListFileName is None:
            self.filename = FileNameGenerator.getLanguageDescriptionFileName()
        else:
            self.filename = langListFileName

        try:
            langJsonFile = open(self.filename, 'r', encoding='utf-8')
        except FileNotFoundError:
            self.langJsonData = {'default':{'name':"english", 'isoCode':"en"}, 'languages':{}}
        else:
            self.langJsonData = json.load(langJsonFile)
            langJsonFile.close()

    def _printError(self, errorStr):
        print ("Error: "+errorStr)

    def update(self):
        """!
        @brief Update the JSON file with the current contents of self.langJsonData
        """
        with open(self.filename, 'w', encoding='utf-8') as langJsonFile:
            json.dump(self.langJsonData, langJsonFile, indent=2)

    def setDefault(self, langName):
        """!
        @brief

        @param langName (string) - Language name to use default if detection fails
        """
        if langName.lower() in self.langJsonData['languages'].keys():
            defaultDict = {'name':langName, 'isoCode':self.langJsonData['languages'][langName]['isoCode']}
            self.langJsonData['default'] = defaultDict
        else:
            self._printError("You must select a current language as the default.")
            print("Available languages:")
            for langName in list(self.langJsonData['languages']):
                print("  "+langName)

    def getDefaultData(self):
        """!
        @brief Get the default language data
        @return tuple (string, string) - Default lauguage (entry name, ISO 639 set 3 language code)
        """
        defaultLang = self.langJsonData['default']['name']
        defaultIsoCode = self.langJsonData['default']['isoCode']
        return defaultLang, defaultIsoCode

    @staticmethod
    def _createLanguageEntry(googleLangCode = "", linuxEnvCode = "", linuxRegionList = [],
                             windowsLangId = [], windowsRegionList = [] , iso639Code = "", compileSwitch = ""):
        """!
        @brief Create a language dictionart entry

        @param googleLangCode (string) - Google translate language code
        @param linuxEnvCode (string) - linux LANG environment value for this language
        @param linuxRegionList (list of strings) - Linux LANG region codes for this language
        @param windowsLangId (list of numbers) - Windows LANGID & 0xFF value(s) for this language
        @param windowsRegionList (list of numbers) - Windows LANGID value(s) for this language
        @param iso639Code (string) - ISO 639 set 3 language code
        @param compileSwitch (string) - Language compile switch

        @return language dictionary object
        """
        langData = [('googleCode', googleLangCode),
                    ('LANG', linuxEnvCode),
                    ('LANG_regions', linuxRegionList),
                    ('LANGID', windowsLangId),
                    ('LANGID_regions', windowsRegionList),
                    ('isoCode', iso639Code),
                    ('compileSwitch', compileSwitch)]
        langEntry = dict(langData)
        return langEntry

    def getLanguageList(self):
        """!
        @brief Get a list of the current defined languages
        @return list of strings - Current ['languages'] keys
        """
        return list(self.langJsonData['languages'].keys())

    def getLanguagePropertyData(self, entryName, propertyName):
        """!
        @brief Get a list of the current defined languages
        @return list of strings - Current ['languages'] keys
        """
        return self.langJsonData['languages'][entryName][propertyName]

    def getLanguageGoogleCodeData(self, entryName):
        """!
        @brief Get the googleCode data for the given entryName language
        @param entryName {string} Entry key from getLanguageList entry
        @return string - Current ['languages'][entryName]['googleCode'] data
        """
        return self.langJsonData['languages'][entryName]['googleCode']

    def getLanguageLANGData(self, entryName):
        """!
        @brief Get the LANG and LANG_regions data for the given entryName language
        @param entryName {string} Entry key from getLanguageList entry
        @return tuple (string, list of strings) - Current ['languages'][entryName]['LANG'] data,
                                                  and ['languages'][entryName]['LANGID_regions'] data
        """
        langCode = self.langJsonData['languages'][entryName]['LANG']
        regionList = self.langJsonData['languages'][entryName]['LANG_regions']
        return langCode, regionList

    def getLanguageLANGIDData(self, entryName):
        """!
        @brief Get the LANGID and LANGID_regions data for the given entryName language
        @param entryName {string} Entry key from getLanguageList entry
        @return tuple (list of numbers, list of numbers) -
                Current ['languages'][entryName]['LANGID'] data,
                and ['languages'][entryName]['LANGID_regions'] data
        """
        langCode = self.langJsonData['languages'][entryName]['LANGID']
        regionList = self.langJsonData['languages'][entryName]['LANGID_regions']
        return langCode, regionList

    def getLanguageIsoCodeData(self, entryName):
        """!
        @brief Get the isoCode data for the given entryName language
        @param entryName {string} Entry key from getLanguageList entry
        @return string - Current ['languages'][entryName][isoCode] data
        """
        return self.langJsonData['languages'][entryName]['isoCode']

    def getLanguageCompileSwitchData(self, entryName):
        """!
        @brief Get the compileSwitch data for the given entryName language
        @param entryName {string} Entry key from getLanguageList entry
        @return string - Current ['languages'][entryName][compileSwitch] data
        """
        return self.langJsonData['languages'][entryName]['compileSwitch']

    @staticmethod
    def getLanguagePropertyList():
        """!
        @brief Return a tuple list of the usable language dictionary entries
        @return list of language entry property names
        """
        entryTemplate = LanguageDescriptionList._createLanguageEntry()
        return list(entryTemplate.keys())

    @staticmethod
    def getLanguagePropertyReturnData(propertyName):
        """!
        @brief Get the property description
        @param propertyName (string) Name of the property from getLanguagePropertyList()
        @return tuple - Data type (text|number) or None if the propertyName is unknown
                        Description or None if the propertyName is unknown
                        True if data is a list else False
        """
        if propertyName == 'googleCode':
            return "string", "Google translate language code", False
        elif propertyName == 'LANG':
            return "string", "Linux environment language code", False
        elif propertyName == 'LANG_regions':
            return "string", "Linux environment region codes for this language code", True
        elif propertyName == 'LANGID':
            return "LANGID", "Windows LANGID & 0xFF language code(s)", True
        elif propertyName == 'LANGID_regions':
            return "LANGID", "Windows full LANGID language code(s)", True
        elif propertyName == 'isoCode':
            return "string", "ISO 639 set 3 language code", False
        else:
            return None, None, False

    @staticmethod
    def getLanguagePropertyMethodName(propertyName):
        """!
        @brief Get the property method name
        @param propertyName (string) Name of the property from getLanguagePropertyList()
        @return string CPP description or None if the propertyName is unknown
        """
        if propertyName == 'googleCode':
            return "getGoogleTranslateCode"
        elif propertyName == 'LANG':
            return "getLANGLanguage"
        elif propertyName == 'LANG_regions':
            return "getLANGRegionList"
        elif propertyName == 'LANGID':
            return "getLANGIDCode"
        elif propertyName == 'LANGID_regions':
            return "getLANGIDList"
        elif propertyName == 'isoCode':
            return "getLangIsoCode"
        else:
            return None

    @staticmethod
    def getLanguageIsoPropertyMethodName():
        """!
        @brief Get the property method name
        @return string CPP description or None if the propertyName is unknown
        """
        return LanguageDescriptionList.getLanguagePropertyMethodName('isoCode')

    def addLanguage(self, langName, googleLangCode, linuxEnvCode, linuxRegionList,
                    windowsLangId, windowsRegionList, iso639Code, compileSwitch):
        """!
        @brief Add a language to the self.langJsonData data

        @param langName (string) - Language name to use for file/class name generation
        @param googleLangCode (string) - Google translate language code
        @param linuxEnvCode (string) - linux LANG environment value for this language
        @param linuxRegionList (list of strings) - Linux LANG region codes for this language
        @param windowsLangId (list of numbers) - Windows LANGID & 0xFF value(s) for this language
        @param windowsRegionList (list of numbers) - Windows LANGID value(s) for this language
        @param iso639Code (string) - ISO 639 set 3 language code
        @param compileSwitch (string) - Language compile switch
        """
        langEntry = self._createLanguageEntry(googleLangCode, linuxEnvCode, linuxRegionList,
                                              windowsLangId, windowsRegionList, iso639Code,
                                              compileSwitch)
        self.langJsonData['languages'][langName] = langEntry

    def _inputLanguageName(self):
        """!
        @brief Get the language from user input and check for validity
        @return string - language name
        """
        languageName = ""
        while(languageName == ""):
            name = input("Enter language name value to be used for class<lang> generation: ").lower()

            # Check validity
            if re.match('^[a-z].*', name):
                # Valid name
                languageName = name
            else:
                # invalid name
                self._printError("Only characters a-z are allowed in the <lang> name, try again.")
        return languageName

    def _inputGoogleTranslateCode(self):
        """!
        @brief Get the google translate language code from user input and check for validity
        @return string - translate code
        """
        googleTranslateId = ""
        while(googleTranslateId == ""):
            transId = input("Enter google translate language code (2 lower case characters): ").lower()

            # Check validity
            if re.match('^[a-z]{2}$', transId):
                # Valid name
                googleTranslateId = transId
            else:
                # invalid name
                self._printError("Only two characters a-z are allowed in the code, try again.")
        return googleTranslateId

    def _inputLinuxLangCode(self):
        """!
        @brief Get the linux language code from user input and check for validity
        @return string - linux language code
        """
        linuxLangId = ""
        while(linuxLangId == ""):
            linuxEnvCode = input("Enter linux language code (first 2 chars of 'LANG' environment value): ").lower()

            # Check validity
            if re.match('^[a-z]{2}$', linuxEnvCode):
                # Valid name
                linuxLangId = linuxEnvCode
            else:
                # invalid name
                self._printError("Only two characters a-z are allowed in the code, try again.")
        return linuxLangId

    def _inputLinuxLangRegions(self):
        """!
        @brief Get the linux language region code(s) from user input and check for validity
        @return list of strings - linux region codes
        """
        linuxRegionList = []
        print ("Enter linux region code(s) (2 chars following the _ in the 'LANG' environment value).")
        print ("Enter empty string to exit.")

        while (True):
            region = input("Region value: ").upper()

            # Check validity
            if region == "":
                # End of list
                break
            elif re.match('^[A-Z]{2}$', region):
                # Valid region
                linuxRegionList.append(region)
            else:
                # invalid name
                self._printError("Only two characters A-Z are allowed in the code, try again.")
        return linuxRegionList

    def _inputWindowsLangIds(self):
        """!
        @brief Get the windows language code(s) from user input
        @return tuple ([numbers], [numbers]) - windows LANGID codes.  First list is
                unique user LANGID codees & 0x0FF. Second list is all LANGID codes from user)
        """
        windowsIdCodeList = []
        windowsIdCodes = []
        print ("Enter Windows LANGID values. A value of 0 will exit.")
        while (True):
            region = int(input("LANGID value: "))
            if region == 0:
                break
            else:
                if region > 0x0FF:
                    if region not in windowsIdCodeList:
                        windowsIdCodeList.append(region)

                winId = region & 0x0FF
                if winId not in windowsIdCodes:
                    windowsIdCodes.append(winId)
        return windowsIdCodes, windowsIdCodeList

    def newLanguage(self):
        """!
        @brief Add a new language to the self.langJsonData data

        @return boolean - True if user selected to overwrite or commit
        """
        newEntry = {}
        entryCorrect = False

        while not entryCorrect:
            name = self._inputLanguageName()
            compileSwitch = name.upper()+"_ERRORS"
            googleCode = self._inputGoogleTranslateCode()
            linuxLangCode = self._inputLinuxLangCode()
            linuxLangRegions = self._inputLinuxLangRegions()
            winCaseIds, winLangIds = self._inputWindowsLangIds()

            newEntry = self._createLanguageEntry(googleCode, linuxLangCode, linuxLangRegions,
                                                 winCaseIds, winLangIds, googleCode, compileSwitch)

            # Print entry for user to inspect
            print("New Entry:")
            print(newEntry)
            commit = input("Is this correct? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                entryCorrect = True


        # Determine if it's an overwrite or addition
        commitFlag = False
        if name in self.langJsonData['languages'].keys():
            # Determine if we should overwrite existing
            commit = input("Overwrite existing "+name+" entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                self.langJsonData['languages'][name] = newEntry
                commitFlag = True
        else:
            # Determine if we should add the new entry
            commit = input("Add new entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                self.langJsonData['languages'][name] = newEntry
                commitFlag = True

        return commitFlag

def AddEnglish(languages):
    """!
    @brief Add the english language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "en"
    linuxRegionList = ["AU","BZ","CA","CB","GB","IE","JM","NZ","PH","TT","US","ZA","ZW"]
    winLanID = [0x09]
    winLanIDList = [3081,10249,4105,9225,2057,16393,6153,8201,5129,13321,7177,11273,1033,12297]
    languages.addLanguage("english", "en", linuxEnv, linuxRegionList, winLanID, winLanIDList, "en", "ENGLISH_ERRORS")

def AddSpanish(languages):
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
    languages.addLanguage("spanish", "es", linuxEnv, linuxRegionList, winLanID, winLanIDList, "es", "SPANISH_ERRORS")

def AddFrench(languages):
    """!
    @brief Add the french language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "fr"
    linuxRegionList = ["BE","CA","CH","FR","LU","MC"]
    winLanID = [0x0C]
    winLanIDList = [2060,11276,3084,9228,12300,1036,5132,13324,6156,14348,10252,4108,7180]
    languages.addLanguage("french", "fr", linuxEnv, linuxRegionList, winLanID, winLanIDList, "fr", "FRENCH_ERRORS")

def AddSimplifiedChinese(languages):
    """!
    @brief Add the simplified chinese language definition
           Example for AddLanguage call

    @param languages (LanguageDescriptionList) - Object to add to
    """
    linuxEnv = "zh"
    linuxRegionList = ["CN","HK","MO","SG","TW"]
    winLanID = [0x04]
    winLanIDList = [2052,3076,5124,4100,1028]
    languages.addLanguage("SimplifiedChinese", "zh", linuxEnv, linuxRegionList, winLanID, winLanIDList, "zh", "CHINESE_ERRORS")

def CreateDefaultJson(languages):
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

def PrintLanguages(languages):
    """!
    @brief Print the current language data file
    @param languages (LanguageDescriptionList) - Object to output
    """
    jsonLangData = jsonLangFile.langJsonData
    for langName, langData in jsonLangData['languages'].items():
        print (langName+": {")
        print (langData)
        print ("} end "+langName)

    print ("Default = "+jsonLangData['default']['name'])

def AddLanguage(languages):
    """!
    @brief Add a language to the LanguageDescriptionList file
    @param languages (LanguageDescriptionList) - Object to add new language data to
    """
    commit = languages.newLanguage()
    if commit:
        print ("Updating JSON file")
        languages.update()

import argparse
import pathlib

def CommandMain():
    """!
    Utility command interface
    @param subcommand {string} JSON Language command
    """
    parser = argparse.ArgumentParser(prog="jsonLanguageDescriptionList",
                                     description="Update argpaser library language description JSON file")
    parser.add_argument('-p','--path', dest='jsonpath', required=False, type=pathlib.Path,
                        default='../data', help='Existing destination directory')
    parser.add_argument('subcommand', choices=['add', 'print', 'createnew', 'setdefaultlang'],
                        help='Use one of the valid defined subcommands [add|print|createnew|setdefaultlang]')

    args = parser.parse_args()
    jsonLangFile = LanguageDescriptionList(FileNameGenerator.getLanguageDescriptionFileName(args.jsonpath))
    if args.subcommand.lower() == "add":
        AddLanguage(jsonLangFile)
    elif args.subcommand.lower() == "print":
        PrintLanguages(jsonLangFile)
    elif args.subcommand.lower() == "createnew":
        CreateDefaultJson(jsonLangFile)
    elif args.subcommand.lower() == "setdefaultlang":
        defaultLang = jsonLangFile._inputLanguageName()
        jsonLangFile.setDefault(defaultLang)
    else:
        print ("Error: Unknown JSON language description file command: "+args.subcommand)
        SystemExit(1)


if __name__ == '__main__':
    CommandMain()
