import re
import sys

from template.util import registrar, unscalar_lex


factory = None
rawstart = None

class Grammar:
  def __init__(self):
    self.lextable = LEXTABLE
    self.states = STATES
    self.rules = RULES

  def install_factory(self, new_factory):
    global factory
    factory = new_factory


RESERVED = (
  "GET", "CALL", "SET", "DEFAULT", "INSERT", "INCLUDE", "PROCESS",
  "WRAPPER", "BLOCK", "END", "USE", "PLUGIN", "FILTER", "MACRO",
  "PYTHON", "RAWPYTHON", "TO", "STEP", "AND", "OR", "NOT", "DIV",
  "MOD", "IF", "UNLESS", "ELSE", "ELSIF", "FOR", "NEXT", "WHILE",
  "SWITCH", "CASE", "META", "IN", "TRY", "THROW", "CATCH", "FINAL",
  "LAST", "RETURN", "STOP", "CLEAR", "VIEW", "DEBUG"
)

CMPOP = dict((op, op) for op in ("!=", "==", "<", ">", ">=", "<="))

LEXTABLE = {
  "FOREACH": "FOR",
  "BREAK":   "LAST",
  "&&":      "AND",
  "||":      "OR",
  "!":       "NOT",
  "|":       "FILTER",
  ".":       "DOT",
  "_":       "CAT",
  "..":      "TO",
  "=":       "ASSIGN",
  "=>":      "ASSIGN",
  ",":       "COMMA",
  "\\":      "REF",
  "and":     "AND",
  "or":      "OR",
  "not":     "NOT",
  "mod":     "MOD",
  "div":     "DIV",
}

tokens = ("(", ")", "[", "]", "{", "}", "${", "$", "+", "/", ";", ":", "?")

for keyword in RESERVED:
  LEXTABLE[keyword] = keyword

for op in CMPOP.iterkeys():
  LEXTABLE[op] = "CMPOP"

for op in "-", "*", "%":
  LEXTABLE[op] = "BINOP"

for token in tokens:
  LEXTABLE[token] = token


