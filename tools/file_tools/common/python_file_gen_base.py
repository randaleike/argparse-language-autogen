"""@package commonProgramFileTools
Utility classes for programming language file generation
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

from datetime import datetime

from .comment_block import CommentParams
from .comment_block import CommentGenerator
from .copyright_tools import CopyrightGenerator
from .eula import EulaText

from .doxygen_gen_tools import PyDoxyCommentGenerator
from ..json_data.param_return_tools import ParamRetDict
from ..json_data.jsonStringClassDescription import TranslationTextParser

#============================================================================
#============================================================================
# File generation helper class
#============================================================================
#============================================================================
class GeneratePythonFileHelper(object):
    """!
    @brief File generation helper class.

    This class implements boiler plate data and helper functions used by
    the parent file specific generation class to generate the file
    """
    def __init__(self, eulaName:str|None = None):
        """!
        @brief GenerateFileHelper constructor

        @param eulaName {string} Name of the EULA from EulaText class to use.
        """
        super().__init__()

        self.copyrightGenerator = CopyrightGenerator()
        if eulaName is None:
            self.eula = EulaText("MIT_open")
        else:
            self.eula = EulaText(eulaName)

        self.doxyCommentGen = PyDoxyCommentGenerator()
        self.levelTabSize = 4
        self.headerCommentGen = CommentGenerator(CommentParams.pyCommentParms, 80, useSingleLine=True)

        self.typeXlationDict = {'string':"str",
                                'text':"str",
                                'size':"int",
                                'integer':"int",
                                'unsigned':"int",
                                'structure':"dict",
                                'tuple':"tuple"}

    def _declareType(self, baseType:str, typeMod:int=0)->str:
        """!
        @brief Generate the type text based on the input type name and type modification data
        @param baseType (str) Delclaration type
        @param typeMod (int) ParamRetDict type modification code
        @return string - : Type(s)
        """
        arraySize = ParamRetDict.getArraySize(typeMod)
        if ParamRetDict.isModList(typeMod) or (arraySize > 0):
            returnText = "list"
        else:
            langType = baseType
            if baseType in list(self.typeXlationDict.keys()):
                langType = self.typeXlationDict[baseType]

            if ParamRetDict.isOrUndefType(typeMod):
                returnText = langType+"|None"
            else:
                returnText = langType
        return returnText

    def _xlateParams(self, paramDictList:list)->list:
        """!
        @brief Translate the generic parameter list type strings to the python specific parameter type strings
        @param paramDictList {list} List of ParamRetDict parameter dictionaries to translate
        @return list - List of ParamRetDict parameter dictionaries with the translated type
        """
        xlatedParams = []
        for param in paramDictList:
            xlatedType = self._declareType(ParamRetDict.getParamType(param), ParamRetDict.getParamTypeMod(param))
            xlatedParam = ParamRetDict.buildParamDictWithMod(ParamRetDict.getParamName(param),
                                                             xlatedType,
                                                             ParamRetDict.getParamDesc(param),
                                                             0)
            xlatedParams.append(xlatedParam)
        return xlatedParams

    def _xlateReturnDict(self, retDict:dict|None)->dict|None:
        """!
        @brief Translate the generic return dictionary to the python specific return dictionary
        @param retDict {dictionary} ParamRetDict return dictionary to translate
        @return dictionary|None - ParamRetDict return dictionary with the translated type or None if input is None
        """
        if retDict is not None:
            xlatedType = self._declareType(ParamRetDict.getReturnType(retDict), ParamRetDict.getReturnTypeMod(retDict))
            return ParamRetDict.buildReturnDictWithMod(xlatedType, ParamRetDict.getReturnDesc(retDict), 0)
        else:
            return None

    def _genFunctionRetType(self, returnDict:dict|None)->str:
        """!
        @brief Generate the function return+name string
        @param returnDict (dict|None) Return ParamRetDict dictionary
        @return string - returnSpec name
        """
        returnText = ""
        if returnDict is not None:
            typeName = ParamRetDict.getReturnType(returnDict)
            typeMod = ParamRetDict.getReturnTypeMod(returnDict)
            returnText += "->"
            returnText += self._declareType(typeName, typeMod)

        returnText += ":"
        return returnText

    def _genFunctionParams(self, paramDictList:list)->str:
        """!
        @brief Generate the parameter method string
        @param paramDictList (list) List of parameter dictionaries
        @return string - (<param type> <param name>[, <param type> <param name>[, ...]])
        """
        paramPrefix = ""
        paramText = "("
        for paramDict in paramDictList:
            typeName = ParamRetDict.getParamType(paramDict)
            typeMod = ParamRetDict.getParamTypeMod(paramDict)

            paramText += paramPrefix
            paramText += ParamRetDict.getParamName(paramDict)
            paramText += ":"
            paramText += self._declareType(typeName, typeMod)
            paramPrefix = ", "
        paramText += ")"
        return paramText

    def _declareFunctionWithDecorations(self, name:str, briefdesc:str, paramDictList:list, retDict:dict|None = None,
                                       indent:int = 4, noDoxygen:bool = False, prefixDecaration:str|None = None,
                                       postfixDecaration:str|None = None, inlinecode:list|None = None,
                                       longDesc:str|None = None)->list:
        """!
        @brief Generate a function declatation text block with doxygen comment

        @param name {string} Function name
        @param desc {string} Function description
        @param paramDictList {list of dictionaries} - Return parameter data
        @param retDict {dictionary or None} - Return parameter data or None
        @param indent {integer} Comment and function declaration indentation
        @param noDoxygen {boolean} True skip doxygen comment generation, False generate doxygen comment block
        @param prefixDecaration {string} Valid C/C++ declaration prefix decoration, i.e "virtual"
        @param postfixDecaration {string} Valid C/C++ declaration postfix decoration, i.e "const" | "override" ...
        @param inlinecode {sting list or None} Inline code for the declaration or None id there is no inline definition
        @param longDesc {string or None} Long description of the function

        @return string list - Function doxygen comment block and declaration
        """
        funcDeclareText = []
        declIndent = "".rjust(indent, ' ')

        # Add fungenDoxyMethodCommentction prefix definitions if defined
        if prefixDecaration is not None:
            funcDeclareText.append(declIndent+prefixDecaration+"\n")

        # Create function declaration line
        funcLine = declIndent
        funcLine += "def "
        funcLine += name

        # Add the function parameters
        funcLine += self._genFunctionParams(paramDictList)
        funcLine += self._genFunctionRetType(retDict)
        funcLine += "\n"
        funcDeclareText.append(funcLine)

        # Add doxygen comment block
        if not noDoxygen:
            xlatedParamList = self._xlateParams(paramDictList)
            xlatedRet = self._xlateReturnDict(retDict)
            funcDeclareText.extend(self.doxyCommentGen.genDoxyMethodComment(briefdesc, xlatedParamList, xlatedRet,
                                                                            longDesc, indent+self.levelTabSize))

        # Add inline code if defined
        inlineIndent = "".rjust(indent+self.levelTabSize, ' ')
        if inlinecode is None:
            funcDeclareText.append(inlineIndent+self.doxyCommentGen.genSingleLineStart()+" @todo Implement code\n")
        else:
            for codeLine in inlinecode:
                funcDeclareText.append(inlineIndent+codeLine+"\n")

        return funcDeclareText

    def _defineFunctionWithDecorations(self, name:str, briefdesc:str, paramDictList:list, retDict:dict,
                                      noDoxygen:bool = False, prefixDecaration:str|None = None,
                                      postfixDecaration:str|None = None, longDesc:list|None = None)->list:
        """!
        @brief Generate a function definition start with doxygen comment

        @param name {string} Function name
        @param desc {string} Function description
        @param paramDictList {list of dictionaries} - Return parameter data
        @param retDict {dictionary} - Return parameter data
        @param noDoxygen {boolean} True skip doxygen comment generation, False generate doxygen comment block
        @param prefixDecaration {string or None} Valid C/C++ decldefineFunctionWithDecorationsaration prefix decoration, i.e "virtual"
        @param postfixDecaration {string or None} Valid C/C++ declaration postfix decoration, i.e "const" | "override" ...
        @param longDesc {string or None} Long description of the function

        @return string list - Function doxygen comment block and declaration start
        """
        funcDefineText = []

        # Add function prefix definitions if defined
        if prefixDecaration is not None:
            funcDefineText.append(prefixDecaration+"\n")

        # Create function declaration line
        funcLine = "def "
        funcLine += name

        # Add the function parameters
        funcLine += self._genFunctionParams(paramDictList)
        funcLine += self._genFunctionRetType(retDict)
        funcLine += "\n"
        funcDefineText.append(funcLine)

        # Add doxygen comment block
        if not noDoxygen:
            xlatedParamList = self._xlateParams(paramDictList)
            xlatedRet = self._xlateReturnDict(retDict)
            funcDefineText.extend(self.doxyCommentGen.genDoxyMethodComment(briefdesc, xlatedParamList, xlatedRet,
                                                                           longDesc, self.levelTabSize))
        return funcDefineText

    def _endFunction(self, name:str)->str:
        """!
        @brief Get the function declaration string for the given name
        @param name (string) - Function name
        @return string - Function close with comment
        """
        return "# end of function "+name

    def _generateGenericFileHeader(self, autotoolname:str, startYear:int=2025, owner:str|None = None)->list:
        """!
        @brief Generate the boiler plate file header with copyright and eula

        @param autotoolname {string} Auto generation tool name for comments
        @param startYear {number} First copyright year
        @param owner {string or None} File owner for copyright message or None
        @return list of strings - Code to output
        """
        commentText = []
        copyrightEulaText = []
        if owner is not None:
            # Generate copyright and EULA text
            currentYear = datetime.now().year
            copyrightEulaText.append(self.copyrightGenerator.createNewCopyright(owner, startYear, currentYear))
            copyrightEulaText.append("") # white space for readability
            copyrightEulaText.append(self.eula.formatEulaName())
            copyrightEulaText.append("") # white space for readability
            copyrightEulaText.extend(self.eula.formatEulaText())
            copyrightEulaText.append("") # white space for readability

        copyrightEulaText.append("This file was autogenerated by "+autotoolname+" do not edit")
        copyrightEulaText.append("") # white space for readability

        # Generate comment header
        for line in self.headerCommentGen.buildCommentBlockHeader():
            commentText.append(line+"\n")

        # Wrap and output commentText lines
        for line in copyrightEulaText:
            commentText.append(self.headerCommentGen.wrapCommentLine(line)+"\n")

        # Generate comment footer
        for line in self.headerCommentGen.buildCommentBlockFooter():
            commentText.append(line+"\n")
        return commentText

    def _genImport(self, className:str, moduleName:str = None)->str:
        """!
        @brief Add Include line to the output file
        @param className {string} Name of the class to import
        @param moduleName {string} Name of the module to import from
        @return string - Import statement
        """
        if moduleName is not None:
            return "from "+moduleName+"import "+className+"\n"
        else:
            return "import "+className+"\n"

    def _genImportBlock(self, includeNames:list)->list:
        """!
        @brief Generate a series if include line(s) for each name in the list
        @param includeNames {list of tuples} Name(s) of class(es), Module name(s) of the class to import
        @return list of strings - Import code block to output
        """
        includeBlock = ["// Imports\n"]
        for className, moduleName in includeNames:
            includeBlock.append(self._genImport(className, moduleName))
        return includeBlock

    def _genNamespaceOpen(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return []

    def _genNamespaceClose(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return []

    def _genUsingNamespace(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return []

    def _genClassOpen(self, className:str, classDesc:str|None=None, inheritence:str|None = None,
                      classDecoration:str|None = None, indent:int=0)->list:
        """!
        @brief Generate the class open code

        @param className {string} Name of the class
        @param inheritence {sting} Parent class and visability or None
        @param classDecoration {sting} Class decoration or None, ignored in python
        @param indent {integer} Space indentation for the declaration and comments

        @return list of strings - Code to output
        """
        codeText = []
        declIndent = "".rjust(indent, ' ')

        # Generate class start
        if inheritence is None:
            inheritence = "object"
        codeText.append(declIndent+"class "+className+"("+inheritence+"):\n")

        # Generate Doxygen class description
        if classDesc is not None:
            codeText.extend(self.doxyCommentGen.genDoxyClassComment(classDesc, None, self.levelTabSize))

        return codeText

    def _genClassClose(self, className:str, indent:int=0)->list:
        """!
        @brief Generate the class close code

        @param className {string} Name of the class
        @param indent {integer} Space indentation for the declaration and comments

        @return list of strings - Code to output
        """
        return ["".rjust(indent, ' ')+"# end of "+className+" class\n"]

    def _genClassDefaultConstructor(self, className:str, indent:int = 4, paramList:list=[],
                                   constructorCode:list= [], noDoxyCommentConstructor:bool = False)->list:
        """!
        @brief Generate default constructor(s)/destructor declarations for a class

        @param className {string} Name of the class
        @param indent {number} Indentation space count for the declarations (default = 8)
        @param paramList {list} List of parameter dictionaries
        @param constructorCode {list} Constructor code
        @param noDoxyCommentConstructor {boolean} Doxygen comment disable. False = generate doxygen comments,
                                                  True = ommit comments
        @return list of strings - Code to output
        """
        # Declare default default constructor
        codeText = self._declareFunctionWithDecorations("__init__",
                                                       "Construct a new "+className+" object",
                                                       paramList,
                                                       None,
                                                       indent,
                                                       noDoxyCommentConstructor,
                                                       None,
                                                       None,
                                                       constructorCode)
        codeText.append("\n")      #whitespace for readability
        return codeText

    def _declareStructure(self, name:str, varDistList:list, indent:int=0,
                          structDesc:str|None = None)->list:
        """!
        @brief Generate a structure declaration

        @param name {string} Name of the structure
        @param varDistList {list} List of ParamRetDict parameter dictionaries for the data elements
        @param indent {integer} Number of spaces to indent the code declarations, default = 0
        @param structDesc {string|None} Doxygen structure description

        @return list of strings - Code to output
        """
        # Generate the declaration
        codeText = self._genClassOpen(name, structDesc, "object", indent=indent)
        bodyIndent = "".rjust(indent+self.levelTabSize, ' ')

        # Generate the body code
        for varDict in varDistList:
            codeText.append(bodyIndent+self._declareVarStatment(varDict, 60))

        # Close the struture
        codeText.extend(self._genClassClose(name, indent))
        return codeText

    def _declareVarStatment(self, varDict:dict, doxyCommentIndent:int = -1)->str:
        """!
        @brief Declare a class/interface variable
        @param varDict {dict} ParamRetDict parameter dictionary describing the variable
        @param doxyCommentIndent {int} Column to begin the doxygen comment
        @return string Variable declatation code
        """
        # Declare the variable
        typeName = ParamRetDict.getParamType(varDict)
        typeMod = ParamRetDict.getParamTypeMod(varDict)

        varTypeDecl = self._declareType(typeName, typeMod)
        varDecl = ParamRetDict.getParamName()+":"+varTypeDecl

        # Test for doxycomment skip
        if doxyCommentIndent != -1:
            if doxyCommentIndent > len(varDecl):
                varDecl.ljust(doxyCommentIndent, ' ')
            else:
                varDecl+= " "
            varDecl += self.doxyCommentGen.genDoxyVarDocStr(ParamRetDict.getParamDesc(varDict))

        # Return the final data
        return varDecl

    def _genAddListStatment(self, listName:str, valueName:str, isText:bool=False)->str:
        if isText:
            return listName+".append(\""+valueName+"\")"
        else:
            return listName+".append("+valueName+")"

    def _genReturnStatment(self, retValue:str, isText:bool=False)->str:
        if isText:
            return "return \""+retValue+"\""
        else:
            return "return "+retValue

    def _isReturnList(self, returnDict:dict):
        return ParamRetDict.isModList(ParamRetDict.getReturnTypeMod(returnDict))
