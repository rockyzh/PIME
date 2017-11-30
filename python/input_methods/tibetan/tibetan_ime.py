#! python3
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from keycodes import *  # for VK_XXX constants
from textService import *
import io
import os.path
import copy

from .trie import *

class TibetanTextService(TextService):

    compositionChar = ''
    tibetanKeymap = None
    imdict = None
    candidates = []
    mState = None

    def __init__(self, client):
        TextService.__init__(self, client)
        self.icon_dir = os.path.abspath(os.path.dirname(__file__))

    def onActivate(self):
        TextService.onActivate(self)
        self.tibetanKeymap = TibetKeyMap()
        self.imdict = IMDict()
        self.customizeUI(candFontSize = 20, candPerRow = 1)
        self.setSelKeys("1234567890")
        # self.setSelKeys("asdfjkl;")

    def onDeactivate(self):
        TextService.onDeactivate(self)

    def filterKeyDown(self, keyEvent):
        if not self.isComposing():
            if keyEvent.keyCode == VK_RETURN or keyEvent.keyCode == VK_BACK or not keyEvent.isChar():
                return False
        return True

    def onKeyDown(self, keyEvent):
        print("keydown:", keyEvent.__dict__)
        print("showCandidates:", self.showCandidates)
        print("compositionString", self.compositionString)

        # handle candidate list
        if self.showCandidates:
            if keyEvent.keyCode == VK_ESCAPE:
                self.setShowCandidates(False)
            elif keyEvent.keyCode >= ord('1') and keyEvent.keyCode <= ord('9'):
                i = keyEvent.keyCode - ord('1')
                if i >= len(self.candidates):
                    return false

                self.setCommitString(self.candidates[i])
                self.setCompositionString("")
                self.setShowCandidates(False)
                return True

        # handle normal keyboard input
        if not self.isComposing():
            if keyEvent.keyCode == VK_RETURN or keyEvent.keyCode == VK_BACK:
                return False
        if keyEvent.keyCode == VK_RETURN or keyEvent.keyCode == ord(' '):
            self.setCommitString(self.compositionString)
            self.setCompositionString("")
            self.setShowCandidates(False)
            return True
        elif keyEvent.keyCode == VK_BACK and self.compositionString != "":
            self.setCompositionString(self.compositionString[:-1])
        elif not keyEvent.isChar():
            return True
        else:
            ret = self.tibetanKeymap.getKey(chr(keyEvent.keyCode).lower(),
                                            False,
                                            keyEvent.isKeyDown(VK_SHIFT),
                                            keyEvent.isKeyDown(VK_MENU) and keyEvent.isKeyDown(VK_CONTROL) and keyEvent.isKeyDown(VK_SHIFT),
                                            False)
            if ret is None:
                self.setCommitString(self.compositionString+chr(keyEvent.keyCode))
                self.setCompositionString("")
                self.setShowCandidates(False)
                return True

            self.setCompositionString(self.compositionString + ret)
            self.setCompositionCursor(len(self.compositionString))

        candidates = self.imdict.predict(self.compositionString)
        print("candidates:", candidates, "len:", len(candidates))

        if len(candidates) == 1:
            self.setCommitString(candidates[0])
            self.setCompositionString("")
            self.setShowCandidates(False)
        elif len(candidates) > 0:
            self.candidates = candidates
            self.setCandidateList(candidates[:min(len(candidates), 9)])
            self.setShowCandidates(True)
        else:
            self.setCommitString(self.compositionString)
            self.setCompositionString("")
            self.setShowCandidates(False)

        return True

    def onCommand(self, commandId, commandType):
        print("onCommand", commandId, commandType)