STATES = [
  {#State 0
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'template': 52,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'switch': 34,
      'try': 35,
      'assign': 19,
      'block': 72,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 1
    "ACTIONS":  {
      "$": 43,
      'LITERAL': 75,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'setlist': 76,
      'item': 39,
      'assign': 19,
      'node': 23,
      'ident': 74
    }
  },
  {#State 2
    "DEFAULT":  -130
  },
  {#State 3
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 79,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 4
    "DEFAULT":  -23
  },
  {#State 5
    "ACTIONS":  {
      ";": 80
    }
  },
  {#State 6
    "DEFAULT":  -37
  },
  {#State 7
    "DEFAULT":  -14
  },
  {#State 8
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 90,
      'filename': 85,
      'name': 82
    }
  },
  {#State 9
    "ACTIONS":  {
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "]": 94,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 96,
      'item': 39,
      'range': 93,
      'node': 23,
      'ident': 77,
      'term': 95,
      'list': 92,
      'lterm': 56
    }
  },
  {#State 10
    "ACTIONS":  {
      ";": 97
    }
  },
  {#State 11
    "DEFAULT":  -5
  },
  {#State 12
    "ACTIONS":  {
      ";": -20
    },
    "DEFAULT":  -27
  },
  {#State 13
    "DEFAULT":  -78,
    "GOTOS":  {
      '@5-1': 98
    }
  },
  {#State 14
    "ACTIONS":  {
      'IDENT': 99
    },
    "DEFAULT":  -87,
    "GOTOS":  {
      'blockargs': 102,
      'metadata': 101,
      'meta': 100
    }
  },
  {#State 15
    "ACTIONS":  {
      'IDENT': 99
    },
    "GOTOS":  {
      'metadata': 103,
      'meta': 100
    }
  },
  {#State 16
    "ACTIONS":  {
      'DOT': 104,
      'ASSIGN': 105
    },
    "DEFAULT":  -109
  },
  {#State 17
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 106,
      'filename': 85,
      'name': 82
    }
  },
  {#State 18
    "ACTIONS":  {
      'IDENT': 107
    }
  },
  {#State 19
    "DEFAULT":  -149
  },
  {#State 20
    "DEFAULT":  -12
  },
  {#State 21
    "ACTIONS":  {
      "{": 30,
      'LITERAL': 78,
      'IDENT': 108,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'loopvar': 110,
      'node': 23,
      'ident': 77,
      'term': 109,
      'lterm': 56
    }
  },
  {#State 22
    "DEFAULT":  -40
  },
  {#State 23
    "DEFAULT":  -127
  },
  {#State 24
    "DEFAULT":  -6
  },
  {#State 25
    "ACTIONS":  {
      "\"": 117,
      "$": 114,
      'LITERAL': 116,
      'FILENAME': 83,
      'IDENT': 111,
      'NUMBER': 84,
      "${": 37
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 118,
      'filename': 85,
      'lvalue': 112,
      'lnameargs': 115,
      'item': 113,
      'name': 82
    }
  },
  {#State 26
    "DEFAULT":  -113
  },
  {#State 27
    "ACTIONS":  {
      "$": 43,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'ident': 119
    }
  },
  {#State 28
    "ACTIONS":  {
      'LITERAL': 124,
      'FILENAME': 83,
      'IDENT': 120,
      'NUMBER': 84
    },
    "DEFAULT":  -87,
    "GOTOS":  {
      'blockargs': 123,
      'filepart': 87,
      'filename': 122,
      'blockname': 121,
      'metadata': 101,
      'meta': 100
    }
  },
  {#State 29
    "DEFAULT":  -43
  },
  {#State 30
    "ACTIONS":  {
      "$": 43,
      'LITERAL': 129,
      'IDENT': 2,
      "${": 37
    },
    "DEFAULT":  -119,
    "GOTOS":  {
      'params': 128,
      'hash': 125,
      'item': 126,
      'param': 127
    }
  },
  {#State 31
    "DEFAULT":  -25
  },
  {#State 32
    "ACTIONS":  {
      "\"": 117,
      "$": 114,
      'LITERAL': 116,
      'FILENAME': 83,
      'IDENT': 111,
      'NUMBER': 84,
      "${": 37
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 118,
      'filename': 85,
      'lvalue': 112,
      'lnameargs': 130,
      'item': 113,
      'name': 82
    }
  },
  {#State 33
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -2,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 131,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 34
    "DEFAULT":  -22
  },
  {#State 35
    "DEFAULT":  -24
  },
  {#State 36
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 132,
      'filename': 85,
      'name': 82
    }
  },
  {#State 37
    "ACTIONS":  {
      "\"": 60,
      "$": 43,
      'LITERAL': 78,
      'IDENT': 2,
      'REF': 27,
      'NUMBER': 26,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 133,
      'item': 39,
      'node': 23,
      'ident': 77
    }
  },
  {#State 38
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 134,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 39
    "ACTIONS":  {
      "(": 135
    },
    "DEFAULT":  -128
  },
  {#State 40
    "ACTIONS":  {
      ";": 136
    }
  },
  {#State 41
    "DEFAULT":  -38
  },
  {#State 42
    "DEFAULT":  -11
  },
  {#State 43
    "ACTIONS":  {
      'IDENT': 137
    }
  },
  {#State 44
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 138,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 45
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 139,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 46
    "DEFAULT":  -42
  },
  {#State 47
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 140,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 48
    "ACTIONS":  {
      'IF': 144,
      'FILTER': 143,
      'FOR': 142,
      'WHILE': 146,
      'WRAPPER': 145,
      'UNLESS': 141
    }
  },
  {#State 49
    "DEFAULT":  -39
  },
  {#State 50
    "DEFAULT":  -10
  },
  {#State 51
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 147,
      'filename': 85,
      'name': 82
    }
  },
  {#State 52
    "ACTIONS":  {
      '': 148
    }
  },
  {#State 53
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 57,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 149,
      'term': 58,
      'expr': 151,
      'assign': 150,
      'lterm': 56
    }
  },
  {#State 54
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 152,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 55
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 153,
      'filename': 85,
      'name': 82
    }
  },
  {#State 56
    "DEFAULT":  -103
  },
  {#State 57
    "ACTIONS":  {
      'ASSIGN': 154
    },
    "DEFAULT":  -112
  },
  {#State 58
    "DEFAULT":  -146
  },
  {#State 59
    "DEFAULT":  -15
  },
  {#State 60
    "DEFAULT":  -176,
    "GOTOS":  {
      'quoted': 155
    }
  },
  {#State 61
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 156,
      'filename': 85,
      'name': 82
    }
  },
  {#State 62
    "ACTIONS":  {
      ";": -16,
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -26
  },
  {#State 63
    "DEFAULT":  -13
  },
  {#State 64
    "DEFAULT":  -36
  },
  {#State 65
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 167,
      'filename': 85,
      'name': 82
    }
  },
  {#State 66
    "DEFAULT":  -9
  },
  {#State 67
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 168,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 68
    "DEFAULT":  -104
  },
  {#State 69
    "ACTIONS":  {
      "$": 43,
      'LITERAL': 75,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'setlist': 169,
      'item': 39,
      'assign': 19,
      'node': 23,
      'ident': 74
    }
  },
  {#State 70
    "ACTIONS":  {
      "$": 43,
      'COMMA': 171,
      'LITERAL': 75,
      'IDENT': 2,
      "${": 37
    },
    "DEFAULT":  -19,
    "GOTOS":  {
      'item': 39,
      'assign': 170,
      'node': 23,
      'ident': 74
    }
  },
  {#State 71
    "DEFAULT":  -8
  },
  {#State 72
    "DEFAULT":  -1
  },
  {#State 73
    "DEFAULT":  -21
  },
  {#State 74
    "ACTIONS":  {
      'ASSIGN': 172,
      'DOT': 104
    }
  },
  {#State 75
    "ACTIONS":  {
      'ASSIGN': 154
    }
  },
  {#State 76
    "ACTIONS":  {
      "$": 43,
      'COMMA': 171,
      'LITERAL': 75,
      'IDENT': 2,
      "${": 37
    },
    "DEFAULT":  -30,
    "GOTOS":  {
      'item': 39,
      'assign': 170,
      'node': 23,
      'ident': 74
    }
  },
  {#State 77
    "ACTIONS":  {
      'DOT': 104
    },
    "DEFAULT":  -109
  },
  {#State 78
    "DEFAULT":  -112
  },
  {#State 79
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      ";": 173,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    }
  },
  {#State 80
    "DEFAULT":  -7
  },
  {#State 81
    "DEFAULT":  -173
  },
  {#State 82
    "DEFAULT":  -166
  },
  {#State 83
    "DEFAULT":  -172
  },
  {#State 84
    "DEFAULT":  -174
  },
  {#State 85
    "ACTIONS":  {
      'DOT': 174
    },
    "DEFAULT":  -168
  },
  {#State 86
    "ACTIONS":  {
      "$": 43,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'ident': 175
    }
  },
  {#State 87
    "DEFAULT":  -171
  },
  {#State 88
    "DEFAULT":  -169
  },
  {#State 89
    "DEFAULT":  -176,
    "GOTOS":  {
      'quoted': 176
    }
  },
  {#State 90
    "DEFAULT":  -35
  },
  {#State 91
    "ACTIONS":  {
      "+": 177,
      "(": 178
    },
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 179
    }
  },
  {#State 92
    "ACTIONS":  {
      "{": 30,
      'COMMA': 182,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "]": 180,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 181,
      'lterm': 56
    }
  },
  {#State 93
    "ACTIONS":  {
      "]": 183
    }
  },
  {#State 94
    "DEFAULT":  -107
  },
  {#State 95
    "DEFAULT":  -116
  },
  {#State 96
    "ACTIONS":  {
      'TO': 184
    },
    "DEFAULT":  -104
  },
  {#State 97
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 185,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 98
    "ACTIONS":  {
      ";": 186
    }
  },
  {#State 99
    "ACTIONS":  {
      'ASSIGN': 187
    }
  },
  {#State 100
    "DEFAULT":  -99
  },
  {#State 101
    "ACTIONS":  {
      'COMMA': 189,
      'IDENT': 99
    },
    "DEFAULT":  -86,
    "GOTOS":  {
      'meta': 188
    }
  },
  {#State 102
    "ACTIONS":  {
      ";": 190
    }
  },
  {#State 103
    "ACTIONS":  {
      'COMMA': 189,
      'IDENT': 99
    },
    "DEFAULT":  -17,
    "GOTOS":  {
      'meta': 188
    }
  },
  {#State 104
    "ACTIONS":  {
      "$": 43,
      'IDENT': 2,
      'NUMBER': 192,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 191
    }
  },
  {#State 105
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'WRAPPER': 55,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      "\"": 60,
      'PROCESS': 61,
      'FILTER': 25,
      'RETURN': 64,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 193,
      'DEFAULT': 69,
      "{": 30,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'term': 58,
      'loop': 4,
      'expr': 195,
      'wrapper': 46,
      'atomexpr': 48,
      'atomdir': 12,
      'mdir': 194,
      'sterm': 68,
      'filter': 29,
      'ident': 149,
      'python': 31,
      'setlist': 70,
      'switch': 34,
      'try': 35,
      'assign': 19,
      'directive': 196,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 106
    "DEFAULT":  -33
  },
  {#State 107
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'INCLUDE': 17,
      "(": 198,
      'SWITCH': 54,
      'WRAPPER': 55,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      "\"": 60,
      'PROCESS': 61,
      'FILTER': 25,
      'RETURN': 64,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 193,
      'DEFAULT': 69,
      "{": 30,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'term': 58,
      'loop': 4,
      'expr': 199,
      'wrapper': 46,
      'atomexpr': 48,
      'atomdir': 12,
      'mdir': 197,
      'sterm': 68,
      'filter': 29,
      'ident': 149,
      'python': 31,
      'setlist': 70,
      'switch': 34,
      'try': 35,
      'assign': 19,
      'directive': 196,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 108
    "ACTIONS":  {
      'IN': 201,
      'ASSIGN': 200
    },
    "DEFAULT":  -130
  },
  {#State 109
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 202
    }
  },
  {#State 110
    "ACTIONS":  {
      ";": 203
    }
  },
  {#State 111
    "ACTIONS":  {
      'ASSIGN': -130
    },
    "DEFAULT":  -173
  },
  {#State 112
    "ACTIONS":  {
      'ASSIGN': 204
    }
  },
  {#State 113
    "DEFAULT":  -159
  },
  {#State 114
    "ACTIONS":  {
      "$": 43,
      'IDENT': 205,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'ident': 175
    }
  },
  {#State 115
    "ACTIONS":  {
      ";": 206
    }
  },
  {#State 116
    "ACTIONS":  {
      'ASSIGN': -161
    },
    "DEFAULT":  -169
  },
  {#State 117
    "DEFAULT":  -176,
    "GOTOS":  {
      'quoted': 207
    }
  },
  {#State 118
    "DEFAULT":  -158
  },
  {#State 119
    "ACTIONS":  {
      'DOT': 104
    },
    "DEFAULT":  -110
  },
  {#State 120
    "ACTIONS":  {
      'ASSIGN': 187
    },
    "DEFAULT":  -173
  },
  {#State 121
    "DEFAULT":  -83
  },
  {#State 122
    "ACTIONS":  {
      'DOT': 174
    },
    "DEFAULT":  -84
  },
  {#State 123
    "ACTIONS":  {
      ";": 208
    }
  },
  {#State 124
    "DEFAULT":  -85
  },
  {#State 125
    "ACTIONS":  {
      "}": 209
    }
  },
  {#State 126
    "ACTIONS":  {
      'ASSIGN': 210
    }
  },
  {#State 127
    "DEFAULT":  -122
  },
  {#State 128
    "ACTIONS":  {
      "$": 43,
      'COMMA': 212,
      'LITERAL': 129,
      'IDENT': 2,
      "${": 37
    },
    "DEFAULT":  -118,
    "GOTOS":  {
      'item': 126,
      'param': 211
    }
  },
  {#State 129
    "ACTIONS":  {
      'ASSIGN': 213
    }
  },
  {#State 130
    "DEFAULT":  -73
  },
  {#State 131
    "DEFAULT":  -4
  },
  {#State 132
    "ACTIONS":  {
      ";": 214
    }
  },
  {#State 133
    "ACTIONS":  {
      "}": 215
    }
  },
  {#State 134
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'BINOP': 161
    },
    "DEFAULT":  -142
  },
  {#State 135
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 216
    }
  },
  {#State 136
    "DEFAULT":  -76,
    "GOTOS":  {
      '@4-2': 217
    }
  },
  {#State 137
    "DEFAULT":  -132
  },
  {#State 138
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      ";": 218,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    }
  },
  {#State 139
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -29
  },
  {#State 140
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -28
  },
  {#State 141
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 219,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 142
    "ACTIONS":  {
      "{": 30,
      'LITERAL': 78,
      'IDENT': 108,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'loopvar': 220,
      'node': 23,
      'ident': 77,
      'term': 109,
      'lterm': 56
    }
  },
  {#State 143
    "ACTIONS":  {
      "\"": 117,
      "$": 114,
      'LITERAL': 116,
      'FILENAME': 83,
      'IDENT': 111,
      'NUMBER': 84,
      "${": 37
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 118,
      'filename': 85,
      'lvalue': 112,
      'lnameargs': 221,
      'item': 113,
      'name': 82
    }
  },
  {#State 144
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 222,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 145
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 223,
      'filename': 85,
      'name': 82
    }
  },
  {#State 146
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 224,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 147
    "DEFAULT":  -41
  },
  {#State 148
    "DEFAULT":  0
  },
  {#State 149
    "ACTIONS":  {
      'DOT': 104,
      'ASSIGN': 172
    },
    "DEFAULT":  -109
  },
  {#State 150
    "ACTIONS":  {
      ")": 225
    }
  },
  {#State 151
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      ")": 226,
      'OR': 162
    }
  },
  {#State 152
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      ";": 227,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    }
  },
  {#State 153
    "ACTIONS":  {
      ";": 228
    }
  },
  {#State 154
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 229,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 155
    "ACTIONS":  {
      "\"": 234,
      'TEXT': 231,
      ";": 233,
      "$": 43,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'ident': 230,
      'quotable': 232
    }
  },
  {#State 156
    "DEFAULT":  -34
  },
  {#State 157
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 235,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 158
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 236,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 159
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 237,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 160
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 238,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 161
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 239,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 162
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 240,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 163
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 241,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 164
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 242,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 165
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 243,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 166
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 244,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 167
    "DEFAULT":  -32
  },
  {#State 168
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      ";": 245,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    }
  },
  {#State 169
    "ACTIONS":  {
      "$": 43,
      'COMMA': 171,
      'LITERAL': 75,
      'IDENT': 2,
      "${": 37
    },
    "DEFAULT":  -31,
    "GOTOS":  {
      'item': 39,
      'assign': 170,
      'node': 23,
      'ident': 74
    }
  },
  {#State 170
    "DEFAULT":  -147
  },
  {#State 171
    "DEFAULT":  -148
  },
  {#State 172
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 246,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 173
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 247,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 174
    "ACTIONS":  {
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 248
    }
  },
  {#State 175
    "ACTIONS":  {
      'DOT': 104
    },
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 249
    }
  },
  {#State 176
    "ACTIONS":  {
      "\"": 250,
      'TEXT': 231,
      ";": 233,
      "$": 43,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'ident': 230,
      'quotable': 232
    }
  },
  {#State 177
    "ACTIONS":  {
      "\"": 89,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'filename': 85,
      'name': 251
    }
  },
  {#State 178
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 252
    }
  },
  {#State 179
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "DEFAULT":  -163,
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 180
    "DEFAULT":  -105
  },
  {#State 181
    "DEFAULT":  -114
  },
  {#State 182
    "DEFAULT":  -115
  },
  {#State 183
    "DEFAULT":  -106
  },
  {#State 184
    "ACTIONS":  {
      "\"": 60,
      "$": 43,
      'LITERAL': 78,
      'IDENT': 2,
      'REF': 27,
      'NUMBER': 26,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 259,
      'item': 39,
      'node': 23,
      'ident': 77
    }
  },
  {#State 185
    "ACTIONS":  {
      'FINAL': 260,
      'CATCH': 262
    },
    "DEFAULT":  -72,
    "GOTOS":  {
      'final': 261
    }
  },
  {#State 186
    "ACTIONS":  {
      'TEXT': 263
    }
  },
  {#State 187
    "ACTIONS":  {
      "\"": 266,
      'LITERAL': 265,
      'NUMBER': 264
    }
  },
  {#State 188
    "DEFAULT":  -97
  },
  {#State 189
    "DEFAULT":  -98
  },
  {#State 190
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'template': 267,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 72,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 191
    "DEFAULT":  -125
  },
  {#State 192
    "DEFAULT":  -126
  },
  {#State 193
    "ACTIONS":  {
      ";": 268
    }
  },
  {#State 194
    "DEFAULT":  -89
  },
  {#State 195
    "ACTIONS":  {
      ";": -150,
      "+": 157,
      'LITERAL': -150,
      'IDENT': -150,
      'CAT': 163,
      "$": -150,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      'COMMA': -150,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162,
      "${": -150
    },
    "DEFAULT":  -26
  },
  {#State 196
    "DEFAULT":  -92
  },
  {#State 197
    "DEFAULT":  -91
  },
  {#State 198
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 57,
      'IDENT': 269,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'margs': 270,
      'node': 23,
      'ident': 149,
      'term': 58,
      'expr': 151,
      'assign': 150,
      'lterm': 56
    }
  },
  {#State 199
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -26
  },
  {#State 200
    "ACTIONS":  {
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 271,
      'lterm': 56
    }
  },
  {#State 201
    "ACTIONS":  {
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 272,
      'lterm': 56
    }
  },
  {#State 202
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "DEFAULT":  -64,
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 203
    "DEFAULT":  -56,
    "GOTOS":  {
      '@1-3': 273
    }
  },
  {#State 204
    "ACTIONS":  {
      "\"": 89,
      "$": 86,
      'LITERAL': 88,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'names': 91,
      'nameargs': 274,
      'filename': 85,
      'name': 82
    }
  },
  {#State 205
    "ACTIONS":  {
      'ASSIGN': -132
    },
    "DEFAULT":  -130
  },
  {#State 206
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 275,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 207
    "ACTIONS":  {
      "\"": 276,
      'TEXT': 231,
      ";": 233,
      "$": 43,
      'IDENT': 2,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'ident': 230,
      'quotable': 232
    }
  },
  {#State 208
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 277,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 209
    "DEFAULT":  -108
  },
  {#State 210
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 278,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 211
    "DEFAULT":  -120
  },
  {#State 212
    "DEFAULT":  -121
  },
  {#State 213
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 279,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 214
    "DEFAULT":  -74,
    "GOTOS":  {
      '@3-3': 280
    }
  },
  {#State 215
    "DEFAULT":  -131
  },
  {#State 216
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      ")": 281,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 217
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 282,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 218
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 283,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 219
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -47
  },
  {#State 220
    "DEFAULT":  -58
  },
  {#State 221
    "DEFAULT":  -81
  },
  {#State 222
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -45
  },
  {#State 223
    "DEFAULT":  -66
  },
  {#State 224
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -61
  },
  {#State 225
    "DEFAULT":  -144
  },
  {#State 226
    "DEFAULT":  -145
  },
  {#State 227
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 284,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 228
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 285,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 229
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -151
  },
  {#State 230
    "ACTIONS":  {
      'DOT': 104
    },
    "DEFAULT":  -177
  },
  {#State 231
    "DEFAULT":  -178
  },
  {#State 232
    "DEFAULT":  -175
  },
  {#State 233
    "DEFAULT":  -179
  },
  {#State 234
    "DEFAULT":  -111
  },
  {#State 235
    "ACTIONS":  {
      'DIV': 159,
      'MOD': 165,
      "/": 166
    },
    "DEFAULT":  -135
  },
  {#State 236
    "ACTIONS":  {
      ":": 286,
      'CMPOP': 164,
      "?": 158,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    }
  },
  {#State 237
    "ACTIONS":  {
      'MOD': 165
    },
    "DEFAULT":  -136
  },
  {#State 238
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'BINOP': 161
    },
    "DEFAULT":  -140
  },
  {#State 239
    "ACTIONS":  {
      "+": 157,
      'DIV': 159,
      'MOD': 165,
      "/": 166
    },
    "DEFAULT":  -133
  },
  {#State 240
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'BINOP': 161
    },
    "DEFAULT":  -141
  },
  {#State 241
    "ACTIONS":  {
      "+": 157,
      'CMPOP': 164,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'BINOP': 161
    },
    "DEFAULT":  -139
  },
  {#State 242
    "ACTIONS":  {
      "+": 157,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'BINOP': 161
    },
    "DEFAULT":  -138
  },
  {#State 243
    "DEFAULT":  -137
  },
  {#State 244
    "ACTIONS":  {
      'DIV': 159,
      'MOD': 165
    },
    "DEFAULT":  -134
  },
  {#State 245
    "DEFAULT":  -59,
    "GOTOS":  {
      '@2-3': 287
    }
  },
  {#State 246
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -150
  },
  {#State 247
    "ACTIONS":  {
      'ELSIF': 290,
      'ELSE': 288
    },
    "DEFAULT":  -50,
    "GOTOS":  {
      'else': 289
    }
  },
  {#State 248
    "DEFAULT":  -170
  },
  {#State 249
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "DEFAULT":  -162,
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 250
    "DEFAULT":  -167
  },
  {#State 251
    "DEFAULT":  -165
  },
  {#State 252
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      ")": 291,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 253
    "ACTIONS":  {
      'DOT': 104,
      'ASSIGN': 292
    },
    "DEFAULT":  -109
  },
  {#State 254
    "ACTIONS":  {
      "(": 135,
      'ASSIGN': 210
    },
    "DEFAULT":  -128
  },
  {#State 255
    "DEFAULT":  -153
  },
  {#State 256
    "ACTIONS":  {
      'ASSIGN': 213
    },
    "DEFAULT":  -112
  },
  {#State 257
    "DEFAULT":  -152
  },
  {#State 258
    "DEFAULT":  -155
  },
  {#State 259
    "DEFAULT":  -117
  },
  {#State 260
    "ACTIONS":  {
      ";": 293
    }
  },
  {#State 261
    "ACTIONS":  {
      'END': 294
    }
  },
  {#State 262
    "ACTIONS":  {
      ";": 296,
      'DEFAULT': 297,
      'FILENAME': 83,
      'IDENT': 81,
      'NUMBER': 84
    },
    "GOTOS":  {
      'filepart': 87,
      'filename': 295
    }
  },
  {#State 263
    "ACTIONS":  {
      'END': 298
    }
  },
  {#State 264
    "DEFAULT":  -102
  },
  {#State 265
    "DEFAULT":  -100
  },
  {#State 266
    "ACTIONS":  {
      'TEXT': 299
    }
  },
  {#State 267
    "ACTIONS":  {
      'END': 300
    }
  },
  {#State 268
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 301,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 269
    "ACTIONS":  {
      'COMMA': -96,
      'IDENT': -96,
      ")": -96
    },
    "DEFAULT":  -130
  },
  {#State 270
    "ACTIONS":  {
      'COMMA': 304,
      'IDENT': 302,
      ")": 303
    }
  },
  {#State 271
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 305
    }
  },
  {#State 272
    "DEFAULT":  -156,
    "GOTOS":  {
      'args': 306
    }
  },
  {#State 273
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 307,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 274
    "DEFAULT":  -157
  },
  {#State 275
    "ACTIONS":  {
      'END': 308
    }
  },
  {#State 276
    "ACTIONS":  {
      'ASSIGN': -160
    },
    "DEFAULT":  -167
  },
  {#State 277
    "ACTIONS":  {
      'END': 309
    }
  },
  {#State 278
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -124
  },
  {#State 279
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -123
  },
  {#State 280
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 310,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 281
    "DEFAULT":  -129
  },
  {#State 282
    "ACTIONS":  {
      'END': 311
    }
  },
  {#State 283
    "ACTIONS":  {
      'ELSIF': 290,
      'ELSE': 288
    },
    "DEFAULT":  -50,
    "GOTOS":  {
      'else': 312
    }
  },
  {#State 284
    "ACTIONS":  {
      'CASE': 313
    },
    "DEFAULT":  -55,
    "GOTOS":  {
      'case': 314
    }
  },
  {#State 285
    "ACTIONS":  {
      'END': 315
    }
  },
  {#State 286
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 316,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 287
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 317,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 288
    "ACTIONS":  {
      ";": 318
    }
  },
  {#State 289
    "ACTIONS":  {
      'END': 319
    }
  },
  {#State 290
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 320,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 291
    "DEFAULT":  -164
  },
  {#State 292
    "ACTIONS":  {
      'NOT': 38,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "(": 53,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'expr': 321,
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 58,
      'lterm': 56
    }
  },
  {#State 293
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 322,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 294
    "DEFAULT":  -67
  },
  {#State 295
    "ACTIONS":  {
      'DOT': 174,
      ";": 323
    }
  },
  {#State 296
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 324,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 297
    "ACTIONS":  {
      ";": 325
    }
  },
  {#State 298
    "DEFAULT":  -79
  },
  {#State 299
    "ACTIONS":  {
      "\"": 326
    }
  },
  {#State 300
    "DEFAULT":  -82
  },
  {#State 301
    "ACTIONS":  {
      'END': 327
    }
  },
  {#State 302
    "DEFAULT":  -94
  },
  {#State 303
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'WRAPPER': 55,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      "\"": 60,
      'PROCESS': 61,
      'FILTER': 25,
      'RETURN': 64,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 193,
      'DEFAULT': 69,
      "{": 30,
      "${": 37
    },
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'term': 58,
      'loop': 4,
      'expr': 199,
      'wrapper': 46,
      'atomexpr': 48,
      'atomdir': 12,
      'mdir': 328,
      'sterm': 68,
      'filter': 29,
      'ident': 149,
      'python': 31,
      'setlist': 70,
      'switch': 34,
      'try': 35,
      'assign': 19,
      'directive': 196,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 304
    "DEFAULT":  -95
  },
  {#State 305
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "DEFAULT":  -62,
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 306
    "ACTIONS":  {
      "{": 30,
      'COMMA': 258,
      'LITERAL': 256,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "DEFAULT":  -63,
    "GOTOS":  {
      'sterm': 68,
      'item': 254,
      'param': 255,
      'node': 23,
      'ident': 253,
      'term': 257,
      'lterm': 56
    }
  },
  {#State 307
    "ACTIONS":  {
      'END': 329
    }
  },
  {#State 308
    "DEFAULT":  -80
  },
  {#State 309
    "DEFAULT":  -88
  },
  {#State 310
    "ACTIONS":  {
      'END': 330
    }
  },
  {#State 311
    "DEFAULT":  -77
  },
  {#State 312
    "ACTIONS":  {
      'END': 331
    }
  },
  {#State 313
    "ACTIONS":  {
      ";": 332,
      'DEFAULT': 334,
      "{": 30,
      'LITERAL': 78,
      'IDENT': 2,
      "\"": 60,
      "$": 43,
      "[": 9,
      'NUMBER': 26,
      'REF': 27,
      "${": 37
    },
    "GOTOS":  {
      'sterm': 68,
      'item': 39,
      'node': 23,
      'ident': 77,
      'term': 333,
      'lterm': 56
    }
  },
  {#State 314
    "ACTIONS":  {
      'END': 335
    }
  },
  {#State 315
    "DEFAULT":  -65
  },
  {#State 316
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -143
  },
  {#State 317
    "ACTIONS":  {
      'END': 336
    }
  },
  {#State 318
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 337,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 319
    "DEFAULT":  -46
  },
  {#State 320
    "ACTIONS":  {
      'CMPOP': 164,
      "?": 158,
      ";": 338,
      "+": 157,
      'MOD': 165,
      'DIV': 159,
      "/": 166,
      'AND': 160,
      'CAT': 163,
      'BINOP': 161,
      'OR': 162
    }
  },
  {#State 321
    "ACTIONS":  {
      "+": 157,
      'CAT': 163,
      'CMPOP': 164,
      "?": 158,
      'DIV': 159,
      'MOD': 165,
      "/": 166,
      'AND': 160,
      'BINOP': 161,
      'OR': 162
    },
    "DEFAULT":  -154
  },
  {#State 322
    "DEFAULT":  -71
  },
  {#State 323
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 339,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 324
    "ACTIONS":  {
      'FINAL': 260,
      'CATCH': 262
    },
    "DEFAULT":  -72,
    "GOTOS":  {
      'final': 340
    }
  },
  {#State 325
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 341,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 326
    "DEFAULT":  -101
  },
  {#State 327
    "DEFAULT":  -93
  },
  {#State 328
    "DEFAULT":  -90
  },
  {#State 329
    "DEFAULT":  -57
  },
  {#State 330
    "DEFAULT":  -75
  },
  {#State 331
    "DEFAULT":  -44
  },
  {#State 332
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 342,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 333
    "ACTIONS":  {
      ";": 343
    }
  },
  {#State 334
    "ACTIONS":  {
      ";": 344
    }
  },
  {#State 335
    "DEFAULT":  -51
  },
  {#State 336
    "DEFAULT":  -60
  },
  {#State 337
    "DEFAULT":  -49
  },
  {#State 338
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 345,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 339
    "ACTIONS":  {
      'FINAL': 260,
      'CATCH': 262
    },
    "DEFAULT":  -72,
    "GOTOS":  {
      'final': 346
    }
  },
  {#State 340
    "DEFAULT":  -70
  },
  {#State 341
    "ACTIONS":  {
      'FINAL': 260,
      'CATCH': 262
    },
    "DEFAULT":  -72,
    "GOTOS":  {
      'final': 347
    }
  },
  {#State 342
    "DEFAULT":  -54
  },
  {#State 343
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 348,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 344
    "ACTIONS":  {
      'SET': 1,
      'PYTHON': 40,
      'NOT': 38,
      'IDENT': 2,
      'CLEAR': 41,
      'UNLESS': 3,
      'IF': 44,
      "$": 43,
      'STOP': 6,
      'CALL': 45,
      'THROW': 8,
      'GET': 47,
      "[": 9,
      'TRY': 10,
      'LAST': 49,
      'DEBUG': 51,
      'RAWPYTHON': 13,
      'META': 15,
      'INCLUDE': 17,
      "(": 53,
      'SWITCH': 54,
      'MACRO': 18,
      'WRAPPER': 55,
      ";": -18,
      'FOR': 21,
      'NEXT': 22,
      'LITERAL': 57,
      'TEXT': 24,
      "\"": 60,
      'PROCESS': 61,
      'RETURN': 64,
      'FILTER': 25,
      'INSERT': 65,
      'NUMBER': 26,
      'REF': 27,
      'WHILE': 67,
      'BLOCK': 28,
      'DEFAULT': 69,
      "{": 30,
      'USE': 32,
      'VIEW': 36,
      "${": 37
    },
    "DEFAULT":  -3,
    "GOTOS":  {
      'item': 39,
      'node': 23,
      'rawpython': 59,
      'term': 58,
      'loop': 4,
      'use': 63,
      'expr': 62,
      'capture': 42,
      'statement': 5,
      'view': 7,
      'wrapper': 46,
      'atomexpr': 48,
      'chunk': 11,
      'defblock': 66,
      'atomdir': 12,
      'anonblock': 50,
      'sterm': 68,
      'defblockname': 14,
      'filter': 29,
      'ident': 16,
      'python': 31,
      'setlist': 70,
      'chunks': 33,
      'try': 35,
      'switch': 34,
      'assign': 19,
      'block': 349,
      'directive': 71,
      'macro': 20,
      'condition': 73,
      'lterm': 56
    }
  },
  {#State 345
    "ACTIONS":  {
      'ELSIF': 290,
      'ELSE': 288
    },
    "DEFAULT":  -50,
    "GOTOS":  {
      'else': 350
    }
  },
  {#State 346
    "DEFAULT":  -68
  },
  {#State 347
    "DEFAULT":  -69
  },
  {#State 348
    "ACTIONS":  {
      'CASE': 313
    },
    "DEFAULT":  -55,
    "GOTOS":  {
      'case': 351
    }
  },
  {#State 349
    "DEFAULT":  -53
  },
  {#State 350
    "DEFAULT":  -48
  },
  {#State 351
    "DEFAULT":  -52
  }
];


