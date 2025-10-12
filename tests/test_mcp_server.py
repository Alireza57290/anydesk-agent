import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMCPServerImport:
    def test_import_mcp_server(self):
        from remoteuse.server import mcp_server
        assert mcp_server is not None
    
    def test_mcp_instance_exists(self):
        from remoteuse.server.mcp_server import mcp
        assert mcp is not None
        assert mcp.name == "RemoteUse"
    
    def test_controller_instance_exists(self):
        from remoteuse.server.mcp_server import controller
        assert controller is not None
    
    def test_controller_works(self):
        from remoteuse.server.mcp_server import controller
        result = controller.wait(10)
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
