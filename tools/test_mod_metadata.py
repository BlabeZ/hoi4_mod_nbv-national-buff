"""Protect user-selected names and published Workshop identity across builds."""
from pathlib import Path
import unittest
from unittest.mock import patch
from mod_metadata import descriptor_text


class MetadataTests(unittest.TestCase):
    def render(self, text):
        with patch.object(Path, 'exists', return_value=True), patch.object(Path, 'read_text', return_value=text):
            return descriptor_text('descriptor.mod', '0.1.11')

    def test_custom_metadata_survives_version_update(self):
        text = ('name="自定义显示名"\nversion = "0.1.10" # release\n'
                'remote_file_id="1234567890"\npicture="cover.png"\n'
                'supported_version="1.19.*"\ntags={ "Utilities" }\n')
        self.assertEqual(self.render(text), text.replace('"0.1.10"', '"0.1.11"'))

    def test_missing_version_does_not_rebuild_other_fields(self):
        text = 'name="另一个名称"\nremote_file_id="1234567890"\n'
        self.assertEqual(self.render(text), text + 'version="0.1.11"\n')

    def test_ambiguous_metadata_is_not_silently_replaced(self):
        for text in ('name="A"\nname="B"\nversion="1"\n',
                     'name="A"\nversion="1"\nversion="2"\n'):
            with self.assertRaises(ValueError):
                self.render(text)

    def test_first_build_has_defaults(self):
        with patch.object(Path, 'exists', return_value=False):
            text = descriptor_text('descriptor.mod', '0.1.11')
        self.assertIn('name="国家BUFF统计 UI"', text)
        self.assertIn('version="0.1.11"', text)
        self.assertNotIn('remote_file_id', text)


if __name__ == '__main__':
    unittest.main()
