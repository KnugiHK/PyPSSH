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
python3 pssh_extractor.py init.mp4
```

The script will output the base64-encoded PSSH boxes for both Widevine and PlayReady (if present).

### Developer Usage
You can also import the script as a module and use the `extract_pssh()` function to get the PSSH boxes programmatically. Here's an example of how to use the function in your own Python code:

```python
from pssh_extractor import extract_pssh

# Provide the path to your MP4 init segment
file_path = 'path_to_init_segment.mp4'

# Open the file and read the bytes
with open(file_path, 'rb') as f:
    init_segment = f.read()

# Extract the PSSH boxes (Widevine and PlayReady)
widevine_pssh, playready_pssh = extract_pssh(init_segment)

# Print the raw bytes of PSSH data
if widevine_pssh:
    print(f"Widevine PSSH: {widevine_pssh}")
else:
    print("No Widevine PSSH found")

if playready_pssh:
    print(f"PlayReady PSSH: {playready_pssh}")
else:
    print("No PlayReady PSSH found")
```