RULES = {
  0: ("$start", 2, None),
  8: ("statement", 1, None),
  9: ("statement", 1, None),
  10: ("statement", 1, None),
  11: ("statement", 1, None),
  12: ("statement", 1, None),
  13: ("statement", 1, None),
  14: ("statement", 1, None),
  15: ("statement", 1, None),
  18: ("statement", 0, None),
  20: ("directive", 1, None),
  21: ("directive", 1, None),
  22: ("directive", 1, None),
  23: ("directive", 1, None),
  24: ("directive", 1, None),
  25: ("directive", 1, None),
  27: ("atomexpr", 1, None),
  42: ("atomdir", 1, None),
  43: ("atomdir", 1, None),
  44: ("atomdir", 1, None),
  84: ("blockname", 1, None),
  86: ("blockargs", 1, None),
  87: ("blockargs", 0, None),
  92: ("mdir", 1, None),
  98: ("metadata", 2, None),
  99: ("metadata", 1, None),
  103: ("term", 1, None),
  104: ("term", 1, None),
  112: ("sterm", 1, None),
  113: ("sterm", 1, None),
  115: ("list", 2, None),
  116: ("list", 1, None),
  118: ("hash", 1, None),
  121: ("params", 2, None),
  122: ("params", 1, None),
  127: ("ident", 1, None),
  146: ("expr", 1, None),
  148: ("setlist", 2, None),
  149: ("setlist", 1, None),
  158: ("lnameargs", 1, None),
  159: ("lvalue", 1, None),
  161: ("lvalue", 1, None),
  169: ("name", 1, None),
  171: ("filename", 1, None),
  172: ("filepart", 1, None),
  173: ("filepart", 1, None),
  174: ("filepart", 1, None),
}

