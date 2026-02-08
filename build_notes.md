# Build Commands & Notes

## Build Commands

To build the APK using Buildozer (assuming you have `buildozer` installed or use the GitHub Action):

```bash
# Debug Build
buildozer android debug

# Release Build (requires signing)
buildozer android release

# Clear Build Cache (if you have issues)
buildozer android clean
```

## Prerequisites

### System Dependencies (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk wget \
    autoconf libtool libtool-bin pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    cmake libffi-dev libssl-dev
```

**Important**: `libtool-bin` is required on Ubuntu 24+ to prevent libffi build failures.

### Python Dependencies
```bash
pip install --upgrade pip
pip install --upgrade buildozer cython==0.29.36 python-for-android
```

**Note**: Python 3.11 is recommended for best compatibility with Kivy and python-for-android.

## Troubleshooting Common Errors

### 1. License Not Accepted
**Error**: "Skipping following packages as the license is not accepted"
**Fix**: The workflow now uses `android.accept_sdk_license = True` in buildozer.spec. For manual builds, you'll be prompted to accept.

### 2. Broken Pipe
**Error**: `yes: standard output: Broken pipe`
**Fix**: This is usually a side effect of another error causing Buildozer to exit early. Check the logs *before* the "Broken pipe" message for the real error.

### 3. libffi Build Failure
**Error**: `configure.ac:215: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE`
**Fix**: Install `libtool-bin` package:
```bash
sudo apt-get install libtool-bin
```
This is the most common cause of build failures on Ubuntu 24+.

### 4. HTTP 502 / Download Failures
**Error**: `Download failed: HTTP Error 502: Bad Gateway`
**Fix**:
- The workflow now uses the `develop` branch of python-for-android which has updated recipe URLs.
- Alternatively, clear cache and retry: `buildozer android clean`

### 5. Java/Gradle Errors
**Fix**:
- Ensure you are using Java 17 (recommended for Android API 33).
- Run `buildozer android debug` with `log_level = 2` in buildozer.spec to see full Gradle output.

## GitHub Actions CI/CD

The repository uses GitHub Actions to automatically build the APK on every push to main. The workflow:
1. Sets up Python 3.11
2. Installs all required system dependencies (including libtool-bin)
3. Caches buildozer dependencies for faster builds
4. Builds the APK using buildozer
5. Uploads the APK as an artifact
6. Creates a GitHub release with the APK

## Local Build Instructions

If you prefer to build locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/kskreddy2k7/quiz-ai-app.git
   cd quiz-ai-app
   ```

2. Install dependencies (see Prerequisites above)

3. Build the APK:
   ```bash
   buildozer android debug
   ```

4. Find the APK in `bin/` directory

## Alternative: Build with GitHub Codespaces

For a zero-setup build environment:

1. Open the repository in GitHub Codespaces
2. Install dependencies:
   ```bash
   sudo apt-get update && sudo apt-get install -y openjdk-17-jdk libtool-bin
   pip install buildozer cython==0.29.36 python-for-android
   ```
3. Run: `buildozer android debug`

**Note**: Codespaces provide a consistent Ubuntu environment with all base tools pre-installed.
