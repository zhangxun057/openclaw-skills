from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import pytest


def load_check_release_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / 'scripts' / 'check_release.py'
    spec = importlib.util.spec_from_file_location('check_release', module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_release_check_script_passes_on_repo_state():
    if os.environ.get('AGENT_MEMORY_RELEASE_CHECK') == '1':
        pytest.skip('Avoid recursive invocation while check_release.py is already running pytest.')

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(repo_root / 'scripts' / 'check_release.py')],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert 'Release checks passed.' in result.stdout
    assert 'pytest -q' in result.stdout
    assert 'Version:' in result.stdout


def test_frontmatter_parser_preserves_colons_in_values():
    module = load_check_release_module()

    fields = module.parse_frontmatter(
        'name: memory-system\n'
        'description: Use when values contain paths like https://example.com/foo:bar\n'
        'homepage: https://github.com/cjke84/agent-memory-system-guide\n'
        'user-invocable: true\n'
        'metadata: {"openclaw": {"homepage": "https://example.com/a:b"}}\n'
    )

    assert fields['name'] == 'memory-system'
    assert fields['description'] == 'Use when values contain paths like https://example.com/foo:bar'
    assert fields['metadata'] == '{"openclaw": {"homepage": "https://example.com/a:b"}}'


def test_frontmatter_parser_rejects_invalid_lines():
    module = load_check_release_module()

    with pytest.raises(SystemExit, match='invalid line'):
        module.parse_frontmatter(
            'name: memory-system\n'
            ' bad-continuation\n'
            'homepage: https://github.com/cjke84/agent-memory-system-guide\n'
        )