# Registration decorator for RULES:

define = registrar(RULES, lambda f, key, lhs, len: ((key, (lhs, len, f)),))


@define(1, "template", 1)
def rule(*args):
  return factory.template(args[1])


@define(2, "block", 1)
def rule(*args):
  return factory.block(args[1])


@define(3, "block", 0)
def rule(*args):
  return factory.block()


@define(4, "chunks", 2)
def rule(*args):
  if len(args) >= 3 and args[2] is not None:
    args[1].append(args[2])
  return args[1]


@define(5, "chunks", 1)
def rule(*args):
  if len(args) >= 2 and args[1] is not None:
    return [args[1]]
  else:
    return []


@define(6, "chunk", 1)
def rule(*args):
  return factory.textblock(args[1])


@define(7, "chunk", 2)
def rule(*args):
  if not args[1]:
    return ""
  else:
    return args[0].location() + args[1]


@define(16, "statement", 1)
def rule(*args):
  return factory.get(args[1])


@define(17, "statement", 2)
def rule(*args):
  return args[0].add_metadata(args[2])


@define(19, "directive", 1)
def rule(*args):
  return factory.set(args[1])


@define(26, "atomexpr", 1)
def rule(*args):
  return factory.get(args[1])


@define(28, "atomdir", 2)
def rule(*args):
  return factory.get(args[2])


