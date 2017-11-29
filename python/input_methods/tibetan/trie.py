#coding=utf-8 
import os 
import codecs

class Node:
    def __init__(self, label=None, data=None):
        self.label = label
        self.data = data
        self.children = dict()
    
    def addChild(self, key, data=None):
        if not isinstance(key, Node):
            self.children[key] = Node(key, data)
        else:
            self.children[key.label] = key
    
    def __getitem__(self, key):
        return self.children[key]

class Trie:
    def __init__(self):
        self.head = Node()
    
    def __getitem__(self, key):
        return self.head.children[key]
    
    def add(self, word):
        current_node = self.head
        word_finished = True
        
        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break
        
        # For ever new letter, create a new child node
        if not word_finished:
            while i < len(word):
                current_node.addChild(word[i])
                current_node = current_node.children[word[i]]
                i += 1
        
        # Let's store the full word at the end node so we don't need to
        # travel back up the tree to reconstruct the word
        current_node.data = word
    
    def has_word(self, word):
        if word == '':
            return False
        if word == None:
            raise ValueError('Trie.has_word requires a not-Null string')
        
        # Start at the top
        current_node = self.head
        exists = True
        for letter in word:
            if letter in current_node.children:
                current_node = current_node.children[letter]
            else:
                exists = False
                break
        
        # Still need to check if we just reached a word like 't'
        # that isn't actually a full word in our dictionary
        if exists:
            if current_node.data == None:
                exists = False
        
        return exists
    
    def start_with_prefix(self, prefix):
        """ Returns a list of all words in tree that start with prefix """
        words = list()
        if prefix == None:
            raise ValueError('Requires not-Null prefix')
        
        # Determine end-of-prefix node
        top_node = self.head
        for letter in prefix:
            if letter in top_node.children:
                top_node = top_node.children[letter]
            else:
                # Prefix not in tree, go no further
                return words
        
        # Get words under prefix
        if top_node == self.head:
            queue = [node for key, node in top_node.children.iteritems()]
        else:
            queue = [top_node]
        
        # Perform a breadth first search under the prefix
        # A cool effect of using BFS as opposed to DFS is that BFS will return
        # a list of words ordered by increasing length
        while queue:
            current_node = queue.pop()
            if current_node.data != None:
                # Isn't it nice to not have to go back up the tree?
                words.append(current_node.data)
            
            queue = [node for key,node in current_node.children.iteritems()] + queue
        
        return words
    
    def getData(self, word):
        """ This returns the 'data' of the node identified by the given word """
        if not self.has_word(word):
            raise ValueError('{} not found in trie'.format(word))
        
        # Race to the bottom, get data
        current_node = self.head
        for letter in word:
            current_node = current_node[letter]
        
        return current_node.data

class IMDict:
    """
    Members:
    [letterTrie] is a trie tree stored tebantoo's letters and words, could be used to predict output words.
    [extTrie] is a trie tree  using to give some advise associate words.
    """
    def __init__(self):
        self.letterTrie = Trie()
        #self.wordTrie = Trie()
        self.extTrie = Trie()

        ls = self.readFile("letter.txt")
        for word in ls:
            if self.letterTrie.has_word(word):
                print "duplicate letter:",word
            self.letterTrie.add(word)

        ws = self.readFile("word.txt")
        for word in ws:
            if self.letterTrie.has_word(word):
                print "duplicate word:",word
            self.letterTrie.add(word)

        es = self.readFile("extend.txt")
        for word in es:
            if self.extTrie.has_word(word):
                print "duplicate extend:",word
            self.extTrie.add(word)

    def readFile(self, fn):
        f = codecs.open(fn,'r','utf-8')
        lines = [ l.strip() for l in f]
        f.close()
        return lines

    def predict(self, inputs):
        prelist = list()
        
        prelist.extend(self.letterTrie.start_with_prefix(inputs))
        prelist.extend(self.extTrie.start_with_prefix(inputs))

        return prelist

