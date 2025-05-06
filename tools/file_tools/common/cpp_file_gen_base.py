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

from .doxygen_gen_tools import CDoxyCommentGenerator
from ..json_data.param_return_tools import ParamRetDict
from ..json_data.jsonStringClassDescription import TranslationTextParser

#============================================================================
#============================================================================
# File generation helper class
#============================================================================
#============================================================================
class GenerateCppFileHelper(object):
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
        self.doxyCommentGen = CDoxyCommentGenerator()
        self.levelTabSize = 4
        headerGenCommentParam = CommentParams.cCommentParms
        headerGenCommentParam['blockLineStart'] = "* "
        self.headerCommentGen = CommentGenerator(headerGenCommentParam, 80)

        self.typeXlationDict = {'string':"std::string",
                                'text':"std::string",
                                'size':"size_t",
                                'integer':"int",
                                'unsigned':"unsigned"}

    def _declareType(self, baseType:str, typeMod:int=0)->str:
        """!
        @brief Generate the type text based on the input type name and type modification data
        @param baseType (str) Delclaration type
        @param typeMod (int) ParamRetDict type modification code
        @return string C++ type specification
        """
        typeReturn = baseType
        if baseType in list(self.typeXlationDict.keys()):
            typeReturn = self.typeXlationDict[baseType]

        arraySize = ParamRetDict.getArraySize(typeMod)
        if arraySize > 0:
            if ParamRetDict.isModPointer(typeMod):
                return "std::array<"+typeReturn+"*, "+str(arraySize)+">"
            elif ParamRetDict.isModReference(typeMod):
                return "std::array<"+typeReturn+"&, "+str(arraySize)+">"
            else:
                return "std::array<"+typeReturn+", "+str(arraySize)+">"
        elif ParamRetDict.isModList(typeMod):
            if ParamRetDict.isModPointer(typeMod):
                return "std::list<"+typeReturn+"*>"
            elif ParamRetDict.isModReference(typeMod):
                return "std::list<"+typeReturn+"&>"
            else:
                return "std::list<"+typeReturn+">"
        else:
            if ParamRetDict.isModPointer(typeMod):
                return typeReturn+"*"
            elif ParamRetDict.isModReference(typeMod):
                return typeReturn+"&"
            else:
                return typeReturn

    def _xlateParams(self, paramDictList:list)->list:
        """!
        @brief Translate the generic parameter list type strings to the cpp specific parameter type strings
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
        @brief Translate the generic return dictionary to the cpp specific return dictionary
        @param retDict {dictionary} ParamRetDict return dictionary to translate
        @return dictionary - ParamRetDict return dictionary with the translated type or None if input is None
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
        if returnDict is not None:
            typeName = ParamRetDict.getReturnType(returnDict)
            typeMod = ParamRetDict.getReturnTypeMod(returnDict)
            returnText = self._declareType(typeName, typeMod)
            returnText += " "
        else:
            returnText = ""
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
            paramText += self._declareType(typeName, typeMod)
            paramText += " "
            paramText += ParamRetDict.getParamName(paramDict)
            paramPrefix = ", "
        paramText += ")"
        return paramText

    def _declareFunctionWithDecorations(self, name:str, briefdesc:str, paramDictList:list, retDict:dict|None = None,
                                        indent:int = 0, noDoxygen:bool = False, prefixDecaration:str|None = None,
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

        # Add doxygen comment block
        if not noDoxygen:
            xlatedParamList = self._xlateParams(paramDictList)
            xlatedRet = self._xlateReturnDict(retDict)
            funcDeclareText.extend(self.doxyCommentGen.genDoxyMethodComment(briefdesc, xlatedParamList, xlatedRet, longDesc, indent))

        # Create function declaration line
        funcLine = "".rjust(indent, ' ')

        # Add function prefix definitions if defined
        if prefixDecaration is not None:
            funcLine += prefixDecaration
            funcLine += " "

        # Construct main function declaration
        funcLine += self._genFunctionRetType(retDict)
        funcLine += name

        # Add the function parameters
        funcLine += self._genFunctionParams(paramDictList)

        # Add function post fix decorations if defined
        if postfixDecaration is not None:
            funcLine += " "
            funcLine += postfixDecaration

        # Add inline code if defined
        if inlinecode is None:
            funcLine += ";\n"
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
        funcLine = ""

        # Add doxygen comment block
        if not noDoxygen:
            xlatedParamList = self._xlateParams(paramDictList)
            xlatedRet = self._xlateReturnDict(retDict)
            funcDefineText.extend(self.doxyCommentGen.genDoxyMethodComment(briefdesc, xlatedParamList, xlatedRet, longDesc))

        # Add function prefix definitions if defined
        if prefixDecaration is not None:
            funcLine += prefixDecaration
            funcLine += " "

        # Create function definition line
        funcLine += self._genFunctionRetType(retDict)
        funcLine += name
        funcLine += self._genFunctionParams(paramDictList)

        # Add function post fix decorations if defined
        if postfixDecaration is not None:
            funcLine += " "
            funcLine += postfixDecaration
        funcDefineText.append(funcLine+"\n")

        return funcDefineText

    def _endFunction(self, name:str)->str:
        """!
        @brief Get the function declaration string for the given name
        @param name (string) - Function name
        @return string - Function close with comment
        """
        return "} // end of "+name+"()\n"

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

    def _genInclude(self, includeName:str)->str:
        """!
        @brief Add Include line to the output file
        @param includeName {string} Name of the include file to add
        @param libname {string} Unused in CPP include generation
        @return string - Include statement
        """
        if -1 == includeName.find("<"):
            return "#include \""+includeName+"\"\n"
        else:
            return "#include "+includeName+"\n"

    def _genIncludeBlock(self, includeNames:list)->list:
        """!
        @brief Generate a series if include line(s) for each name in the list
        @param includeNames {list of strings} Name(s) of the include file to add
        @return list of strings - Include code block to output
        """
        includeBlock = ["// Includes\n"]
        for includeName in includeNames:
            includeBlock.append(self._genInclude(includeName))
        return includeBlock

    def _genNamespaceOpen(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return ["namespace "+namespaceName, " {\n"]

    def _genNamespaceClose(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return ["}; // end of namespace "+namespaceName+"\n"]

    def _genUsingNamespace(self, namespaceName:str)->list:
        """!
        @brief Generate namespace start code for include file
        @param namespaceName {string} Name of the namespace
        @return list of strings - Code to output
        """
        return ["using namespace "+namespaceName+";\n"]

    def _genClassOpen(self, className:str, classDesc:str|None = None, inheritence:str|None = None,
                      classDecoration:str|None = None, indent:int=0)->list:
        """!
        @brief Generate the class open code

        @param className {string} Name of the class
        @param inheritence {sting} Parent class and visability or None
        @param classDecoration {sting} Class decoration or None
        @param indent {integer} Space indentation for the declaration and comments

        @return list of strings - Code to output
        """
        codeText = []
        declIndent = "".rjust(indent, ' ')

        # Generate Doxygen class description
        if classDesc is not None:
            codeText.extend(self.doxyCommentGen.genDoxyClassComment(classDesc, blockIndent=indent))

        # Generate class start
        declLine = declIndent+"class "+className
        if inheritence is not None:
            if classDecoration is not None:
                declLine += " "
                declLine += classDecoration
                declLine += " : "
                declLine += inheritence
            else:
                declLine += " : "
                declLine += inheritence

        codeText.append(declLine+"\n")
        codeText.append("{\n")

        return codeText

    def _genClassClose(self, className:str, indent:int=0)->list:
        """!
        @brief Generate the class close code

        @param className {string} Name of the class
        @param indent {integer} Space indentation for the declaration and comments

        @return list of strings - Code to output
        """
        return ["".rjust(indent, ' ')+"}; // end of "+className+" class\n"]

    def _genClassDefaultConstructorDestructor(self, className:str, indent:int = 8, virtualDestructor:bool = False,
                                              noDoxyCommentConstructor:bool = False, noCopy:bool = False)->list:
        """!
        @brief Generate default constructor(s)/destructor declarations for a class

        @param className {string} Name of the class
        @param indent {number} Indentation space count for the declarations (default = 8)
        @param virtualDestructor {boolean} False if destructor is not virtual (default)
                                           True if virtual decoration on destructor
        @param noDoxyCommentConstructor {boolean} Doxygen comment disable. False = generate doxygen comments,
                                                  True = ommit comments
        @param noCopy {boolean} Disable copy constructors, True: copy/move constructors = delete
                                                           False: copy/move constructors = default
        @return list of strings - Code to output
        """
        # Setup params for the different constructors
        otherReference = [ParamRetDict.buildParamDict("other", "const "+className+"&", "Reference to object to copy")]
        otherMove = [ParamRetDict.buildParamDict("other", className+"&&", "Reference to object to move")]
        equateReturn = ParamRetDict.buildReturnDict(className+"&", "*this")
        destructorPrefix = None

        if noCopy:
            copyConstructorPostfix = "= delete"
        else:
            copyConstructorPostfix = "= default"

        if virtualDestructor:
            destructorPrefix = "virtual"

        # Declare default default constructor
        codeText = self._declareFunctionWithDecorations(className,
                                                       "Construct a new "+className+" object",
                                                       [],
                                                       None,
                                                       indent,
                                                       noDoxyCommentConstructor,
                                                       None,
                                                       "= default")
        if not noDoxyCommentConstructor:
            codeText.append("\n")      #whitespace for readability

        # Declare default copy constructor
        codeText.extend(self._declareFunctionWithDecorations(className,
                                                            "Copy constructor for a new "+className+" object",
                                                            otherReference,
                                                            None,
                                                            indent,
                                                            noDoxyCommentConstructor,
                                                            None,
                                                            copyConstructorPostfix))

        if not noDoxyCommentConstructor:
            codeText.append("\n")      #whitespace for readability

        # Declare default move constructor
        codeText.extend(self._declareFunctionWithDecorations(className,
                                                            "Move constructor for a new "+className+" object",
                                                            otherMove,
                                                            None,
                                                            indent,
                                                            noDoxyCommentConstructor,
                                                            None,
                                                            copyConstructorPostfix))

        if not noDoxyCommentConstructor:
            codeText.append("\n")      #whitespace for readability

        # Declare default equate constructor
        codeText.extend(self._declareFunctionWithDecorations("operator=",
                                                            "Equate constructor for a new "+className+" object",
                                                            otherReference,
                                                            equateReturn,
                                                            indent,
                                                            noDoxyCommentConstructor,
                                                            None,
                                                            copyConstructorPostfix))

        if not noDoxyCommentConstructor:
            codeText.append("\n")      #whitespace for readability

        # Declare default equate move constructor
        codeText.extend(self._declareFunctionWithDecorations("operator=",
                                                            "Equate move constructor for a new "+className+" object",
                                                            otherMove,
                                                            equateReturn,
                                                            indent,
                                                            noDoxyCommentConstructor,
                                                            None,
                                                            copyConstructorPostfix))

        if not noDoxyCommentConstructor:
            codeText.append("\n")      #whitespace for readability

        # Declare default destructor
        codeText.extend(self._declareFunctionWithDecorations("~"+className,
                                                            "Destructor for "+className+" object",
                                                            [],
                                                            None,
                                                            indent,
                                                            noDoxyCommentConstructor,
                                                            destructorPrefix,
                                                            "= default"))
        codeText.append("\n")      #whitespace for readability
        return codeText

    def _declareStructure(self, name:str, varDistList:list, indent:int=0,
                          structDesc:str|None = None,
                          prefixDecoration:str|None = None,
                          postfixDecoration:str|None = None)->list:
        """!
        @brief Generate a structure declaration

        @param name {string} Name of the structure
        @param varDistList {list} List of ParamRetDict parameter dictionaries for the data elements
        @param indent {integer} Number of spaces to indent the code declarations, default = 0
        @param structDesc {string|None} Doxygen structure description
        @param prefixDecoration {str} Structure definition prefix decorations
        @param postfixDecoration {str} Structure definition end decorations

        @return list of strings - Code to output
        """
        codeText = []
        declIndent = "".rjust(indent, ' ')
        bodyIndent = "".rjust(indent+self.levelTabSize, ' ')

        # Generate the doxygen comment
        codeText.extend(self.doxyCommentGen.genDoxyClassComment(structDesc, None, indent))

        # Generate the structure
        if prefixDecoration is not None:
            codeText.append(declIndent+prefixDecoration+" structure "+name+"\n")
        else:
            codeText.append(declIndent+"structure "+name+"\n")
        codeText.append(declIndent+"{\n")

        # Generate the body code
        for varDict in varDistList:
            codeText.append(bodyIndent+self._declareVarStatment(varDict, 60))

        # Close the struture
        if postfixDecoration is not None:
            codeText.append(declIndent+"} "+postfixDecoration+";\n")
        else:
            codeText.append(declIndent+"};\n")
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
        varDecl = varTypeDecl+" "+ParamRetDict.getParamName()+";"

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
            return listName+".emplace_back(\""+valueName+"\");"
        else:
            return listName+".emplace_back("+valueName+");"

    def _genReturnStatment(self, retValue:str, isText:bool=False)->str:
        if isText:
            return "return \""+retValue+"\";"
        else:
            return "return "+retValue+";"

    def _isReturnList(self, returnDict:dict):
        return ParamRetDict.isModList(ParamRetDict.getReturnTypeMod(returnDict))
