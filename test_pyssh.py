import base64
import struct
import uuid
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Updated to import from pypssh instead of pssh_extractor
from pypssh import DRMSystemID, PSSH, main


# --- Helper Functions for Mock Data ---

def create_mock_pssh_box(system_id: uuid.UUID, payload: bytes = b"") -> bytes:
    """Creates a valid byte representation of a PSSH box for testing."""
    # box_size (4) + 'pssh' (4) + version/flags (4) + system_id (16) + payload
    box_size = 28 + len(payload)
    size_bytes = struct.pack('>I', box_size)
    marker = b'pssh'
    version_flags = b'\x00\x00\x00\x00'
    return size_bytes + marker + version_flags + system_id.bytes + payload


@pytest.fixture
def mock_widevine_box():
    return create_mock_pssh_box(DRMSystemID.WIDEVINE, b'widevine_data')


@pytest.fixture
def mock_playready_box():
    return create_mock_pssh_box(DRMSystemID.PLAYREADY, b'playready_data')


@pytest.fixture
def mock_fairplay_box():
    return create_mock_pssh_box(DRMSystemID.FAIRPLAY, b'fairplay_data')


@pytest.fixture
def unknown_drm_id():
    return uuid.uuid4()


# --- Unit Tests for Static/Helper Methods ---

class TestPSSHStaticMethods:
    def test_find_next_pssh_box_success(self, mock_widevine_box):
        # Pad with garbage data before and after
        data = b'garbage_prefix' + mock_widevine_box + b'garbage_suffix'
        
        # Test extraction
        box = PSSH._find_next_pssh_box(data, 0)
        assert box == mock_widevine_box

    def test_find_next_pssh_box_not_found(self):
        data = b'no_pssh_marker_here'
        assert PSSH._find_next_pssh_box(data, 0) is None

    def test_find_next_pssh_box_marker_too_early(self):
        # 'pssh' found, but no space for the 4-byte size header
        data = b'pssh_but_no_size'
        assert PSSH._find_next_pssh_box(data, 0) is None

    def test_find_next_pssh_box_truncated_data(self, mock_widevine_box):
        # Cut the box short so box_end > len(data)
        truncated_data = mock_widevine_box[:-5]
        assert PSSH._find_next_pssh_box(truncated_data, 0) is None

    def test_find_next_pssh_box_too_small(self):
        # Create a box smaller than the minimum 28 bytes
        box_size = 20
        size_bytes = struct.pack('>I', box_size)
        data = size_bytes + b'pssh' + b'\x00' * 12
        assert PSSH._find_next_pssh_box(data, 0) is None

    def test_get_system_id(self, mock_widevine_box):
        extracted_id = PSSH._get_system_id(mock_widevine_box)
        assert extracted_id == DRMSystemID.WIDEVINE


# --- Unit Tests for PSSH Object Creation & Parsing ---

class TestPSSHClass:
    def test_from_bytes_all_systems(self, mock_widevine_box, mock_playready_box, mock_fairplay_box):
        # Combine all boxes with some garbage data in between
        data = (b'start' + mock_widevine_box + 
                b'mid' + mock_playready_box + 
                b'end' + mock_fairplay_box)
        
        pssh = PSSH.from_bytes(data)
        
        assert pssh.widevine == mock_widevine_box
        assert pssh.playready == mock_playready_box
        assert pssh.fairplay == mock_fairplay_box

    def test_from_bytes_unknown_system(self, mock_widevine_box, unknown_drm_id):
        unknown_box = create_mock_pssh_box(unknown_drm_id, b'unknown_data')
        data = mock_widevine_box + unknown_box
        
        pssh = PSSH.from_bytes(data)
        
        # Widevine should be parsed, unknown box should be ignored
        assert pssh.widevine == mock_widevine_box
        assert pssh.playready is None
        assert pssh.fairplay is None

    @patch('builtins.open', new_callable=mock_open)
    def test_parse_from_file(self, mock_file, mock_widevine_box):
        mock_file.return_value.read.return_value = mock_widevine_box
        
        pssh = PSSH.parse('dummy_path.mp4')
        
        mock_file.assert_called_once_with('dummy_path.mp4', 'rb')
        assert pssh.widevine == mock_widevine_box
        assert pssh.playready is None


# --- Unit Tests for Base64 Conversions ---

class TestBase64Encoding:
    def test_get_widevine_b64(self, mock_widevine_box):
        pssh = PSSH(widevine=mock_widevine_box)
        expected_b64 = base64.b64encode(mock_widevine_box).decode('utf-8')
        assert pssh.get_widevine_b64() == expected_b64

    def test_get_widevine_b64_none(self):
        pssh = PSSH(widevine=None)
        assert pssh.get_widevine_b64() is None

    def test_get_playready_b64(self, mock_playready_box):
        pssh = PSSH(playready=mock_playready_box)
        expected_b64 = base64.b64encode(mock_playready_box).decode('utf-8')
        assert pssh.get_playready_b64() == expected_b64

    def test_get_fairplay_b64(self, mock_fairplay_box):
        pssh = PSSH(fairplay=mock_fairplay_box)
        expected_b64 = base64.b64encode(mock_fairplay_box).decode('utf-8')
        assert pssh.get_fairplay_b64() == expected_b64


# --- Unit Tests for CLI (main function) ---

class TestCLI:
    @patch('sys.argv', ['pypssh.py'])
    @patch('pypssh.logger.error')
    def test_main_missing_args(self, mock_logger):
        # Catch the SystemExit exception that sys.exit() naturally raises
        with pytest.raises(SystemExit) as excinfo:
            main()
            
        # Verify the exit code was 1
        assert excinfo.value.code == 1
        mock_logger.assert_called_once_with("Usage: python3 pssh_extractor.py <init_segment_file_path>")

    @patch('sys.argv', ['pypssh.py', 'test_segment.mp4'])
    @patch('pypssh.PSSH.parse')
    @patch('pypssh.logger.info')
    def test_main_success(self, mock_logger_info, mock_parse, mock_widevine_box):
        # Mock the parsed PSSH object
        mock_pssh_instance = MagicMock()
        mock_pssh_instance.get_widevine_b64.return_value = "widevine_b64_string"
        mock_pssh_instance.get_playready_b64.return_value = None
        mock_pssh_instance.get_fairplay_b64.return_value = None
        mock_parse.return_value = mock_pssh_instance
        
        main()
        
        mock_parse.assert_called_once_with('test_segment.mp4')
        
        # Verify logger was called to output the results
        mock_logger_info.assert_any_call("Widevine PSSH: widevine_b64_string")
        mock_logger_info.assert_any_call("No PlayReady PSSH found")
        mock_logger_info.assert_any_call("No FairPlay PSSH found")