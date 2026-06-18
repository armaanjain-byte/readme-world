import sys
import os
import pytest

# Add the repository root to sys.path so tests can import the engine modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_state_file(mocker, tmp_path):
    """
    Automatically mock state.py's DEFAULT_STATE_FILE to point to a temporary file
    so tests never corrupt the actual state.json in the root directory.
    """
    mock_file = tmp_path / "state.json"
    mocker.patch("state.DEFAULT_STATE_FILE", str(mock_file))
    
    mock_generated = tmp_path / "generated_state.json"
    mocker.patch("state.STATE_FILE", str(mock_generated))
    yield str(mock_file)

@pytest.fixture(autouse=True)
def mock_config_file(mocker, tmp_path):
    """
    Automatically mock world.config.yml to point to a temporary file,
    ensuring tests have a consistent baseline config.
    """
    mock_file = tmp_path / "world.config.yml"
    mock_file.write_text("name: TestRunner\nworldpack: worldpacks/default", encoding="utf-8")
    
    # We patch the hardcoded path in generate_world if it exists
    mocker.patch("generate_world.CONFIG_FILE", str(mock_file))
    yield str(mock_file)
