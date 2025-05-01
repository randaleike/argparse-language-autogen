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

class JsonHelper(object):
    """!
    Json file processing generic helper functions
    """
    def __init__(self):
        pass

    def _getCommitOverWriteFlag(self, entryName:str, override:bool = False):
        """!
        @brief Determine if the user is ready to commit the new entry over the existing one
        @param entryName {string} Name of the method that will be added
        @param override {boolean} True = force commit, False = ask user
        """
        commitFlag = False
        if override:
            commitFlag = True
        else:
            # Determine if we should overwrite existing
            commit = input("Overwrite existing "+entryName+" entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                commitFlag = True
        return commitFlag

    def _getCommitNewFlag(self, entryName:str):
        """!
        @brief Determine if the user is ready to commit the new entry
        @param entryName {string} Name of the method that will be added
        """
        commit = input("Add new "+entryName+" entry? [Y/N]").upper()
        if ((commit == 'Y') or (commit == "YES")):
            return True
        else:
            return False

    def _getCommitFlag(self, entryName:str, entryKeys:list, override:bool = False):
        """!
        @brief Determine if the user is ready to commit the new entry
        @param entryName {string} Name of the method that will be added
        @param entryKeys {list of keys} List of the existing entry keys
        @param override {boolean} True = force commit, False = ask user
        """
        if entryName in entryKeys:
            return self._getCommitOverWriteFlag(entryName, override)
        else:
            return self._getCommitNewFlag(entryName)