class TibetKeyMap:
    # doc error 'r':u'\u0f6a' in u'\u0f62'    '0':u'\u0f20' in u'\u0f26' 
    keymap = {
    '`':u'\u0f68', '1':u'\u0f21', '2':u'\u0f22', '3':u'\u0f23', '4':u'\u0f24', '5':u'\u0f25', '6':u'\u0f26', '7':u'\u0f27', '8':u'\u0f28', '9':u'\u0f29', '0':u'\u0f20', '-':u'\u0f67', '=':u'\u0f5d',
    'q':u'\u0f45', 'w':u'\u0f46', 'e':u'\u0f7a', 'r':u'\u0f62', 't':u'\u0f4f', 'y':u'\u0f61', 'u':u'\u0f74', 'i':u'\u0f72', 'o':u'\u0f7c', 'p':u'\u0f55', '[':u'\u0f59', ']':u'\u0f5a', '\\':u'\u0f5b',
    'a':u'\u0f60', 's':u'\u0f66', 'd':u'\u0f51', 'f':u'\u0f56', 'g':u'\u0f44', 'h':u'\u0f58', 'j':u'\u0f0b', 'k':u'\u0f42', 'l':u'\u0f63', ';':u'\u0f5e', '\'':u'\u0f0d',
    'z':u'\u0f5f', 'x':u'\u0f64', 'c':u'\u0f40', 'v':u'\u0f41', 'b':u'\u0f54', 'n':u'\u0f53', ',':u'\u0f50', '.':u'\u0f47', '/':u'\u0f49',
    }

    keymap_m = {
    '`':u'\u0fb8', '1':u'\u0f04', '2':u'\u0f05', '3':u'\u0f7e', '4':u'\u0f83', '5':u'\u0f37', '6':u'\u0f35', '7':u'\u0f7f', '8':u'\u0f14', '9':u'\u0f11', '0':u'\u0f08', '-':u'\u0fb7', '=':u'\u0fba',
    'q':u'\u0f95', 'w':u'\u0f96', 'e':u'\u0f7b', 'r':u'\u0fb2', 't':u'\u0f9f', 'y':u'\u0fb1', 'u':u'\u0fad', 'i':u'\u0f80', 'o':u'\u0f7d', 'p':u'\u0fa5', '[':u'\u0fa9', ']':u'\u0faa', '\\':u'\u0fab',
    'a':u'\u0fb0', 's':u'\u0fb6', 'd':u'\u0fa1', 'f':u'\u0fa6', 'g':u'\u0f94', 'h':u'\u0fa8', 'j':u'\u0f84', 'k':u'\u0f92', 'l':u'\u0fb3', ';':u'\u0fae', '\'':u'\u0f0e',
    'z':u'\u0faf', 'x':u'\u0fb4', 'c':u'\u0f90', 'v':u'\u0f91', 'b':u'\u0fa4', 'n':u'\u0fa3', 'm':u'\u0f85', ',':u'\u0fa0', '.':u'\u0f97', '/':u'\u0f99',
    }

    # doc error 'a':u'\u0f71' in u'\u0fb0'
    keymap_shift = {
    '`':u'\u0f01', '1':u'\u0f2a', '2':u'\u0f2b', '3':u'\u0f2c', '4':u'\u0f2d', '5':u'\u0f2e', '6':u'\u0f2f', '7':u'\u0f30', '8':u'\u0f31', '9':u'\u0f32', '0':u'\u0f33', '-':u'\u0f3c', '=':u'\u0f3d',
    'q':u'\u0f15', 'w':u'\u0f16', 'e':u'\u0f17', 'r':u'\u0fbc', 't':u'\u0f4a', 'y':u'\u0fbb', 'u':u'\u0f18', 'i':u'\u0f19', 'o':u'\u0f1a', 'p':u'\u0f1b', '[':u'\u0f1c', ']':u'\u0f1d', '\\':u'\u0f1e',
    'a':u'\u0f71', 's':u'\u0f1f', 'd':u'\u0f4c', 'f':u'\u0f3e', 'g':u'\u0f3f', 'h':u'\u0fcf', 'j':u'\u0f02', 'k':u'\u0f03', 'l':u'\u0f06', ';':u'\u0f07', '\'':u'\u0f38',
    'z':u'\u0f34', 'x':u'\u0f65', 'c':u'\u0f69', 'v':u'\u0f87', 'b':u'\u0f86', 'n':u'\u0f4e', ',':u'\u0f4b', '.':u'\u0f3a', '/':u'\u0f3b',
    }

    keymap_alt_ctrl_shift = {
    '`':u'\u0f00', '1':u'\u0f76', '2':u'\u0f77', '3':u'\u0f78', '4':u'\u0f79', '5':u'\u0f81', '6':u'\u0f09', '7':u'\u0f0a', '8':u'\u0f0f', '9':u'\u0f10', '0':u'\u0f12', '-':u'\u0f0c', '=':u'\u0f13',
    'q':u'\u0f89', 'w':u'\u0f88', 'e':u'\u0fbe', 'r':u'\u0f6a', 't':u'\u0f9a', 'y':u'\u0fbf', 'u':u'\u0f75', 'i':u'\u0f73', 'o':u'\u0fc0', 'p':u'\u0fc1', '[':u'\u0fc2', ']':u'\u0fc3', '\\':u'\u0f5c',
    'a':u'\u0fc4', 's':u'\u0fc5', 'd':u'\u0f9c', 'f':u'\u0f57', 'g':u'\u0fc6', 'h':u'\u0fc7', 'j':u'\u0fc8', 'k':u'\u0f43', 'l':u'\u0fc9', ';':u'\u0fca', '\'':u'\u0fcb',
    'z':u'\u0fcc', 'x':u'\u0fb5', 'c':u'\u0fb9', 'v':u'\u0f36', 'b':u'\u0f82', 'n':u'\u0f9e', 'm':u'\u0f52', ',':u'\u0f9b', '.':u'\u0f8b', '/':u'\u0f8a',
    }

    keymap_M_shift = {
    't':u'\u0f9d', '\\':u'\u0fac', 'd':u'\u0f4d', 'f':u'\u0fa7', 'k':u'\u0f93', 'm':u'\u0fa2',
    }

    def __init__(self):
        pass

    def getKey(self, inchar, m=False, shift=False, acs=False, Mshift=False):
        if m == True :
            if inchar in self.keymap_m:
                return self.keymap_m[inchar]
            else:
                return None
        if shift == True :
            if inchar in self.keymap_shift:
                return self.keymap_shift[inchar]
            else:
                return None
        if acs == True :
            if inchar in self.keymap_alt_ctrl_shift:
                return self.keymap_alt_ctrl_shift[inchar]
            else:
                return None
        if Mshift == True :
            if inchar in self.keymap_M_shift:
                return self.keymap_M_shift[inchar]
            else:
                return None

        if inchar in self.keymap:
            return self.keymap[inchar]
        else:
            return None


if __name__ == '__main__':
    """ Example use """
    """
    trie = Trie()
    words = 'hello goodbye help gerald gold tea ted team to too tom stan standard money'
    for word in words.split():
        trie.add(word)
    print "'goodbye' in trie: ", trie.has_word('goodbye')
    print trie.start_with_prefix('g')
    print trie.start_with_prefix('to')
    """
    imdict = IMDict()

    outs = imdict.predict(u'\u0f68\u0f7c\u0f42') #u'\u0f68'

    print(len(outs))
    print(outs)

    for w in outs:
         print(u"{}".format(w))





