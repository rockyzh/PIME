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

    def __init__(self, client):
        TextService.__init__(self, client)
        self.icon_dir = os.path.abspath(os.path.dirname(__file__))

    def onActivate(self):
        TextService.onActivate(self)
        self.tibetanKeymap = TibetKeyMap()
        self.imdict = IMDict()
        self.customizeUI(candFontSize=20, candPerRow=1)
        self.setSelKeys("1234567890")
        # self.setSelKeys("asdfjkl;")

    def onDeactivate(self):
        TextService.onDeactivate(self)

    # 使用者按下按鍵，在 app 收到前先過濾那些鍵是輸入法需要的。
    # return True，系統會呼叫 onKeyDown() 進一步處理這個按鍵
    # return False，表示我們不需要這個鍵，系統會原封不動把按鍵傳給應用程式
    def filterKeyDown(self, keyEvent):
        # 紀錄最後一次按下的鍵和按下的時間，在 filterKeyUp() 中要用
        self.lastKeyDownCode = keyEvent.keyCode

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
            if chr(keyEvent.keyCode).lower() == 'm':
                if self.mState is not None:
                    self.mState = None
                else:
                    self.mState = MSTATE_CAPITAL_M if keyEvent.isKeyDown(VK_SHIFT) else MSTATE_M
                return True

            ret = self.tibetanKeymap.getKey(chr(keyEvent.keyCode).lower(),
                                            self.mState == MSTATE_M,
                                            keyEvent.isKeyDown(VK_SHIFT),
                                            keyEvent.isKeyDown(VK_MENU) and keyEvent.isKeyDown(VK_CONTROL) and keyEvent.isKeyDown(VK_SHIFT),
                                            self.mState == MSTATE_M)
            if ret is None:
                self.setCommitString(self.compositionString+chr(keyEvent.keyCode))
                self.setCompositionString("")
                self.setShowCandidates(False)
                return True

            self.mState = None

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