@define(29, "atomdir", 2)
def rule(*args):
  return factory.call(args[2])


@define(30, "atomdir", 2)
def rule(*args):
  return factory.set(args[2])


@define(31, "atomdir", 2)
def rule(*args):
  return factory.default(args[2])


@define(32, "atomdir", 2)
def rule(*args):
  return factory.insert(args[2])


@define(33, "atomdir", 2)
def rule(*args):
  return factory.include(args[2])


@define(34, "atomdir", 2)
def rule(*args):
  return factory.process(args[2])


@define(35, "atomdir", 2)
def rule(*args):
  return factory.throw(args[2])


@define(36, "atomdir", 1)
def rule(*args):
  return factory.return_()


@define(37, "atomdir", 1)
def rule(*args):
  return factory.stop()


@define(38, "atomdir", 1)
def rule(*args):
  return "output.clear()"


@define(39, "atomdir", 1)
def rule(*args):
  if args[0].infor or args[0].inwhile:
    return "raise Break"
  else:
    return "break"


@define(40, "atomdir", 1)
def rule(*args):
  if args[0].infor:
    return factory.next()
  elif args[0].inwhile:
    return "raise Continue"
  else:
    return "continue"


@define(41, "atomdir", 2)
def rule(*args):
  if args[2][0][0] in ("'on'", "'off'"):
    args[0].debug_dirs = args[2][0][0] == "'on'"
    return factory.debug(args[2])
  else:
    if args[0].debug_dirs:
      return factory.debug(args[2])
    else:
      return ""


