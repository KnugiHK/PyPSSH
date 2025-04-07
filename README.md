# PyPSSH

**PyPSSH** is a lightweight Python tool to extract and base64-encode Widevine and PlayReady PSSH boxes from MP4 initialization segments. It's designed for DRM diagnostics, license server debugging, and media pipeline automation.

## 🚀 Features

- Extracts Widevine and PlayReady PSSH boxes from MP4 initialization segments.
- Outputs PSSH boxes in base64 encoding for easy use.
- Can be used for debugging DRM workflows or extracting information from encrypted media files.
- Simple and efficient with minimal dependencies.

## 🧰 Usages

### Command Line Usage
To extract Widevine and PlayReady PSSH boxes from an MP4 initialization segment, run the script as follows:

```bash
python3 pypssh.py init.mp4
```

The script will output the base64-encoded PSSH boxes for both Widevine and PlayReady (if present).

### Developer Usage
You can also import the script as a module and use the `extract_pssh()` function to get the PSSH boxes programmatically. Here's an example of how to use the function in your own Python code:

```python
from pssh_extractor import PSSH
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Specify the path to the video initialization segment
video_file_path = '/path/to/video_init.mp4'  # Replace with the actual path

# Parse the PSSH data from the file
pssh = PSSH.parse(video_file_path)

logger.info("Extracted PSSH Data:")
logger.info("--------------------")

# Extract and log Widevine & PlayReady PSSH base64 data if available
widevine_b64 = pssh.get_widevine_b64()
playready_b64 = pssh.get_playready_b64()

if widevine_b64:
    logger.info(f"Widevine PSSH: {widevine_b64}")
else:
    logger.info("No Widevine PSSH found")

if playready_b64:
    logger.info(f"PlayReady PSSH: {playready_b64}")
else:
    logger.info("No PlayReady PSSH found")
```

## ⚖️ Legal

**PyPSSH** is provided under the [MIT License](LICENSE), which allows you to freely use, modify, and distribute the software. However, by using **PyPSSH**, you acknowledge the following:

### 🛡️ DRM and Copyright Compliance

**PyPSSH** may interact with DRM-protected content and is intended for diagnostic, research, and security testing purposes. It does not provide tools to bypass DRM protections but helps in identifying and handling DRM information in media files. Users are responsible for ensuring their use complies with applicable laws, including DRM and copyright regulations, and should not use **PyPSSH** for circumventing DRM protections or infringing on intellectual property rights.

### ⚠️ No Warranty and Liability

**PyPSSH** is provided "as-is," without warranty of any kind. The authors are not liable for any damages, misuse, or legal consequences arising from its use.
