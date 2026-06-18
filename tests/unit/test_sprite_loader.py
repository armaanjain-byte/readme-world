import unittest
import os
import tempfile
from sprite_loader import load_svg_fragment, build_defs

class TestSpriteLoader(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.test_dir.name, "test.svg")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_load_svg_fragment_bare_g(self):
        content = '<g id="test"><rect width="10" height="10"/></g>'
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        result = load_svg_fragment(self.filepath)
        self.assertEqual(result, content)

    def test_load_svg_fragment_wrapped(self):
        content = '''<svg width="100" height="100">
            <g id="wrapped">
                <circle r="5"/>
            </g>
        </svg>'''
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        result = load_svg_fragment(self.filepath)
        expected = '<g id="wrapped">\n                <circle r="5"/>\n            </g>'
        self.assertEqual(result, expected)

    def test_build_defs(self):
        frag1 = '<g id="1"></g>'
        frag2 = '<g id="2"></g>'
        result = build_defs(frag1, frag2)
        self.assertIn('<defs>', result)
        self.assertIn(frag1, result)
        self.assertIn(frag2, result)
        self.assertIn('</defs>', result)

    def test_build_defs_empty(self):
        result = build_defs()
        self.assertEqual(result, "<defs>\n\n</defs>")
        
if __name__ == '__main__':
    unittest.main()