@define(44, "condition", 6)
def rule(*args):
  return factory.if_(args[2], args[4], args[5])


@define(45, "condition", 3)
def rule(*args):
  return factory.if_(args[3], args[1])


@define(46, "condition", 6)
def rule(*args):
  return factory.if_("not (%s)" % args[2], args[4], args[5])


@define(47, "condition", 3)
def rule(*args):
  return factory.if_("not (%s)" % args[3], args[1])


@define(48, "else", 5)
def rule(*args):
  args[5].insert(0, [args[2], args[4]])
  return args[5]


@define(49, "else", 3)
def rule(*args):
  return [args[3]]


@define(50, "else", 0)
def rule(*args):
  return [None]


@define(51, "switch", 6)
def rule(*args):
  return factory.switch(args[2], args[5])


@define(52, "case", 5)
def rule(*args):
  args[5].insert(0, [args[2], args[4]])
  return args[5]


@define(53, "case", 4)
def rule(*args):
  return [args[4]]


@define(54, "case", 3)
def rule(*args):
  return [args[3]]


@define(55, "case", 0)
def rule(*args):
  return [None]


@define(56, "@1-3", 0)
def rule(*args):
  retval = args[0].infor
  args[0].infor += 1
  return retval


@define(57, "loop", 6)
def rule(*args):
  args[0].infor -= 1
  return factory.foreach(*(args[2] + [args[5]]))


