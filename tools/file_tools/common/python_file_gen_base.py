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

    def declareType(self, varDict:dict)->str:
        """!
        @brief Generate the type text based on the variable input ParamRetDict dictionary
        @param varDict (dict) Variable ParamRetDict description dictionary
        @return string - : Type(s)
        """
        if ParamRetDict.isOrUndef(varDict):
            returnText += ParamRetDict.getReturnType(varDict)+"|None"
        else:
            returnText += ParamRetDict.getReturnType(varDict)
        return returnText

    def _genFunctionRetType(self, returnDict:dict|None)->str:
        """!
        @brief Generate the function return+name string
        @param returnDict (dict|None) Return ParamRetDict dictionary
        @return string - returnSpec name
        """
        returnText = ""
        if returnDict is not None:
            returnText += "->"
            returnText += self.declareType(returnDict)

        returnText += ":"
        return returnText

    def genFunctionParams(self, paramDictList:list)->str:
        """!
        @brief Generate the parameter method string
        @param paramDictList (list) List of parameter dictionaries
        @return string - (<param type> <param name>[, <param type> <param name>[, ...]])
        """
        paramPrefix = ""
        paramText = "("
        for paramDict in paramDictList:
            paramText += paramPrefix
            paramText += ParamRetDict.getParamName(paramDict)
            paramText += ":"
            paramText += self.declareType(paramDict)
            paramPrefix = ", "
        paramText += ")"
        return paramText


    def declareFunctionWithDecorations(self, name:str, briefdesc:str, paramDictList:list, retDict:dict|None = None,
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

        # Create function declaration line
        funcLine = "".rjust(indent, ' ')
        funcLine += "def "

        # Add function prefix definitions if defined
        if prefixDecaration is not None:
            funcLine += prefixDecaration
            funcLine += " "

        # Construct main function declaration
        funcLine += name

        # Add the function parameters
        funcLine += self.genFunctionParams(paramDictList)
        funcLine += self._genFunctionRetType(retDict)

        # Add doxygen comment block
        if not noDoxygen:
            funcDeclareText.extend(self.doxyCommentGen.genDoxyMethodComment(briefdesc, paramDictList, retDict,
                                                                            longDesc, indent+self.levelTabSize))

        # Add inline code if defined
        if inlinecode is None:
            funcLine += self.doxyCommentGen.genSingleLineStart()+" @todo Implement code\n"
            funcDeclareText.append(funcLine)
        else:
            funcLine += "\n"
            funcDeclareText.append(funcLine)
            inlineIndent = "".rjust(indent, ' ')
            inlineStart = inlineIndent+"{"
            if len(inlinecode) == 1:
                funcDeclareText.append(inlineStart+inlinecode[0]+"}\n")
            else:
                funcDeclareText.append(inlineStart+"\n")
                inlineBodyIndent = "".rjust(indent+self.levelTabSize, ' ')
                for codeLine in inlinecode:
                    codeLine += "\n"
                    funcDeclareText.append(inlineBodyIndent+codeLine)
                funcDeclareText.append(inlineIndent+"}\n")

        return funcDeclareText

    def defineFunctionWithDecorations(self, name:str, briefdesc:str, paramDictList:list, retDict:dict,
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

        # Create function declaration line
        funcLine = "def "

        # Add function prefix definitions if defined
        if prefixDecaration is not None:
            funcLine += prefixDecaration
            funcLine += " "

        # Construct main function declaration
        funcLine += name

        # Add the function parameters
        funcLine += self.genFunctionParams(paramDictList)
        funcLine += self._genFunctionRetType(retDict)

        # Add doxygen comment block
        if not noDoxygen:
            funcDefineText.extend(self.doxyCommentGen.genDoxyMethodComment(briefdesc, paramDictList, retDict,
                                                                           longDesc, self.levelTabSize))
        return funcDefineText

    def endFunction(self, name:str)->str:
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

    def genImportBlock(self, includeNames:list)->list:
        """!
        @brief Generate a series if include line(s) for each name in the list
        @param includeNames {list of tuples} Name(s) of class(es), Module name(s) of the class to import
        @return list of strings - Import code block to output
        """
        includeBlock = ["// Imports\n"]
        for className, moduleName in includeNames:
            includeBlock.append(self._genImport(className, moduleName))
        return includeBlock

    def genNamespaceOpen(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return []

    def genNamespaceClose(self, namespaceName:str)->list:
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

    def genClassOpen(self, className:str, classDesc:str, inheritence:str|None = None,
                     classDecoration:str|None = None, noDoxyCommentConstructor:bool = False)->list:
        """!
        @brief Generate the class open code

        @param className {string} Name of the class
        @param inheritence {sting} Parent class and visability or None
        @param classDecoration {sting} Class decoration or None
        @param noDoxyCommentConstructor {boolean} Doxygen comment disable. False = generate doxygen comments,
                                                  True = ommit comments
        @return list of strings - Code to output
        """
        codeText = []

        # Generate class start
        if inheritence is None:
            inheritence = "object"
        codeText.append("class "+className+"("+inheritence+"):\n")

        # Generate Doxygen class description
        if not noDoxyCommentConstructor:
            codeText.extend(self.doxyCommentGen.genDoxyClassComment(classDesc, None, self.levelTabSize))

        return codeText

    def genClassClose(self, className:str)->list:
        """!
        @brief Generate the class close code

        @param className {string} Name of the class
        @return list of strings - Code to output
        """
        return ["# end of "+className+" class\n"]

    def genClassDefaultConstructor(self, className:str, indent:int = 4, paramList:list=[],
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
        codeText = self.declareFunctionWithDecorations("__init__",
                                                       "Construct a new "+className+" object",
                                                       paramList,
                                                       None,
                                                       indent,
                                                       noDoxyCommentConstructor,
                                                       "public",
                                                       None,
                                                       constructorCode)
        codeText.append("\n")      #whitespace for readability
        return codeText

    def declareVarStatment(self, varDict:dict, doxyCommentIndent:int = -1)->str:
        """!
        @brief Declare a class/interface variable
        @param varDict {dict} ParamRetDict parameter dictionary describing the variable
        @param doxyCommentIndent {int} Column to begin the doxygen comment
        @return string Variable declatation code
        """
        # Declare the variable
        varTypeDecl = self.declareType(varDict)
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

    def getAddStringListStatment(self, listName:str, valueName:str)->str:
        return listName+".append(\""+valueName+"\")"

    def getStringReturnStatment(self, string:str)->str:
        return "return \""+string+"\""

    def getAddValueListStatment(self, listName:str, valueName:str)->str:
        return listName+".append("+valueName+")"

    def getValueReturnStatment(self, valueName:str)->str:
        return "return "+valueName
