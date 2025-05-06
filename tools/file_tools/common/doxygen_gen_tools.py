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

from ..json_data.param_return_tools import ParamRetDict
from .comment_block import CommentParams
from .text_format import MultiLineFormat

#============================================================================
#============================================================================
# Doxygen comment block helper classes
#============================================================================
#============================================================================
class DoxyCommentGenerator():
    def __init__(self, blockStart:str, blockEnd:str, blockLineStart:str, singleLineStart:str, addParamType:bool=False):
        """!
        @brief DoxyCommentGenerator constructor
        @param blockStart {string} Comment block start marker for the input file type.
        @param blockEnd {string} Comment block end marker for the input file type.
        @param blockLineStart {string} Comment block line start marker for the input file type.
        @param singleLineStart {string} Single line comment block start marker for the input file type.
        @param addParamType {boolean} True add the parameter type to the doxygen param comment text
                                      False do not add parameter type to the doxygen param comment text
        """
        self.blockStart = blockStart
        self.blockEnd = blockEnd
        self.blockLineStart = blockLineStart
        self.singleLineStart = singleLineStart

        self.formatMaxLength = 120
        self.addParamType = addParamType
        self.descFormatMax = self.formatMaxLength-len(self.blockStart)
        self.groupCounter = 0

    def _genCommentBlockPrefix(self)->str:
        """!
        @brief Generate doxygen block prefix string

        @param blockIndent Current comment block indentation

        @return string - Formatted block prefix
        """
        if self.blockLineStart is not None:
            prefix = self.blockLineStart
        else:
            prefix = self.singleLineStart
        return " "+prefix+" "

    def _genBlockStart(self)->str:
        """!
        @brief Generate doxygen block start string
        @return string - Formatted block prefix
        """
        # Set the start
        if self.blockStart is not None:
            blockStart = self.blockStart
        else:
            blockStart = self.singleLineStart
        return blockStart

    def _genBlockEnd(self)->str:
        """!
        @brief Generate doxygen block start string
        @return string - Formatted block prefix
        """
        # Set the end
        if self.blockEnd is not None:
            blockEnd = " "+self.blockEnd
        else:
            blockEnd = ""
        return blockEnd

    def _genBriefDesc(self, briefDesc:str, prefix:str)->list:
        """!
        @brief Generate the doxygen comment block

        @param briefDesc {string} @brief description for the comment block
        @param prefix {string} Current comment block indentation prefix
        @return list of strings - Long description comment as a list of formatted strings
        """
        briefDescList = []

        # Generate the brief description text
        briefStart = "@brief "
        formattedBriefTxt = MultiLineFormat(briefDesc, self.descFormatMax-len(briefStart))
        firstdesc = True
        for briefLine in formattedBriefTxt:
            briefDescList.append(prefix+briefStart+briefLine+"\n")

            if firstdesc:
                firstdesc = False
                briefStart = "       "

        return briefDescList

    def _genLongDesc(self, prefix:str, longDesc:str|None = None)->list:
        """!
        @brief Generate the doxygen comment block

        @param prefix {string} Current comment block prefix string
        @param longDesc {string} Detailed description for the comment block or None if no detailed description

        @return list of strings - Long description comment as a list of formatted strings
        """
        longDescList = []

        # Generate the long description text
        if longDesc is not None:
            formattedLongTxt = MultiLineFormat(longDesc, self.descFormatMax)
            for longDescLine in formattedLongTxt:
                longDescList.append(prefix+longDescLine+"\n")
        return longDescList

    def _genCommentReturnText(self, retDict:dict, prefix:str)->list:
        """!
        @brief Generate @return doxygen text

        @param retDict {dictionary} - Return parameter data
        @param prefix {string} Current comment block prefix string

        @return list of strings - Formatted string list for the comment block
        """
        # Construct first return line
        returnType, returnDesc, typeMod = ParamRetDict.getReturnData(retDict)
        l1 = "@return "+returnType+" - "

        # Format the description into sized string(s)
        descList = MultiLineFormat(returnDesc, self.descFormatMax-len(l1))

        # Construct the final block return text
        retList = []
        firstdesc = True
        descPrefix = prefix+l1
        for descStr in descList:
            retList.append(descPrefix+descStr+"\n")
            if firstdesc:
                firstdesc = False
                descPrefix = prefix+"".rjust(len(l1), ' ')

        # return the final formated data string list
        return retList

    def _genCommentParamText(self, paramDict:dict, prefix:str)->list:
        """!
        @brief Generate @param doxygen text

        @param paramDict {dictionary} - Return parameter data
        @param prefix {string} Current comment block prefix string

        @return list of strings - Formatted string list for the comment block
        """
        # Construct first param line
        paramName, paramType, paramDesc, typeMod = ParamRetDict.getParamData(paramDict)
        l1 = "@param "+paramName
        if self.addParamType:
            l1 += " {"+paramType+"}"
        l1 += " "

        # Format the description into sized string(s)
        descList = MultiLineFormat(paramDesc, self.descFormatMax-len(l1))

        # Add the description string(s)
        firstdesc = True
        retList = []
        paramPrefix = prefix+l1
        for descStr in descList:
            retList.append(paramPrefix+descStr+"\n")
            if firstdesc:
                firstdesc = False
                paramPrefix = prefix+"".rjust(len(l1), ' ')

        # return the final formated data string list
        return retList

    def genDoxyMethodComment(self, briefDesc:str, paramDictList:list, retDict:dict|None = None,
                             longDesc:str|None = None, blockIndent:int = 0)->list:
        """!
        @brief Generate the doxygen comment block

        @param briefDesc {string} @brief description for the comment block
        @param paramDictList {list of dictionaries} - Return parameter data
        @param retDict {dictionary} - Return parameter data
        @param longDesc {string} Detailed description for the comment block or None if no detailed description
        @param blockIndent Current comment block indentation

        @return list of strings - Comment block as a list of formatted strings
        """
        # Generate the block start
        padPrefix = "".rjust(blockIndent, ' ')
        blockStrList = [padPrefix+self._genBlockStart()+"\n"]

        # Generate the block prefix text fot the rest
        prefix = padPrefix+self._genCommentBlockPrefix()

        # Add the brief text
        blockStrList.extend(self._genBriefDesc(briefDesc, prefix))
        blockStrList.append(prefix+"\n") # add empty line for readability

        # Add the long description
        if longDesc is not None:
            blockStrList.extend(self._genLongDesc(prefix, longDesc))
            blockStrList.append(prefix+"\n") # add empty line for readability

        # Add Param data
        if (len(paramDictList) > 0):
            for paramDict in paramDictList:
                blockStrList.extend(self._genCommentParamText(paramDict, prefix))
            blockStrList.append(prefix+"\n") # add empty line for readability

        # Add return data
        if retDict is not None:
            blockStrList.extend(self._genCommentReturnText(retDict, prefix))

        # Complete the block
        blockStrList.append(padPrefix+self._genBlockEnd()+"\n")
        return blockStrList

    def genDoxyClassComment(self, briefDesc:str|None, longDesc:str|None = None, blockIndent:int = 0)->list:
        """!
        @brief Generate a doxygen cgenDoxyClassCommentlass/structure documentation block

        @param briefDesc {string} @brief description for the comment block
        @param longDesc {string} Detailed description for the comment block or None if no detailed description
        @param blockIndent Current cmment block indentation

        @return list of strings - Comment block as a list of formatted strings
        """
        # Generate the block start
        padPrefix = "".rjust(blockIndent, ' ')
        blockStrList = [padPrefix+self._genBlockStart()+"\n"]

        # Generate the block prefix text fot the rest
        prefix = padPrefix+self._genCommentBlockPrefix()

        # Add the brief text
        if briefDesc is not None:
            blockStrList.extend(self._genBriefDesc(briefDesc, prefix))

        # Add the long description
        if longDesc is not None:
            if briefDesc is not None:
                blockStrList.append(prefix+"\n") # add empty line for readability
            blockStrList.extend(self._genLongDesc(prefix, longDesc))

        # Complete the block
        blockStrList.append(padPrefix+self._genBlockEnd()+"\n")
        return blockStrList

    def genDoxyDefgroup(self, fileName:str, group:str|None = None, groupdef:str|None = None)->list:
        """!
        @brief Doxygen defgroup comment block
        @param fileName {string} File name and extention
        @param group {string} Name of the group to define
        @param groupdef {string} Description of the new group
        @return list of strings - Code to output
        """
        doxyGroupBlk = [self._genBlockStart()+"\n"]

        # Generate the block prefix text fot the rest
        prefix = self._genCommentBlockPrefix()
        doxyGroupBlk.append(prefix+"@file "+fileName+"\n")
        if group is not None:
            if groupdef is not None:
                doxyGroupBlk.append(prefix+"@defgroup "+group+" "+groupdef+"\n")
            doxyGroupBlk.append(prefix+"@ingroup "+group+"\n")
            doxyGroupBlk.append(prefix+"@{\n")
            self.groupCounter += 1
        doxyGroupBlk.append(self._genBlockEnd()+"\n")
        return doxyGroupBlk

    def genDoxyGroupEnd(self)->str|None:
        """!
        @brief Doxygen group comment block end marker
        @return string or None - Code to output
        """
        if self.groupCounter > 0:
            doxyEnd = self._genBlockStart()+"@}"+self._genBlockEnd()+"\n"
            self.groupCounter -= 1
            return doxyEnd
        else:
            return None

    def genSingleLineStart(self)->str:
        """!
        @brief Generate doxygen single line comment start string
        @return string - Formatted block prefix
        """
        # Set the start
        return self.singleLineStart

    def genDoxyVarDocStr(self, desc:str)->str:
        """!
        @brief Generate Doxygen variable comment
        @param desc {string} Variable description
        @return string Documentation string
        """
        return self.singleLineStart+"< "+desc

class CDoxyCommentGenerator(DoxyCommentGenerator):
    """!
    C/C++ file Doxygen comment generator class
    """
    def __init__(self):
        super().__init__('/**', '*/', '*', '//!', False)

class PyDoxyCommentGenerator(DoxyCommentGenerator):
    """!
    Python file Doxygen comment generator class
    """
    def __init__(self):
        super().__init__('"""!', '"""', '', '##!', True)

class TsDoxyCommentGenerator(CDoxyCommentGenerator):
    """!
    Typescript file Doxygen comment generator class
    """
    def __init__(self):
        super().__init__('/**', '*/', '*', '//!', True)

class JsDoxyCommentGenerator(CDoxyCommentGenerator):
    """!
    Javascript file Doxygen comment generator class
    """
    def __init__(self):
        super().__init__('/**', '*/', '*', '//!', True)