@define(58, "loop", 3)
def rule(*args):
  return factory.foreach(*(args[3] + [args[1]]))


@define(59, "@2-3", 0)
def rule(*args):
  retval = args[0].inwhile
  args[0].inwhile += 1
  return retval


@define(60, "loop", 6)
def rule(*args):
  args[0].inwhile -= 1
  return factory.while_(args[2], args[5])


@define(61, "loop", 3)
def rule(*args):
  return factory.while_(args[3], args[1])


@define(62, "loopvar", 4)
def rule(*args):
  return [args[1], args[3], args[4]]


@define(63, "loopvar", 4)
def rule(*args):
  return [args[1], args[3], args[4]]


@define(64, "loopvar", 2)
def rule(*args):
  return [0, args[1], args[2]]


@define(65, "wrapper", 5)
def rule(*args):
  return factory.wrapper(args[2], args[4])


@define(66, "wrapper", 3)
def rule(*args):
  return factory.wrapper(args[3], args[1])


@define(67, "try", 5)
def rule(*args):
  return factory.try_(args[3], args[4])


@define(68, "final", 5)
def rule(*args):
  args[5].insert(0, [args[2], args[4]])
  return args[5]


@define(69, "final", 5)
def rule(*args):
  args[5].insert(0, [None, args[4]])
  return args[5]


@define(70, "final", 4)
def rule(*args):
  args[4].insert(0, [None, args[3]])
  return args[4]


@define(71, "final", 3)
def rule(*args):
  return [args[3]]


@define(72, "final", 0)
def rule(*args):
  return [0]


@define(73, "use", 2)
def rule(*args):
  return factory.use(args[2])


@define(74, "@3-3", 0)
def rule(*args):
  return args[0].push_defblock()


@define(75, "view", 6)
def rule(*args):
  return factory.view(args[2], args[5], args[0].pop_defblock())


@define(76, "@4-2", 0)
def rule(*args):
  args[0].inpython += 1


@define(77, "python", 5)
def rule(*args):
  args[0].inpython -= 1
  if args[0].eval_python:
    return factory.python(args[4])
  else:
    return factory.no_python()


@define(78, "@5-1", 0)
def rule(*args):
  global rawstart
  args[0].inpython += 1
  rawstart = args[0].line


@define(79, "rawpython", 5)
def rule(*args):
  args[0].inpython -= 1
  if args[0].eval_python:
    return factory.rawpython(args[4], rawstart)
  else:
    return factory.no_python()


@define(80, "filter", 5)
def rule(*args):
  return factory.filter(args[2], args[4])


@define(81, "filter", 3)
def rule(*args):
  return factory.filter(args[3], args[1])


@define(82, "defblock", 5)
def rule(*args):
  name = "/".join(args[0].defblocks)
  args[0].defblocks.pop()
  args[0].define_block(name, args[4])
  return None


@define(83, "defblockname", 2)
def rule(*args):
  args[0].defblocks.append(unscalar_lex(args[2]))
  return args[2]


@define(85, "blockname", 1)
def rule(*args):
  # FIXME: Should this just be eval(args[1])?
  return re.sub(r"^'(.*)'$", r"\1", args[1])


@define(88, "anonblock", 5)
def rule(*args):
  if args[2]:
    sys.stderr.write("experimental block args: [%s]\n" % ", ".join(args[2]))
  return factory.anon_block(args[4])


@define(89, "capture", 3)
def rule(*args):
  return factory.capture(args[1], args[3])


