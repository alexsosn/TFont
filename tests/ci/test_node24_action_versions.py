from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOWS = Path('.github/workflows')
CHECKOUT = re.compile(r'uses:\s*actions/checkout@(v\d+)')
SETUP_PYTHON = re.compile(r'uses:\s*actions/setup-python@(v\d+)')


class Node24ActionVersionContractTests(unittest.TestCase):
    def _workflow_texts(self) -> dict[str, str]:
        return {
            path.name: path.read_text(encoding='utf-8')
            for path in sorted(WORKFLOWS.glob('*.yml'))
        }

    def test_checkout_uses_node24_major(self) -> None:
        offenders: list[str] = []
        seen = 0
        for name, text in self._workflow_texts().items():
            for match in CHECKOUT.finditer(text):
                seen += 1
                if match.group(1) != 'v5':
                    offenders.append(f'{name}:{match.group(1)}')
        self.assertGreater(seen, 0, 'expected tracked workflows to use actions/checkout')
        self.assertEqual(offenders, [], f'checkout action majors must be v5: {offenders}')

    def test_setup_python_uses_node24_major(self) -> None:
        offenders: list[str] = []
        seen = 0
        for name, text in self._workflow_texts().items():
            for match in SETUP_PYTHON.finditer(text):
                seen += 1
                if match.group(1) != 'v6':
                    offenders.append(f'{name}:{match.group(1)}')
        self.assertGreater(seen, 0, 'expected tracked workflows to use actions/setup-python')
        self.assertEqual(offenders, [], f'setup-python action majors must be v6: {offenders}')

    def test_deprecated_node20_action_tokens_are_absent(self) -> None:
        joined = '\n'.join(self._workflow_texts().values())
        self.assertNotIn('actions/checkout@v4', joined)
        self.assertNotIn('actions/setup-python@v5', joined)


if __name__ == '__main__':
    unittest.main()
