#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import struct
import uuid
import logging
from typing import Tuple


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Constants for PSSH box parsing
PSSH_MARKER = b'pssh'
WIDEVINE_SYSTEM_ID = uuid.UUID('edef8ba9-79d6-4ace-a3c8-27dcd51d21ed')
PLAYREADY_SYSTEM_ID = uuid.UUID('9a04f079-9840-4286-ab92-e65be0885f95')


def extract_pssh(init_segment: bytes) -> Tuple[bytes, bytes]:
    """Extracts PSSH boxes from the given init segment.  

    Args:
        init_segment (bytes): The raw bytes of the init segment.

    Returns:
        Tuple[bytes, bytes]: A tuple containing the base64 encoded Widevine and PlayReady PSSH boxes.
    """
    widevine_pssh = None
    playready_pssh = None

    # Search through the file content
    offset = 0
    while offset < len(init_segment):
        # Look for the 'pssh' marker
        marker_pos = init_segment.find(PSSH_MARKER, offset)
        if marker_pos == -1:
            break

        # Go back 4 bytes and extract get the size (4 bytes big-endian)
        size_pos = marker_pos - 4
        if size_pos < 0:
            offset = marker_pos + 4
            continue

        size_bytes = init_segment[size_pos:marker_pos]
        box_size = struct.unpack('>I', size_bytes)[0]

        # Extract the entire PSSH box
        box_end = size_pos + box_size
        if box_end > len(init_segment):
            offset = marker_pos + 4
            continue

        pssh_box = init_segment[size_pos:box_end]

        # Extract the system ID (16 bytes after the flags bytes)
        # PSSH structure: size(4) + type(4) + version(1) + flags(3) + systemID(16) + ...
        if len(pssh_box) < 28:  # 4 + 4 + 1 + 3 + 16
            offset = marker_pos + 4
            continue

        system_id_bytes = pssh_box[12:28]
        system_id = uuid.UUID(bytes=system_id_bytes)

        # Identify the DRM system and store the base64 encoded box
        if system_id == WIDEVINE_SYSTEM_ID:
            widevine_pssh = pssh_box
        elif system_id == PLAYREADY_SYSTEM_ID:
            playready_pssh = pssh_box

        # Move past this box
        offset = box_end

    return widevine_pssh, playready_pssh


def main(file_path):
    with open(file_path, 'rb') as f:
        init_segment = f.read()

    widevine_pssh, playready_pssh = extract_pssh(init_segment)

    logger.info("Extracted PSSH Data:")
    logger.info("--------------------")
    if widevine_pssh:
        logger.info(
            f"Widevine PSSH: {base64.b64encode(widevine_pssh).decode('utf-8')}")
    else:
        logger.info("No Widevine PSSH found")
    logger.info("")
    if playready_pssh:
        logger.info(
            f"PlayReady PSSH: {base64.b64encode(playready_pssh).decode('utf-8')}")
    else:
        logger.info("No PlayReady PSSH found")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logger.error(
            "Usage: python3 pssh_extractor.py <init_segment_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