@define(90, "macro", 6)
def rule(*args):
  return factory.macro(args[2], args[6], args[4])


@define(91, "macro", 3)
def rule(*args):
  return factory.macro(args[2], args[3])


@define(93, "mdir", 4)
def rule(*args):
  return args[3]


@define(94, "margs", 2)
def rule(*args):
  args[1].append(args[2])
  return args[1]


@define(95, "margs", 2)
def rule(*args):
  return args[1]


@define(96, "margs", 1)
def rule(*args):
  return [args[1]]


@define(97, "metadata", 2)
def rule(*args):
  args[1].extend(args[2])
  return args[1]


@define(100, "meta", 3)
def rule(*args):
  return [args[1], unscalar_lex(args[3])]


@define(101, "meta", 5)
def rule(*args):
  return [args[1], args[4]]


@define(102, "meta", 3)
def rule(*args):
  return [args[1], args[3]]


@define(105, "lterm", 3)
def rule(*args):
  return "List(%s)" % args[2]


@define(106, "lterm", 3)
def rule(*args):
  return "List(%s)" % args[2]


@define(107, "lterm", 2)
def rule(*args):
  return "[]"


@define(108, "lterm", 3)
def rule(*args):
  return "Dict(%s)" % args[2]


@define(109, "sterm", 1)
def rule(*args):
  return factory.ident(args[1])


@define(110, "sterm", 2)
def rule(*args):
  return factory.identref(args[2])


@define(111, "sterm", 3)
def rule(*args):
  return factory.quoted(args[2])


@define(114, "list", 2)
def rule(*args):
  return "%s, %s" % (args[1], args[2])


@define(117, "range", 3)
def rule(*args):
  return "xrange(int(%s), int(%s) + 1)" % (args[1], args[3])


@define(119, "hash", 0)
def rule(*args):
  return ""


@define(120, "params", 2)
def rule(*args):
  return "%s, %s" % (args[1], args[2])


@define(123, "param", 3)
def rule(*args):
  return "(%s, %s)" % (args[1], args[3])


@define(124, "param", 3)
def rule(*args):
  return "(%s, %s)" % (args[1], args[3])


@define(125, "ident", 3)
def rule(*args):
  args[1].extend(args[3])
  return args[1]


@define(126, "ident", 3)
def rule(*args):
  for component in str(unscalar_lex(args[3])).split("."):
    args[1].extend((component, 0))
  return args[1]


@define(128, "node", 1)
def rule(*args):
  return [args[1], 0]


@define(129, "node", 4)
def rule(*args):
  return [args[1], factory.args(args[3])]


@define(130, "item", 1)
def rule(*args):
  return repr(args[1])


@define(131, "item", 3)
def rule(*args):
  return args[2]


@define(132, "item", 2)
def rule(*args):
  if args[0].v1dollar:
    return "'%s'" % args[2]
  else:
    return factory.ident(["'%s'" % args[2], 0])


@define(133, "expr", 3)
def rule(*args):
  return "%s %s %s" % (args[1], args[2], args[3])


@define(134, "expr", 3)
def rule(*args):
  return "%s %s %s" % (args[1], args[2], args[3])


@define(135, "expr", 3)
def rule(*args):
  return "%s %s %s" % (args[1], args[2], args[3])


@define(136, "expr", 3)
def rule(*args):
  return "%s // %s" % (args[1], args[3])


@define(137, "expr", 3)
def rule(*args):
  return "%s %% %s" % (args[1], args[3])


@define(138, "expr", 3)
def rule(*args):
  return "%s %s %s" % (args[1], CMPOP[args[2]], args[3])


@define(139, "expr", 3)
def rule(*args):
  return "%s & %s" % (args[1], args[3])


@define(140, "expr", 3)
def rule(*args):
  return "%s and %s" % (args[1], args[3])


@define(141, "expr", 3)
def rule(*args):
  return "%s or %s" % (args[1], args[3])


@define(142, "expr", 2)
def rule(*args):
  return "~%s" % args[2]


@define(143, "expr", 5)
def rule(*args):
  return "%s and 1**%s or %s" % (args[1], args[3], args[5])


@define(144, "expr", 3)
def rule(*args):
  return factory.assign(*args[2])


@define(145, "expr", 3)
def rule(*args):
  return "(%s)" % args[2]


@define(147, "setlist", 2)
def rule(*args):
  args[1].extend(args[2])
  return args[1]


@define(150, "assign", 3)
def rule(*args):
  return [args[1], args[3]]


@define(151, "assign", 3)
def rule(*args):
  return [args[1], args[3]]


@define(152, "args", 2)
def rule(*args):
  args[1].append(args[2])
  return args[1]


@define(153, "args", 2)
def rule(*args):
  args[1][0].append(args[2])
  return args[1]


@define(154, "args", 4)
def rule(*args):
  args[1][0].append("'', %s" % factory.assign(args[2], args[4]))
  return args[1]


@define(155, "args", 2)
def rule(*args):
  return args[1]


@define(156, "args", 0)
def rule(*args):
  return [ [ ] ]


@define(157, "lnameargs", 3)
def rule(*args):
  args[3].append(args[1])
  return args[3]


@define(160, "lvalue", 3)
def rule(*args):
  return factory.quoted(args[2])


@define(162, "nameargs", 3)
def rule(*args):
  return [[factory.ident(args[2])], args[3]]


@define(163, "nameargs", 2)
def rule(*args):
  return [args[1], args[2]]


@define(164, "nameargs", 4)
def rule(*args):
  return [args[1], args[3]]


@define(165, "names", 3)
def rule(*args):
  args[1].append(args[3])
  return args[1]


@define(166, "names", 1)
def rule(*args):
  return [args[1]]


@define(167, "name", 3)
def rule(*args):
  return factory.quoted(args[2])


@define(168, "name", 1)
def rule(*args):
  return "'%s'" % (args[1],)


@define(170, "filename", 3)
def rule(*args):
  return "%s.%s" % (args[1], args[3])


@define(175, "quoted", 2)
def rule(*args):
  if args[2] is not None:
    args[1].append(args[2])
  return args[1]


@define(176, "quoted", 0)
def rule(*args):
  return []


@define(177, "quotable", 1)
def rule(*args):
  return factory.ident(args[1])


@define(178, "quotable", 1)
def rule(*args):
  return factory.text(args[1])


@define(179, "quotable", 1)
def rule(*args):
  return None


keys = sorted(RULES.keys())

# Did we leave any holes?

assert keys == range(len(RULES))

# No?  Okay, convert RULES from a dict to a tuple for faster access:

RULES = tuple(RULES[key] for key in keys)

# Clean up temporary variables.

del keys
del define
