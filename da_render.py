"""Render DA Markdown and LaTeX to sanitized HTML with native MathML.

Bootstrap from the repository root:
    python -m pip install --target .artifacts/da-tools -r da_requirements.txt
No JavaScript packages, remote assets, or stylesheet are needed by the output.
"""
from pathlib import Path
import re
import sys

_LOCAL = Path(__file__).resolve().parent / '.artifacts' / 'da-tools'
if _LOCAL.is_dir():
    sys.path.insert(0, str(_LOCAL))

try:
    import bleach
    from markdown_it import MarkdownIt
    from latex2mathml.converter import convert
except ImportError as exc:
    raise ImportError('Install root pipeline dependencies: python -m pip install '
                      '--target .artifacts/da-tools -r da_requirements.txt') from exc

_HTML = {'p', 'br', 'hr', 'strong', 'em', 's', 'blockquote', 'pre', 'code',
         'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a',
         'table', 'thead', 'tbody', 'tr', 'th', 'td'}
_MATH = {'math', 'mrow', 'mi', 'mn', 'mo', 'mtext', 'mspace', 'ms',
         'mfrac', 'msqrt', 'mroot', 'msub', 'msup', 'msubsup', 'munder',
         'mover', 'munderover', 'mtable', 'mtr', 'mtd', 'mpadded',
         'mphantom', 'menclose', 'mstyle', 'mmultiscripts', 'mprescripts', 'none'}
_ENUMS = {
    'display': {'inline', 'block'},
    'mathvariant': {'normal', 'bold', 'italic', 'bold-italic', 'double-struck',
                    'script', 'bold-script', 'fraktur', 'bold-fraktur',
                    'sans-serif', 'bold-sans-serif', 'sans-serif-italic',
                    'sans-serif-bold-italic', 'monospace'},
    'stretchy': {'true', 'false'}, 'fence': {'true', 'false'},
    'separator': {'true', 'false'}, 'accent': {'true', 'false'},
    'accentunder': {'true', 'false'}, 'displaystyle': {'true', 'false'},
    'form': {'prefix', 'infix', 'postfix'},
}
_DIMENSION = re.compile(r'-?(?:\d+(?:\.\d*)?|\.\d+)(?:em|ex|px|pt|%|mu)?\Z')


def _attribute(tag, name, value):
    if tag == 'a':
        return name in {'href', 'title'}
    if tag == 'ol' and name == 'start':
        return bool(re.fullmatch(r'\d{1,6}', value))
    if tag not in _MATH:
        return False
    if name == 'xmlns':
        return tag == 'math' and value == 'http://www.w3.org/1998/Math/MathML'
    if name in _ENUMS:
        return value in _ENUMS[name]
    if name in {'width', 'height', 'depth', 'lspace', 'rspace', 'linethickness'}:
        return bool(_DIMENSION.fullmatch(value))
    if name == 'scriptlevel':
        return bool(re.fullmatch(r'[+-]?\d{1,2}', value))
    if name in {'columnalign', 'rowalign'}:
        return all(item in {'left', 'center', 'right', 'top', 'bottom', 'baseline', 'axis'}
                   for item in value.split())
    if name in {'columnspan', 'rowspan'}:
        return bool(re.fullmatch(r'[1-9]\d?', value))
    if name == 'notation':
        return all(item in {'box', 'roundedbox', 'circle', 'top', 'bottom', 'left',
                           'right', 'updiagonalstrike', 'downdiagonalstrike',
                           'verticalstrike', 'horizontalstrike', 'radical',
                           'longdiv', 'actuarial'} for item in value.split())
    return False


def _math_html(latex, display):
    if len(latex) > 20000:
        raise ValueError('Math expression exceeds 20000 characters')
    try:
        return convert(latex, display='block' if display else 'inline')
    except Exception as exc:
        raise ValueError('Cannot render LaTeX expression') from exc


def _inline_math(state, silent):
    start = state.pos
    if state.src[start] != '$':
        return False
    delimiter = '$$' if state.src.startswith('$$', start) else '$'
    begin = start + len(delimiter)
    end = begin
    while True:
        end = state.src.find(delimiter, end)
        if end < 0:
            return False
        slash = end - 1
        while slash >= begin and state.src[slash] == '\\':
            slash -= 1
        if (end - slash - 1) % 2 == 0:
            break
        end += len(delimiter)
    content = state.src[begin:end]
    if not content.strip() or (delimiter == '$' and '\n' in content):
        return False
    if not silent:
        token = state.push('da_math', '', 0)
        token.content = content
        token.meta = {'display': delimiter == '$$'}
    state.pos = end + len(delimiter)
    return True


def _render_math(tokens, idx, options, env):
    return _math_html(tokens[idx].content, tokens[idx].meta['display'])


def render(text):
    """Return allowlisted HTML; malformed LaTeX fails instead of bypassing cleaning."""
    if not isinstance(text, str):
        raise TypeError('Markdown input must be a string')
    if len(text) > 100000:
        raise ValueError('Markdown input exceeds 100000 characters')
    parser = MarkdownIt('commonmark', {'html': False}).enable('table').enable('strikethrough')
    parser.inline.ruler.before('escape', 'da_math', _inline_math)
    parser.renderer.rules['da_math'] = _render_math
    result = parser.render(text)
    return bleach.clean(result, tags=_HTML | _MATH, attributes=_attribute,
                        protocols={'http', 'https', 'mailto'}, strip=True,
                        strip_comments=True)


def render_question(question):
    """Return a new question object with rendered fields, preserving raw content."""
    result = dict(question)
    for field in ('prompt', 'answer', 'explanation'):
        result[field + '_html'] = render(question[field])
    result['options_html'] = [render(option) for option in question.get('options', [])]
    return result
