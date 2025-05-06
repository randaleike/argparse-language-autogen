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

class ParamRetDict(object):
    typeModList:int  = 1<<0
    typeModPtr:int   = 1<<1
    typeModRef:int   = 1<<2
    typeModUndef:int = 1<<3

    typeModArrayShift:int = 16
    typeModArrayMask:int  = 0xFFFF

    """!
    Parameter and return dictionary definitions
    """
    def __init__(self):
        pass

    @staticmethod
    def buildDictModValue(isList:bool = False, isReference:bool = False, isPtr:bool = False, orUndef:bool = False) -> int:
        """!
        @brief Build a return data dictionary
        @param isList {boolean} True if return is list, false if not
        @param isReference {boolean} True if item needs a pointer decoration, false if not
        @param isPtr {boolean} True if item needs a reference decoration, false if not
        @param orUndef {boolean} True if item can also be language undefined type, false if not
        @return {int} Mod value
        """
        entryTypeMod = 0
        if isList:
           entryTypeMod |= ParamRetDict.typeModList
        if isReference:
           entryTypeMod |= ParamRetDict.typeModRef
        if isPtr:
           entryTypeMod |= ParamRetDict.typeModPtr
        if orUndef:
           entryTypeMod |= ParamRetDict.typeModUndef
        return entryTypeMod

    @staticmethod
    def buildReturnDictWithMod(retType:str, retDesc:str = "", entryTypeMod:int = 0) -> dict:
        """!
        @brief Build a return data dictionary
        @param retType {string} Code type definition
        @param retDesc {string} Brief description of the return value for @return doxygen generation
        @param entryTypeMod {integer} Type modification flags
        @return {dictionary} Return dictionary
        """
        return {'type':retType, 'desc':retDesc, 'typeMod': entryTypeMod}

    @staticmethod
    def buildReturnDict(retType:str, retDesc:str = "", isList:bool = False,
                        isReference:bool = False, isPtr:bool = False, orUndef:bool = False) -> dict:
        """!
        @brief Build a return data dictionary
        @param retType {string} Code type definition
        @param retDesc {string} Brief description of the return value for @return doxygen generation
        @param isList {boolean} True if return is list, false if not
        @param isReference {boolean} True if parameter needs a pointer decoration, false if not
        @param isPtr {boolean} True if parameter needs a reference decoration, false if not
        @param orUndef {boolean} True if item can also be language undefined type, false if not
        @return {dictionary} Return dictionary
        """
        entryTypeMod = ParamRetDict.buildDictModValue(isList, isReference, isPtr, orUndef)
        return ParamRetDict.buildReturnDictWithMod(retType, retDesc, entryTypeMod)

    @staticmethod
    def getReturnData(returnDict:dict) -> tuple:
        """!
        @brief Build a return data dictionary
        @param returnDict {dictionary} Return dictionary entry
        @return tuple - Return type string
                        Return description string,
                        Return type modifier bit flags
        """
        return returnDict['type'], returnDict['desc'], returnDict['typeMod']

    @staticmethod
    def getReturnType(returnDict:dict) -> str:
        """!
        @brief Build a return data dictionary
        @param returnDict {dictionary} Return dictionary entry
        @return string - Return type string
        """
        return returnDict['type']

    @staticmethod
    def getReturnDesc(returnDict:dict) -> str:
        """!
        @brief Build a return data dictionary
        @param returnDict {dictionary} Return dictionary entry
        @return string - Return type brief description
        """
        return returnDict['desc']

    @staticmethod
    def getReturnTypeMod(returnDict:dict) -> int:
        """!
        @brief Build a return data dictionary
        @param returnDict {dictionary} Return dictionary entry
        @return int - Return type modification flags
        """
        return returnDict['typeMod']

    @staticmethod
    def buildParamDictWithMod(paramName:str, paramType:str, paramDesc:str = "", entryTypeMod:int = 0) -> dict:
        """!
        @brief Build a return data dictionary
        @param paramName {string} Code param name
        @param paramType {string} Code param type
        @param paramDesc {string} Brief description of the param value for @param doxygen generation
        @param entryTypeMod {int} Type modification flags
        @return {dictionary} Parameter dictionary
        """
        return {'name':paramName, 'type':paramType, 'desc':paramDesc, 'typeMod':entryTypeMod}

    @staticmethod
    def buildParamDict(paramName:str, paramType:str, paramDesc:str = "", isList:bool = False,
                       isReference:bool = False, isPtr:bool = False, orUndef:bool = False) -> dict:
        """!
        @brief Build a return data dictionary
        @param paramName {string} Code param name
        @param paramType {string} Code param type
        @param paramDesc {string} Brief description of the param value for @param doxygen generation
        @param isList {boolean} True if parameter is list, false if not
        @param isReference {boolean} True if parameter needs a pointer decoration, false if not
        @param isPtr {boolean} True if parameter needs a reference decoration, false if not
        @param orUndef {boolean} True if item can also be language undefined type, false if not
        @return {dictionary} Parameter dictionary
        """
        entryTypeMod = ParamRetDict.buildDictModValue(isList, isReference, isPtr, orUndef)
        return ParamRetDict.buildParamDictWithMod(paramName, paramType, paramDesc, entryTypeMod)

    @staticmethod
    def getParamData(paramDict:dict) -> tuple:
        """!
        @brief Build a return data dictionary
        @param paramDict {dictionary} Parameter dictionary entry
        @return tuple - Parameter name string,
                        Parameter type string (text|number),
                        Parameter description string
                        Parameter type modifier bit flags
        """
        return paramDict['name'], paramDict['type'], paramDict['desc'], paramDict['typeMod']

    @staticmethod
    def getParamType(paramDict:dict) -> str:
        """!
        @brief Build a return data dictionary
        @param paramDict {dictionary} Parameter dictionary entry
        @return string - Parameter type string
        """
        return paramDict['type']

    @staticmethod
    def getParamName(paramDict:dict) -> str:
        """!
        @brief Build a return data dictionary
        @param paramDict {dictionary} Parameter dictionary entry
        @return string - Parameter name string
        """
        return paramDict['name']

    @staticmethod
    def getParamDesc(paramDict:dict) -> str:
        """!
        @brief Build a return data dictionary
        @param paramDict {dictionary} Parameter dictionary entry
        @return string - Parameter description string
        """
        return paramDict['desc']

    @staticmethod
    def getParamTypeMod(paramDict:dict) -> int:
        """!
        @brief Build a return data dictionary
        @param paramDict {dictionary} Parameter dictionary entry
        @return int - Parameter type modification flags
        """
        return paramDict['typeMod']

    @staticmethod
    def isModList(typeMod:int) -> bool:
        """!
        @brief Check if the input typeMode has the list modifier set
        @param typeMod {integer} Dictionary TypeMod entry
        @return bool - True if object needs to be a list type, else false
        """
        if (typeMod & ParamRetDict.typeModList) == 0:
            return False
        else:
            return True

    @staticmethod
    def isModPointer(typeMod:int) -> bool:
        """!
        @brief Check if the input typeMode has the pointer modifier set
        @param typeMod {integer} Dictionary TypeMod entry
        @return bool - True if object needs a pointer decoration, else false
        """
        if (typeMod & ParamRetDict.typeModPtr) == 0:
            return False
        else:
            return True

    @staticmethod
    def isModReference(typeMod:int) -> bool:
        """!
        @brief Check if the input typeMode has the reference modifier set
        @param typeMod {integer} Dictionary TypeMod entry
        @return bool - True if object needs a reference decoration, else false
        """
        if (typeMod & ParamRetDict.typeModRef) == 0:
            return False
        else:
            return True

    @staticmethod
    def isOrUndefType(typeMod:int) -> bool:
        """!
        @brief Check if the input typeMode has the Or undefined modifier set
        @param typeMod {integer} Dictionary TypeMod entry
        @return bool - True if object can be undefined, else false
        """
        if (typeMod & ParamRetDict.typeModUndef) == 0:
            return False
        else:
            return True

    @staticmethod
    def getArraySize(typeMod:int) -> int:
        """!
        @brief Get the array size in the type modifier value
        @param typeMod {integer} Dictionary TypeMod entry
        @return int - Array size
        """
        return ((typeMod >> ParamRetDict.typeModArrayShift) & ParamRetDict.typeModArrayMask)

    @staticmethod
    def setArraySize(varDict:dict, arraySize:int):
        """!
        @brief Get the array size in the type modifier value
        @param varDict {dict} Dictionary object to modify
        @return int - Array size
        """
        typeMod = varDict['typeMod']
        typeMod = typeMod | ((arraySize & ParamRetDict.typeModArrayMask) << ParamRetDict.typeModArrayShift)
        varDict['typeMod'] = typeMod
