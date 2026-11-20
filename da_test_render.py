"""Security and formula checks: python -m unittest da_test_render -v."""
import unittest
from html.parser import HTMLParser
from da_render import render, render_question, _HTML, _MATH


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class RenderTests(unittest.TestCase):
    def assert_safe(self, html):
        for tag, attrs in Tags(html).elements:
            self.assertIn(tag, _HTML | _MATH)
            for name, value in attrs.items():
                self.assertFalse(name.startswith('on'))
                self.assertNotIn(name, {'style', 'src', 'srcdoc', 'xlink:href'})
                if name == 'href':
                    self.assertFalse(value.lower().startswith(('javascript:', 'data:', 'vbscript:')))

    def test_markdown(self):
        html = render('**Bold** and *italic*\n\n- One\n- Two\n\n`x < y`')
        self.assertIn('<strong>Bold</strong>', html)
        self.assertIn('<ul>', html)
        self.assertIn('<code>x &lt; y</code>', html)

    def test_inline_math(self):
        html = render(r'The score is $z=\frac{x-\mu}{\sigma}$.')
        self.assertIn('<math', html)
        self.assertIn('<mfrac>', html)
        self.assertIn('display="inline"', html)
        self.assertNotIn('\\frac', html)
        self.assert_safe(html)

    def test_display_math(self):
        html = render('$$\n\\sum_{i=1}^{n} x_i^2\n$$')
        self.assertIn('display="block"', html)
        self.assertIn('<msubsup>', html)
        self.assert_safe(html)

    def test_real_formulas(self):
        for latex in [r'\sqrt{\frac{1}{n-1}\sum_i(x_i-\bar{x})^2}',
                      r'\chi^2=\sum\frac{(O-E)^2}{E}',
                      r'P(A\mid B)=\frac{P(A\cap B)}{P(B)}',
                      r'\begin{pmatrix}1&2\\3&4\end{pmatrix}',
                      r'\hat{y}=\beta_0+\beta_1x', r'\mathbb{R}']:
            with self.subTest(latex=latex):
                html = render('$' + latex + '$')
                self.assertIn('<math', html)
                self.assert_safe(html)

    def test_raw_html_is_text(self):
        html = render('<script>alert(1)</script><img src=x onerror=alert(1)><iframe srcdoc="bad"></iframe>')
        self.assertNotIn('<script', html)
        self.assertNotIn('<img', html)
        self.assertNotIn('<iframe', html)
        self.assert_safe(html)

    def test_unsafe_links(self):
        for text in ['[x](javascript:alert%281%29)', '[x](data:text/html,hello)',
                     '[x](vbscript:msgbox)', '[x](jav&#x61;script:bad)']:
            with self.subTest(text=text):
                self.assert_safe(render(text))
        self.assertIn('href="https://example.com"', render('[safe](https://example.com)'))

    def test_math_injection(self):
        for latex in [r'\text{<script>alert(1)</script>}',
                      r'\text{<img src=x onerror=alert(1)>}',
                      r'\href{javascript:alert(1)}{x}',
                      r'\style{background:url(javascript:bad)}{x}',
                      r'\text{</mtext><script>alert(1)</script><mtext>}']:
            with self.subTest(latex=latex):
                try:
                    html = render('$' + latex + '$')
                except ValueError:
                    continue
                self.assert_safe(html)
                self.assertNotIn('<script', html)

    def test_code_and_escaped_dollars_are_not_math(self):
        self.assertNotIn('<math', render(r'`$x$` and \$5'))
        self.assertNotIn('<math', render('```latex\n$x$\n```'))
        self.assertNotIn('<math', render('unmatched $ here'))

    def test_question_copy(self):
        original = {'prompt':'**Question**', 'answer':'$x^2$', 'explanation':'Steps'}
        result = render_question(original)
        self.assertNotIn('prompt_html', original)
        self.assertEqual(result['options_html'], [])
        self.assertIn('<math', result['answer_html'])
        result = render_question(dict(original, options=['$x$', '**y**']))
        self.assertEqual(len(result['options_html']), 2)

    def test_size_and_type_limits(self):
        with self.assertRaises(TypeError):
            render(None)
        with self.assertRaises(ValueError):
            render('x'*100001)


if __name__ == '__main__':
    unittest.main()
