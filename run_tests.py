import subprocess
import sys

print("=" * 70)
print("RemoteUse Test Suite")
print("=" * 70)

print("\n📦 Running pytest tests...\n")

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v"],
    capture_output=False
)

if result.returncode == 0:
    print("\n✅ All tests passed!")
    print("\n🚀 MCP Server is ready to run:")
    print("   python -m remoteuse.server.mcp_server")
    sys.exit(0)
else:
    print("\n❌ Some tests failed. Please fix the issues.")
    sys.exit(1)
