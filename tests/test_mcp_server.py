import pytest
import sys
import os
import threading
import time

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
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        assert controller is not None
    
    def test_controller_works(self):
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        result = controller.wait(10)
        assert result.success is True


class TestMCPServerThreadSafety:
    def test_singleton_controller(self):
        from remoteuse.server.mcp_server import get_controller
        controller1 = get_controller()
        controller2 = get_controller()
        assert controller1 is controller2
    
    def test_concurrent_get_controller(self):
        from remoteuse.server.mcp_server import get_controller, cleanup_controller
        
        cleanup_controller()
        
        controllers = []
        errors = []
        
        def get_and_store():
            try:
                ctrl = get_controller()
                controllers.append(ctrl)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=get_and_store) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(controllers) == 10
        assert all(c is controllers[0] for c in controllers)
    
    def test_cleanup_controller(self):
        from remoteuse.server.mcp_server import get_controller, cleanup_controller, _controller
        
        controller = get_controller()
        assert controller is not None
        
        cleanup_controller()
        
        from remoteuse.server import mcp_server
        assert mcp_server._controller is None


class TestMCPServerLogging:
    def test_logger_exists(self):
        from remoteuse.server.mcp_server import logger
        assert logger is not None
        assert logger.name == "remoteuse.server.mcp_server"


class TestMCPToolExecution:
    def test_screenshot_via_controller(self):
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        result = controller.screenshot()
        assert result.success is True
        assert "image_base64" in result.data
        assert "width" in result.data
        assert "height" in result.data
    
    def test_wait_via_controller(self):
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        result = controller.wait(10)
        assert result.success is True
        assert "10" in result.message
    
    def test_mouse_move_via_controller(self):
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        result = controller.mouse_move(500, 500)
        assert result.success is True
        assert "500" in result.message
    
    def test_key_press_via_controller(self):
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        result = controller.key_press("escape")
        assert result.success is True
        assert "escape" in result.message.lower()
    
    def test_error_handling_via_controller(self):
        from remoteuse.server.mcp_server import get_controller
        controller = get_controller()
        result = controller.click_at(-10, 100)
        assert result.success is False
        assert result.error is not None


class TestMCPServerRestart:
    def test_cleanup_and_restart(self):
        from remoteuse.server.mcp_server import get_controller, cleanup_controller
        
        controller1 = get_controller()
        controller1_id = id(controller1)
        
        cleanup_controller()
        
        controller2 = get_controller()
        controller2_id = id(controller2)
        
        assert controller1_id != controller2_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
