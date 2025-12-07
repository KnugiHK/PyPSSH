#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import struct
import uuid
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class DRMSystemID:
    WIDEVINE = uuid.UUID('edef8ba9-79d6-4ace-a3c8-27dcd51d21ed')
    PLAYREADY = uuid.UUID('9a04f079-9840-4286-ab92-e65be0885f95')
    FAIRPLAY = uuid.UUID('94ce86fb-07bb-4b43-adb8-93d2fa968ca2')

@dataclass
class PSSH:
    widevine: Optional[bytes] = None
    playready: Optional[bytes] = None
    fairplay: Optional[bytes] = None

    @classmethod
    def parse(cls, file_path: str | Path) -> 'PSSH':
        """Parse PSSH boxes from an init segment file.

        Args:
            file_path: Path to the init segment file.

        Returns:
            PSSH object containing the extracted boxes.
        """
        with open(file_path, 'rb') as f:
            init_segment = f.read()
        return cls.from_bytes(init_segment)

    @classmethod
    def from_bytes(cls, init_segment: bytes) -> 'PSSH':
        """Extract PSSH boxes from raw bytes.

        Args:
            init_segment: Raw bytes containing PSSH boxes.

        Returns:
            PSSH object containing the extracted boxes.
        """
        widevine_pssh = None
        playready_pssh = None
        
        offset = 0
        while offset < len(init_segment):
            pssh_box = cls._find_next_pssh_box(init_segment, offset)
            if not pssh_box:
                break

            system_id = cls._get_system_id(pssh_box)
            if system_id == DRMSystemID.WIDEVINE:
                widevine_pssh = pssh_box
            elif system_id == DRMSystemID.PLAYREADY:
                playready_pssh = pssh_box
            elif system_id == DRMSystemID.FAIRPLAY:
                fairplay_pssh = pssh_box

            offset = init_segment.find(pssh_box) + len(pssh_box)

        return cls(widevine_pssh, playready_pssh, fairplay_pssh)

    def get_widevine_b64(self) -> Optional[str]:
        """Get base64 encoded Widevine PSSH box."""
        return base64.b64encode(self.widevine).decode('utf-8') if self.widevine else None

    def get_playready_b64(self) -> Optional[str]:
        """Get base64 encoded PlayReady PSSH box."""
        return base64.b64encode(self.playready).decode('utf-8') if self.playready else None

    def get_fairplay_b64(self) -> Optional[str]:
        """Get base64 encoded FairPlay PSSH box."""
        return base64.b64encode(self.fairplay).decode('utf-8') if self.fairplay else None

    @staticmethod
    def _find_next_pssh_box(data: bytes, offset: int) -> Optional[bytes]:
        """Find and extract the next PSSH box in the data."""
        marker_pos = data.find(b'pssh', offset)
        if marker_pos == -1:
            return None

        size_pos = marker_pos - 4
        if size_pos < 0:
            return None

        size_bytes = data[size_pos:marker_pos]
        box_size = struct.unpack('>I', size_bytes)[0]
        box_end = size_pos + box_size

        if box_end > len(data):
            return None

        pssh_box = data[size_pos:box_end]
        if len(pssh_box) < 28:  # Minimum PSSH box size
            return None

        return pssh_box

    @staticmethod
    def _get_system_id(pssh_box: bytes) -> uuid.UUID:
        """Extract system ID from PSSH box."""
        system_id_bytes = pssh_box[12:28]
        return uuid.UUID(bytes=system_id_bytes)


def main():
    import sys
    if len(sys.argv) != 2:
        logger.error("Usage: python3 pssh_extractor.py <init_segment_file_path>")
        sys.exit(1)

    pssh = PSSH.parse(sys.argv[1])
    print(type(pssh))

    logger.info("Extracted PSSH Data:")
    logger.info("--------------------")
    
    widevine_b64 = pssh.get_widevine_b64()
    logger.info(f"Widevine PSSH: {widevine_b64}" if widevine_b64 else "No Widevine PSSH found")
    logger.info("")
    
    playready_b64 = pssh.get_playready_b64()
    logger.info(f"PlayReady PSSH: {playready_b64}" if playready_b64 else "No PlayReady PSSH found")
    logger.info("")

    fairplay_b64 = pssh.get_fairplay_b64()
    logger.info(f"FairPlay PSSH: {fairplay_b64}" if fairplay_b64 else "No FairPlay PSSH found")


if __name__ == "__main__":
    main()
