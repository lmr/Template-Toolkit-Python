import errno
import os
import re
import sys

from template import util
from template.base import Base, TemplateException
from template.constants import *
from template.plugin.filter import Filter
from template.util import Literal, EvaluateCode, unpack, dynamic_filter


# Static filters:

def html_filter(text):
  return (text.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;")
              .replace('"', "&quot;"))

def html_paragraph(text):
  return ("<p>\n"
          + "\n</p>\n\n<p>\n".join(re.split(r"(?:\r?\n){2,}", str(text)))
          + "</p>\n")

def html_para_break(text):
  return re.sub(r"(\r?\n){2,}", r"\1<br />\1<br />\1", text)

def html_line_break(text):
  return re.sub(r"(\r?\n)", r"<br />\1", text)

URI_ESCAPES = dict((chr(x), "%%%02X" % x) for x in range(256))

def uri_filter(text):
  return re.sub(r"[^;\/?:@&=+\$,A-Za-z0-9\-_.!~*'()]",
                lambda m: URI_ESCAPES[m.group()], text)

def ucfirst(text):
  if text:
    text = text[0].upper() + text[1:]
  return text

def lcfirst(text):
  if text:
    text = text[0].lower() + text[1:]
  return text

def stderr(*args):
  for arg in args:
    sys.stderr.write(str(arg))
  return ""

def collapse(text):
  return re.sub(r"\s+", " ", text.strip())


# Dynamic filter factories:

@dynamic_filter
def html_entity_filter_factory(context):
  from htmlentitydefs import codepoint2name
  def encode(char):
    name = codepoint2name.get(char)
    if name is not None:
      return "&%s;" % name
    else:
      return "%%%02X" % char
  def html_entity_filter(text=""):
    return re.sub(r"[^\n\r\t !#$%'-;=?-~]",
                  lambda m: encode(ord(m.group(0))), text)
  return html_entity_filter

@dynamic_filter
def indent_filter_factory(context, pad=4):
  try:
    pad = " " * int(pad)
  except:
    pass
  def indent_filter(text=""):
    return re.sub(r"(?m)^(?=(?s).)", lambda _: pad, text)
  return indent_filter

@dynamic_filter
def format_filter_factory(context, formatstr="%s"):
  def format_filter(text=""):
    # The "rstrip" is to emulate Perl's strip, which elides trailing nulls.
    return "\n".join(formatstr % string
                     for string in text.rstrip("\n").split("\n"))
  return format_filter


@dynamic_filter
def truncate_filter_factory(context, length=32, char="..."):
  def truncate_filter(text=""):
    if len(text) <= length:
      return text
    else:
      return text[:length-len(char)] + char
  return truncate_filter

@dynamic_filter
def repeat_filter_factory(context, count=1):
  def repeat_filter(text=""):
    return str(text) * int(count)
  return repeat_filter

@dynamic_filter
def replace_filter_factory(context, search="", replace=""):
  def replace_filter(text=""):
    return re.sub(str(search), lambda _: str(replace), str(text))
  return replace_filter

@dynamic_filter
def remove_filter_factory(context, search="", *args):
  def remove_filter(text=""):
    return re.sub(search, "", text)
  return remove_filter

@dynamic_filter
def eval_filter_factory(context):
  def eval_filter(text=""):
    return context.process(util.Literal(text))
  return eval_filter

@dynamic_filter
def python_filter_factory(context):
  if not context.eval_python():
    return None, TemplateException("python", "EVAL_PYTHON is not set")
  def python_filter(text):
    return util.EvaluateCode(text, context, context.stash())
  return python_filter

@dynamic_filter
def redirect_filter_factory(context, file, options=None):
  outpath = context.config().get("OUTPUT_PATH")
  if not outpath:
    return None, TemplateException("redirect", "OUTPUT_PATH is not set")
  if not isinstance(options, dict):
    options = { "binmode": options }
  def redirect_filter(text=""):
    outpath = context.config().get("OUTPUT_PATH")
    if not outpath:
      return ""
    try:
      try:
        os.makedirs(outpath)
      except OSError, e:
        if e.errno != errno.EEXIST:
          raise
      outpath += "/" + str(file)
      mode = "w%s" % (options.get("binmode") and "b" or "")
      fh = open(outpath, mode)
      fh.write(text)
      fh.close()
    except Exception, e:
      raise TemplateException("redirect", e)
    return ""
  return redirect_filter

@dynamic_filter
def stdout_filter_factory(context, options=None):
  if not isinstance(options, dict):
    options = {"binmode": options}
  def stdout_filter(text):
    sys.stdout.write(text)
    return ""
  return stdout_filter



FILTERS = {
  "html": html_filter,
  "html_para": html_paragraph,
  "html_break": html_para_break,
  "html_para_break": html_para_break,
  "html_line_break": html_line_break,
  "uri": uri_filter,
  "upper": str.upper,
  "lower": str.lower,
  "ucfirst": ucfirst,
  "lcfirst": lcfirst,
  "stderr": stderr,
  "trim": str.strip,
  "null": lambda *_: "",
  "collapse": collapse,

  # dynamic filters
  "html_entity": html_entity_filter_factory,
  "indent":      indent_filter_factory,
  "format":      format_filter_factory,
  "truncate":    truncate_filter_factory,
  "repeat":      repeat_filter_factory,
  "replace":     replace_filter_factory,
  "remove":      remove_filter_factory,
  "eval":        eval_filter_factory,
  "evaltt":      eval_filter_factory,
  "python":      python_filter_factory,
  "redirect":    redirect_filter_factory,
  "file":        redirect_filter_factory,
  "stdout":      stdout_filter_factory,
 }

class Filters(Base):
  def __init__(self, params):
    Base.__init__(self)
    self.FILTERS  = params.get("FILTERS")  or {}
    self.TOLERANT = params.get("TOLERANT") or False
    self.DEBUG    = (params.get("DEBUG") or 0) & DEBUG_FILTERS

  def fetch(self, name, args, context):
    factory = None
    error   = None

    if not isinstance(name, str):
      if isinstance(name, Filter):
        factory = name.factory()
        if not factory:
          return self.error(name.error())
      else:
        return name, None
    else:
      factory = self.FILTERS.get(name) or FILTERS.get(name)
      if not factory:
        return None, STATUS_DECLINED
    is_dynamic = getattr(factory, "dynamic_filter", False)

    if callable(factory):
      if is_dynamic:
        try:
          retval = factory(context, *(args or []))
          if isinstance(retval, (tuple, list)):
            filter, error = util.unpack(retval, 2)
          else:
            filter, error = retval, None
        except TemplateException, e:
          error = error or e
        except Exception, e:
          error = error or TemplateException(ERROR_FILTER, str(e))
        if not (error or callable(filter)):
          error = "invalid FILTER for '%s' (not callable)" % name
      else:
        filter = factory
    else:
      error = "invalid FILTER entry for '%s' (not callable)" % name

    if not error:
      return filter, None
    elif self.TOLERANT:
      return None, STATUS_DECLINED
    else:
      return error, STATUS_ERROR

  def store(self, name, filter):
    self.FILTERS[name] = filter
    return True, None
