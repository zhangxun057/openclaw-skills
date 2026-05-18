from pathlib import Path


def test_install_mentions_openviking_optional():
    repo_root = Path(__file__).resolve().parents[1]
    install_text = (repo_root / 'INSTALL.md').read_text(encoding='utf-8')
    assert 'templates/OBSIDIAN-NOTE.md' in install_text
    assert 'OpenViking as an optional enhancement' in install_text
    assert 'OpenViking 视为可选增强' in install_text


def test_install_documents_native_openclaw_install_flow():
    repo_root = Path(__file__).resolve().parents[1]
    install_text = (repo_root / 'INSTALL.md').read_text(encoding='utf-8')

    assert 'openclaw skills install agent-memory-system-guide' in install_text
    assert '`skills/`' in install_text
    assert 'workspace' in install_text


def test_install_documents_post_install_self_check():
    repo_root = Path(__file__).resolve().parents[1]
    install_text = (repo_root / 'INSTALL.md').read_text(encoding='utf-8')

    assert 'Post-install self-check' in install_text
    assert 'memory_capture.py bootstrap' in install_text
    assert 'SESSION-STATE.md' in install_text
    assert 'working-buffer.md' in install_text
    assert 'Detailed workflow docs' in install_text
    assert 'README_EN.md' in install_text
    assert 'README_CN.md' in install_text
    assert 'session-start' in install_text
    assert 'report' in install_text
    assert 'doctor' in install_text
    assert 'distill' in install_text
    assert 'apply' in install_text
