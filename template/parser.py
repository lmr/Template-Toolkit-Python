import re
import sys

from template import grammar, directive, base, util
from template.constants import *

CONTINUE = 0
ACCEPT   = 1
ERROR    = 2
ABORT    = 3

TAG_STYLE = {
  "default":   (r"\[%",   r"%\]"),
  "template1": (r"[[%]%", r"%[]%]"),
  "metatext":  (r"%%",    r"%%"),
  "html":      (r"<!--",  r"-->"),
  "mason":     (r"<%",    r">"),
  "asp":       (r"<%",    r"%>"),
  "php":       (r"<\?",   r"\?>"),
  "star":      (r"\[\*",  r"\*\]"),
}

TAG_STYLE["template"] = TAG_STYLE["tt2"] = TAG_STYLE["default"]

DEFAULT_STYLE = {
  "START_TAG":   TAG_STYLE["default"][0],
  "END_TAG":     TAG_STYLE["default"][1],
  "ANYCASE":     False,
  "INTERPOLATE": False,
  "PRE_CHOMP":   False,
  "POST_CHOMP":  False,
  "V1DOLLAR":    False,
  "EVAL_PYTHON": False,
}

QUOTED_ESCAPES = {"n": "\n", "r": "\r", "t": "\t"}

CHOMP_FLAGS = r"[-=~+]"

CHOMP_ALL = str(CHOMP_ALL)
CHOMP_COLLAPSE = str(CHOMP_COLLAPSE)
CHOMP_GREEDY = str(CHOMP_GREEDY)
CHOMP_NONE = str(CHOMP_NONE)

CHOMP_CONST = {
  "-": CHOMP_ALL,
  "=": CHOMP_COLLAPSE,
  "~": CHOMP_GREEDY,
  "+": CHOMP_NONE
}

def Chomp(x):
  return re.sub(r"[-=~+]", lambda m: CHOMP_CONST[m.group(0)], str(x))


GRAMMAR = re.compile(r"""
    # strip out any comments
    (\#[^\n]*)
  |
    # a quoted string matches in $3
    (["'])    # $2 - opening quote, ' or "
    (         # $3 - quoted text buffer
      (?:     # repeat group (no backreference)
        \\\\  # an escaped backslash
      |       # ...or...
        \\\2  # an escaped quote \" or \' (match $1)
      |       # ...or...
        .     # any other character
      | \n
      )*?     # non-greedy repeat
    )         # end of $3
    \2        # match opening quote
  |
    # an unquoted number matches in $4
    (-? \d+ (?: \. \d+ )?)  # numbers
  |
    # filename matches in $5
      ( /? \w+ (?: (?: /|::? ) \w* )+ | /\w+ )
  |
    # an identifier matches in $6
    (\w+)
  |
    # an unquoted word or symbol matches in $7
    (  [(){}\[\]:;,/\\]  # misc parentheses and symbols
    |  ->                # arrow operator (for future?)
    |  [-+*]             # math operations
    |  \${?              # dollar with optional left brace
    |  =>                # like "="
    |  [=!<>]?= | [!<>]  # equality tests
    |  &&? | \|\|?       # boolean ops
    |  \.\.?             # n..n sequence
    |  \S+               # something unquoted
    )                    # end of $7
""", re.X)

QUOTED_STRING = re.compile(r"""
   ( (?: \\. | [^\$] ){1,3000} ) # escaped or non-'$' character [$1]
   |
   ( \$ (?:                    # embedded variable              [$2]
     (?: \{ ([^\}]*) \} )      # ${ ... }                       [$3]
     |
     ([\w\.]+)                 # $word                          [$4]
     )
   )
""", re.X)

