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

TIBETAN_MODE = 0
ENGLISH_MODE = 1

MSTATE_M = 1
MSTATE_CAPITAL_M = 2

class TibetanTextService(TextService):
    compositionChar = ''
    tibetanKeymap = None
    imdict = None
    candidates = []
    mState = None

    langMode = None

    candidatesPageSize = 10
    candidatesPage = 0
    candidateCursor = 0

    def __init__(self, client):
        TextService.__init__(self, client)
        self.icon_dir = os.path.abspath(os.path.dirname(__file__))

    def onActivate(self):
        TextService.onActivate(self)
        self.tibetanKeymap = TibetKeyMap()
        self.imdict = IMDict()
        self.customizeUI(candFontSize=20, candPerRow=10, candUseCursor=True)
        self.setSelKeys("1234567890")

    def onDeactivate(self):
        TextService.onDeactivate(self)

    # 使用者按下按鍵，在 app 收到前先過濾那些鍵是輸入法需要的。
    # return True，系統會呼叫 onKeyDown() 進一步處理這個按鍵
    # return False，表示我們不需要這個鍵，系統會原封不動把按鍵傳給應用程式
    def filterKeyDown(self, keyEvent):
        print("filterKeyDown:", keyEvent.__dict__)
        # 使用者開始輸入，還沒送出前的編輯區內容稱 composition string
        # isComposing() 是 False，表示目前沒有正在編輯中文
        # 另外，若使用 "`" key 輸入特殊符號，可能會有編輯區是空的，但選字清單開啟，輸入法需要處理的情況
        # 此時 isComposing() 也會是 True
        if self.isComposing():
            return True
        # --------------   以下都是「沒有」正在輸入中文的狀況   --------------

        # 如果按下 Alt，可能是應用程式熱鍵，輸入法不做處理
        if keyEvent.isKeyDown(VK_MENU):
            return False

        # 如果按下 Ctrl 鍵
        if keyEvent.isKeyDown(VK_CONTROL):
            # 開啟 Ctrl 快速輸入符號，輸入法需要此按鍵
            if keyEvent.isPrintableChar() and self.langMode == CHINESE_MODE:
                return True
            else: # 否則可能是應用程式熱鍵，輸入法不做處理
                return False

        # 若按下 Shift 鍵
        if keyEvent.isKeyDown(VK_SHIFT):
            # 若開啟 Shift 快速輸入符號，輸入法需要此按鍵
            if keyEvent.isPrintableChar() and self.langMode == CHINESE_MODE:
                return True

        # 不論中英文模式，NumPad 都允許直接輸入數字，輸入法不處理
        if keyEvent.isKeyToggled(VK_NUMLOCK): # NumLock is on
            # if this key is Num pad 0-9, +, -, *, /, pass it back to the system
            if keyEvent.keyCode >= VK_NUMPAD0 and keyEvent.keyCode <= VK_DIVIDE:
                return False # bypass IME

        # --------------   以下皆為半形模式   --------------

        # 如果是英文半形模式，輸入法不做任何處理
        if self.langMode == ENGLISH_MODE:
            return False
        # --------------   以下皆為中文模式   --------------

        print("filterKeyDown:", keyEvent.isKeyToggled(VK_CAPITAL), keyEvent.isChar(), chr(keyEvent.charCode).isalpha(), keyEvent.isPrintableChar())

        # 中文模式下開啟 Capslock，須切換成英文
        if keyEvent.isKeyToggled(VK_CAPITAL):
            # 如果此按鍵是英文字母，中文模式下要從大寫轉小寫，需要輸入法處理
            if keyEvent.isChar() and chr(keyEvent.charCode).isalpha():
                return True
            # 是其他符號或數字，則視同英文模式，不用處理
            else:
                return False

        # 中文模式下，當中文編輯區是空的，輸入法只需處理注音符號和標點
        # 大略可用是否為 printable char 來檢查
        # 注意: 此處不能直接寫死檢查按鍵是否為注音或標點，因為在不同 keyboard layout，例如
        # 倚天鍵盤或許氏...等，代表注音符號的按鍵全都不同
        if keyEvent.isPrintableChar() and keyEvent.keyCode != VK_SPACE:
            return True

        # 其餘狀況一律不處理，原按鍵輸入直接送還給應用程式
        return False

    def candidatesTurnPage(self, page):
        print("candidate turn to page:", page)
        self.setShowCandidates(True)
        self.setCandidateList(self.candidates[page*self.candidatesPageSize : page*self.candidatesPageSize+self.candidatesPageSize])

    def commitComposition(self, s):
        self.setCommitString(s)
        self.setCompositionString("")
        self.setShowCandidates(False)
        self.candidates = []
        self.candidateCursor = 0

    def onKeyDown(self, keyEvent):
        print("keydown:", keyEvent.__dict__)
        print("showCandidates:", self.showCandidates)
        print("compositionString", self.compositionString)

        # handle candidate list
        if self.showCandidates and len(self.candidates) > 0:
            if keyEvent.keyCode == VK_ESCAPE:
                self.setShowCandidates(False)
                self.candidates = []
                self.candidateCursor = 0
            elif ord('0') <= keyEvent.keyCode <= ord('9'):
                i = 9 if keyEvent.keyCode == ord('0') else keyEvent.keyCode - ord('1')
                if i > min(self.candidatesPageSize-1, len(self.candidates)-1-int(self.candidateCursor/self.candidatesPageSize)*self.candidatesPageSize):
                    return False

                self.commitComposition(self.candidates[i+int(self.candidateCursor/self.candidatesPageSize)*self.candidatesPageSize])
                return True
            elif keyEvent.keyCode == VK_LEFT:
                if self.candidateCursor > 0 and self.candidateCursor % self.candidatesPageSize == 0:
                    self.candidatesTurnPage(int((self.candidateCursor-1)/self.candidatesPageSize))
                self.candidateCursor = self.candidateCursor-1 if self.candidateCursor > 0 else 0
                self.setCandidateCursor(self.candidateCursor % self.candidatesPageSize)
                return True
            elif keyEvent.keyCode == VK_RIGHT:
                if self.candidateCursor < len(self.candidates)-1 and self.candidateCursor % self.candidatesPageSize == self.candidatesPageSize-1:
                    self.candidatesTurnPage(int((self.candidateCursor+1)/self.candidatesPageSize))
                self.candidateCursor = (self.candidateCursor+1) if self.candidateCursor < len(self.candidates)-1 else len(self.candidates)-1
                self.setCandidateCursor(self.candidateCursor % self.candidatesPageSize)
                return True
            elif keyEvent.keyCode == VK_UP:
                if int(self.candidateCursor/self.candidatesPageSize) > 0:
                    self.candidatesTurnPage(int(self.candidateCursor/self.candidatesPageSize)-1)
                    self.candidateCursor = self.candidateCursor-self.candidatesPageSize
                    self.setCandidateCursor(self.candidateCursor % self.candidatesPageSize)
                return True
            elif keyEvent.keyCode == VK_DOWN:
                if int(self.candidateCursor/self.candidatesPageSize) < int((len(self.candidates)-1) / self.candidatesPageSize):
                    self.candidatesTurnPage(int(self.candidateCursor/self.candidatesPageSize)+1)
                    self.candidateCursor = min(len(self.candidates)-1, self.candidateCursor+self.candidatesPageSize) 
                    self.setCandidateCursor(self.candidateCursor % self.candidatesPageSize)
                return True

        # handle normal keyboard input
        if not self.isComposing():
            if keyEvent.keyCode == VK_RETURN or keyEvent.keyCode == VK_BACK:
                return False

            if chr(keyEvent.keyCode).lower() == 'm':
                if self.mState is None:
                    self.mState = MSTATE_CAPITAL_M if keyEvent.isKeyDown(VK_SHIFT) else MSTATE_M

                    print("switch m state to:", self.mState)
                    return True

        if keyEvent.keyCode == VK_RETURN or keyEvent.keyCode == VK_SPACE:
            self.commitComposition(self.candidates[self.candidateCursor])
            return True

        elif keyEvent.keyCode == VK_BACK and self.compositionString != "":
            self.setCompositionString(self.compositionString[:-1])
            if len(self.compositionString) == 0:
                self.setShowCandidates(False)
                self.candidates = []
                self.candidateCursor = 0
                return True
        elif not keyEvent.isPrintableChar():
            return True
        else:
            ret = self.tibetanKeymap.getKey(chr(keyEvent.keyCode).lower(),
                                            self.mState == MSTATE_M,
                                            keyEvent.isKeyDown(VK_SHIFT),
                                            keyEvent.isKeyDown(VK_MENU) and keyEvent.isKeyDown(VK_CONTROL) and keyEvent.isKeyDown(VK_SHIFT),
                                            self.mState == MSTATE_M)
            if ret is None:
                self.commitComposition(self.compositionString+chr(keyEvent.keyCode))
                return True

            self.mState = None

            self.setCompositionString(self.compositionString + ret)
            self.setCompositionCursor(len(self.compositionString))

        candidates = self.imdict.predict(self.compositionString)
        print("candidates count:", len(candidates))

        if len(candidates) == 1:
            self.commitComposition(candidates[0])
        elif len(candidates) > 0:
            self.candidates = candidates
            self.setCandidateList(candidates[:min(len(candidates), self.candidatesPageSize)])
            self.setShowCandidates(True)
            self.candidateCursor = 0
        else:
            #ignore incorrect key
            self.setCompositionString(self.compositionString[:-1])
            self.setCompositionCursor(len(self.compositionString))

        return True

    def onCommand(self, commandId, commandType):
        print("onCommand", commandId, commandType)
