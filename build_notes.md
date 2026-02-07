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

## Troubleshooting Common Errors

### 1. License Not Accepted
**Error**: "Skipping following packages as the license is not accepted"
**Fix**: Ensure `yes |` is used in CI/CD pipelines: `yes | buildozer android debug`. locally, you will be prompted to accept.

### 2. Broken Pipe
**Error**: `yes: standard output: Broken pipe`
**Fix**: This is usually a side effect of another error causing Buildozer to exit early. Check the logs *before* the "Broken pipe" message.

### 3. HTTP 502 / Download Failures
**Error**: `Download failed: HTTP Error 502: Bad Gateway`
**Fix**:
- Remove specific requirements like `openssl` or `sqlite3` from `buildozer.spec` if `python3` already includes them.
- Use `p4a.branch = master` in `buildozer.spec` to get the latest recipe URLs.

### 4. Java/Gradle Errors
**Fix**:
- Ensure you are using a compatible Java version (Java 17 is recommended for newer Android APIs).
- Run `buildozer android debug --log_level 2` to see full Gradle output.