class Parser(base.Base):
  def __init__(self, param):
    base.Base.__init__(self)
    self.START_TAG   = param.get("START_TAG") or DEFAULT_STYLE["START_TAG"]
    self.END_TAG     = param.get("END_TAG")   or DEFAULT_STYLE["END_TAG"]
    self.TAG_STYLE   = "default"
    self.ANYCASE     = False
    self.INTERPOLATE = False
    self.PRE_CHOMP   = CHOMP_NONE
    self.POST_CHOMP  = CHOMP_NONE
    self.V1DOLLAR    = False
    self.EVAL_PYTHON = False
    self.FILE_INFO   = 1
    self._ERROR      = ""
    self.INFOR = 0
    self.INWHILE = 0
    self.STYLE = []

    for key in self.__dict__.keys():
      if key in param:
        setattr(self, key, param[key])

    self.FILEINFO = []
    self.DEFBLOCKS = []
    self.DEFBLOCK_STACK = []

    factory = param.get("FACTORY", directive.Directive)
    self.GRAMMAR = grammar.Grammar()
    self.FACTORY = factory({'NAMESPACE': param.get('NAMESPACE')})
    self.LEXTABLE = self.GRAMMAR.LEXTABLE
    self.STATES = self.GRAMMAR.STATES
    self.RULES = self.GRAMMAR.RULES
    if not self.new_style(param):
      return self.Error(self.error())

  def new_style(self, config):
    if self.STYLE:
      style = self.STYLE[-1]
    else:
      style = DEFAULT_STYLE
    style = style.copy()
    tagstyle = config.get("TAG_STYLE")
    if tagstyle:
      tags = TAG_STYLE.get(tagstyle)
      if tags is None:
        return self.error("Invalid tag style: %s" % tagstyle)
      start, end = tags
      config["START_TAG"] = config.get("START_TAG", start)
      config["END_TAG"] = config.get("END_TAG", end)
    for key in DEFAULT_STYLE.keys():
      value = config.get(key)
      if value is not None:
        style[key] = value
    self.STYLE.append(style)
    return style

  def old_style(self):
    if len(self.STYLE) <= 1:
      return self.error("only 1 parser style remaining")
    self.STYLE.pop()
    return self.STYLE[-1]

  def location(self):
    if not self.FILE_INFO:
      return "\n"
    line = self.LINE[0]
    info = self.FILEINFO[-1]
    file_ = info.get("path") or info.get("name") or "(unknown template)"
    line = re.sub(r"-.*", "", str(line))  # might be 'n-n'
    return '#line %s "%s"\n' % (line, file_)

  def parse(self, text, info):
    self.DEFBLOCK = {}
    self.METADATA = {}
    self._ERROR = ""
    tokens = self.split_text(text)
    if tokens is None:
      return None
    self.FILEINFO.append(info)
    block = self._parse(tokens, info)
    self.FILEINFO.pop()
    if block:
      return {"BLOCK": block,
              "DEFBLOCKS": self.DEFBLOCK,
              "METADATA": self.METADATA}
    else:
      return None

  def split_text(self, text):
    tokens = []
    line = 1
    style = self.STYLE[-1]
    def make_splitter(delims):
      return re.compile(r"(?s)(.*?)%s(.*?)%s" % delims)
    splitter = make_splitter((style["START_TAG"], style["END_TAG"]))
    while True:
      match = splitter.match(text)
      if not match:
        break
      text = text[match.end():]
      pre, dir = match.group(1), match.group(2)
      prelines = pre.count("\n")
      dirlines = dir.count("\n")
      postlines = 0
      if dir.startswith("#"):
        # commment out entire directive except for any end chomp flag
        match = re.search(CHOMP_FLAGS + "$", dir)
        if match:
          dir = match.group(0)
        else:
          dir = ""
      else:
        # PRE_CHOMP: process whitespace before tag
        match = re.match(r"(%s)?\s*" % CHOMP_FLAGS, dir)
        chomp = Chomp(match and match.group(1) or style["PRE_CHOMP"])
        if match:
          dir = dir[match.end():]
        if chomp and pre:
          if chomp == CHOMP_ALL:
            pre = re.sub(r"(\n|^)[^\S\n]*\Z", "", pre)
          elif chomp == CHOMP_COLLAPSE:
            pre = re.sub(r"(\s+)\Z", " ", pre)
          elif chomp == CHOMP_GREEDY:
            pre = re.sub(r"(\s+)\Z", "", pre)

      # POST_CHOMP: process whitespace after tag
      match = re.search(r"\s*(%s)?\s*$" % CHOMP_FLAGS, dir)
      chomp = Chomp(match and match.group(1) or style["POST_CHOMP"])
      if match:
        dir = dir[:match.start()]
      if chomp:
        if chomp == CHOMP_ALL:
          match = re.match(r"[^\S\n]*\n", text)
          if match:
            text = text[match.end():]
            postlines += 1
        elif chomp == CHOMP_COLLAPSE:
          match = re.match(r"\s+", text)
          if match:
            text = " " + text[match.end():]
            postlines += match.group().count("\n")
        elif chomp == CHOMP_GREEDY:
          match = re.match(r"\s+", text)
          if match:
            text = text[match.end():]
            postlines += match.group().count("\n")

      if pre:
        if style["INTERPOLATE"]:
          tokens.append([pre, line, 'ITEXT'])
        else:
          tokens.extend(["TEXT", pre])
      line += prelines
      if dir:
        # The TAGS directive is a compile-time switch.
        match = re.match(r"(?i)TAGS\s+(.*)", dir)
        if match:
          tags = re.split(r"\s+", match.group(1))
          if len(tags) > 1:
            splitter = make_splitter(tuple(re.escape(x) for x in tags[:2]))
          elif tags[0] in TAG_STYLE:
            splitter = make_splitter(TAG_STYLE[tags[0]])
          else:
            sys.stderr.write("Invalid TAGS style: %s" % tags[0])
        else:
          if dirlines > 0:
            line_range = "%d-%d" % (line, line + dirlines)
          else:
            line_range = str(line)
          tokens.append([dir, line_range, self.tokenise_directive(dir)])
      line += dirlines + postlines

    if text:
      if style["INTERPOLATE"]:
        tokens.append([text, line, "ITEXT"])
      else:
        tokens.extend(["TEXT", text])

    return tokens

  def tokenise_directive(self, dirtext):
    tokens = []
    for match in GRAMMAR.finditer(dirtext):
      # ignore comments to EOL
      if match.group(1):
        continue
      # quoted string
      token = match.group(3)
      if token is not None:
        # double-quoted string may include $variable references
        if match.group(2) == '"':
          if re.search(r"[$\\]", token):
            toktype = "QUOTED"
            # unescape " and \ but leave \$ escaped so that
            # interpolate_text() doesn't incorrectly treat it
            # as a variable reference
            token = re.sub(r'\\([\\"])', r'\1', token)
            token = re.sub(r'\\([^$nrt])', r'\1', token)
            token = re.sub(r'\\([nrt])', lambda m: QUOTED_ESCAPES[m.group(1)],
                           token)
            tokens.extend(['"', '"'])
            tokens.extend(self.interpolate_text(token))
            tokens.extend(['"', '"'])
            continue
          else:
            toktype = "LITERAL"
            token = "scalar(%r)" % token
        else:
          toktype = "LITERAL"
          # Remove escaped single quotes and backslashes:
          token = re.sub(r"\\(.)",
                         lambda m: m.group(m.group(1) in "'\\"), token)
          token = "scalar(%r)" % token
      else:
        token = match.group(4)
        if token is not None:
          token = "scalar(%s)" % token
          toktype = "NUMBER"
        else:
          token = match.group(5)
          if token is not None:
            toktype = "FILENAME"
          else:
            token = match.group(6)
            if token is not None:
              # reserved words may be in lower case unless case sensitive
              if self.ANYCASE:
                uctoken = token.upper()
              else:
                uctoken = token
              toktype = self.LEXTABLE.get(uctoken)
              if toktype is not None:
                token = uctoken
              else:
                toktype = "IDENT"
            else:
              token = match.group(7)
              toktype = self.LEXTABLE.get(token, "UNQUOTED")
      tokens.extend([toktype, token])
    return tokens

  def _parse(self, tokens, info):
    self.GRAMMAR.install_factory(self.FACTORY)
    stack = [[0, None]]  # DFA stack
    coderet = None
    token = None
    in_string = False
    in_python = False
    line      = [0]
    status    = CONTINUE
    lhs = None
    text = None
    self.LINE = line
    self.FILE = info.get("name")
    self.INPYTHON = 0
    value = None

    while True:
      stateno = stack[-1][0]
      state   = self.STATES[stateno]

      # see if any lookaheads exist for the current state
      if "ACTIONS" in state:
        # get next token and expand any directives (ie. token is a
        # list) onto the front of the token list
        while token is None and tokens:
          token = tokens.pop(0)
          if isinstance(token, (list, tuple)):
            # text, line, token = token
            text, line[0], token = util.unpack(token, 3)
            if isinstance(token, (list, tuple)):
              tokens[:0] = token + [";", ";"]
              token = None  # force redo
            elif token == "ITEXT":
              if in_python:
                # don't perform interpolation in PYTHON blocks
                token = "TEXT"
                value = text
              else:
                tokens[:0] = self.interpolate_text(text, line[0])
                token = None  # force redo
          else:
            # toggle string flag to indicate if we're crossing
            # a string boundary
            if token == '"':
              in_string = not in_string
            value = tokens and tokens.pop(0) or None

        if token is None:
          token = ""

        # get the next state for the current lookahead token
        lookup = state["ACTIONS"].get(token)
        if lookup:
          action = lookup
        else:
          action = state.get("DEFAULT")

      else:
        # no lookahead assertions
        action = state.get("DEFAULT")

      # ERROR: no ACTION
      if action is None:
        break

      # shift (positive ACTION)
      if action > 0:
        stack.append([action, value])
        token = value = None
        # PERL: redo;
      else:
        # reduce (negative ACTION)
        lhs, len_, code = self.RULES[-action]
        # no action implies ACCEPTance
        if not action:
          status = ACCEPT
        # use dummy sub if code ref doesn't exist
        if not code:
          code = lambda *arg: len(arg) >= 2 and arg[1] or None
        if len_ > 0:
          codevars = [x[1] for x in stack[-len_:]]
        else:
          codevars = []
        try:
          coderet = code(self, *codevars)
        except base.Exception, e:
          return self._parse_error(str(e))
        # reduce stack by len_
        if len_ > 0:
          stack[-len_:] = []
        # ACCEPT
        if status == ACCEPT:
          return coderet
        elif status == ABORT:
          return None
        elif status == ERROR:
          break
        stack.append([self.STATES[stack[-1][0]].get("GOTOS", {}).get(lhs),
                      coderet])

    # ERROR
    if value is None:
      return self._parse_error("unexpected end of input")
    elif value == ";":
      return self._parse_error("unexpected end of directive", text)
    else:
      return self._parse_error("unexpected token (%s)" % util.unscalar_lex(value), text)

  def _parse_error(self, msg, text=None):
    line = self.LINE[0]
    if not line:
      line = "unknown"
    if text is not None:
      msg += "\n  [%% %s %%]" % text
    return self.error("line %s: %s" % (line, msg))

  def define_block(self, name, block):
    if self.DEFBLOCK is None:
      return None
    self.DEFBLOCK[name] = block
    return None

  def push_defblock(self):
    self.DEFBLOCK_STACK.append(self.DEFBLOCK)
    self.DEFBLOCK = {}

  def pop_defblock(self):
    if not self.DEFBLOCK_STACK:
      return self.DEFBLOCK
    block = self.DEFBLOCK
    self.DEFBLOCK = self.DEFBLOCK_STACK.pop(0)
    return block

  def add_metadata(self, setlist):
    setlist = [util.unscalar_lex(x) for x in setlist]
    if self.METADATA is not None:
      for key, value in util.chop(setlist, 2):
        self.METADATA[key] = value
    return None

  def interpolate_text(self, text, line=0):
    tokens = []
    for match in QUOTED_STRING.finditer(text):
      pre = match.group(1)
      var = match.group(3) or match.group(4)
      dir = match.group(2)
      # preceding text
      if pre:
        line += pre.count("\n")
        tokens.extend(("TEXT", pre.replace("\\$", "$")))
      # variable reference
      if var:
        line += dir.count("\n")
        tokens.append([dir, line, self.tokenise_directive(var)])
      # other '$' reference - treated as text
      elif dir:
        line += dir.count("\n")
        tokens.extend(("TEXT", dir))
    return tokens
