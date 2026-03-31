from typing import Optional, BinaryIO, Dict
import io
import logging
import asyncio
from e2b import AsyncSandbox as E2BSandboxSDK
from app.core.config import get_settings
from app.domain.models.tool_result import ToolResult
from app.domain.external.sandbox import Sandbox

logger = logging.getLogger(__name__)


class ShellSession:
    def __init__(self):
        self.output_lines: list = []
        self.handle = None
        self.is_running = False


class E2BSandbox(Sandbox):
    def __init__(self, sandbox: E2BSandboxSDK, sandbox_id: str):
        self._sandbox = sandbox
        self._sandbox_id = sandbox_id
        self._sessions: Dict[str, ShellSession] = {}

    @property
    def id(self) -> str:
        return self._sandbox_id

    @property
    def cdp_url(self) -> str:
        return ""

    @property
    def vnc_url(self) -> str:
        return ""

    def _get_session(self, session_id: str) -> ShellSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ShellSession()
        return self._sessions[session_id]

    async def ensure_sandbox(self) -> None:
        pass

    async def exec_command(self, session_id: str, exec_dir: str, command: str) -> ToolResult:
        session = self._get_session(session_id)
        session.output_lines = []
        session.is_running = True

        try:
            full_command = f"cd {exec_dir} 2>/dev/null || true && {command}"

            def on_stdout(output):
                line = output.line if hasattr(output, 'line') else str(output)
                session.output_lines.append(line + "\n")

            def on_stderr(output):
                line = output.line if hasattr(output, 'line') else str(output)
                session.output_lines.append(line + "\n")

            handle = await self._sandbox.commands.run(
                full_command,
                background=True,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )
            session.handle = handle

            return ToolResult(
                success=True,
                message="Command started",
                data={"session_id": session_id}
            )
        except Exception as e:
            session.is_running = False
            logger.error(f"Failed to exec command: {e}")
            return ToolResult(success=False, message=str(e))

    async def view_shell(self, session_id: str, console: bool = False) -> ToolResult:
        session = self._get_session(session_id)
        output = "".join(session.output_lines)
        return ToolResult(
            success=True,
            message="Shell view",
            data={"output": output, "running": session.is_running}
        )

    async def wait_for_process(self, session_id: str, seconds: Optional[int] = None) -> ToolResult:
        session = self._get_session(session_id)
        if not session.handle:
            return ToolResult(success=True, message="No process running", data={"output": ""})
        try:
            if seconds:
                await asyncio.wait_for(session.handle.wait(), timeout=seconds)
            else:
                await session.handle.wait()
            session.is_running = False
            output = "".join(session.output_lines)
            return ToolResult(success=True, message="Process finished", data={"output": output})
        except asyncio.TimeoutError:
            output = "".join(session.output_lines)
            return ToolResult(success=True, message="Timeout", data={"output": output})
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def write_to_process(self, session_id: str, input_text: str, press_enter: bool = True) -> ToolResult:
        session = self._get_session(session_id)
        if not session.handle:
            return ToolResult(success=False, message="No process running")
        try:
            text = input_text + ("\n" if press_enter else "")
            await session.handle.send_stdin(text)
            return ToolResult(success=True, message="Input sent")
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def kill_process(self, session_id: str) -> ToolResult:
        session = self._get_session(session_id)
        if session.handle:
            try:
                await session.handle.kill()
                session.is_running = False
            except Exception as e:
                logger.warning(f"Failed to kill process: {e}")
        return ToolResult(success=True, message="Process killed")

    async def file_write(self, file: str, content: str, append: bool = False,
                         leading_newline: bool = False, trailing_newline: bool = False,
                         sudo: bool = False) -> ToolResult:
        try:
            final_content = content
            if leading_newline:
                final_content = "\n" + final_content
            if trailing_newline:
                final_content = final_content + "\n"

            if append:
                try:
                    existing = await self._sandbox.files.read(file)
                    final_content = existing + final_content
                except Exception:
                    pass

            await self._sandbox.files.write(file, final_content)
            return ToolResult(success=True, message="File written")
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_read(self, file: str, start_line: int = None,
                        end_line: int = None, sudo: bool = False) -> ToolResult:
        try:
            content = await self._sandbox.files.read(file)
            if start_line or end_line:
                lines = content.split("\n")
                start = (start_line - 1) if start_line else 0
                end = end_line if end_line else len(lines)
                content = "\n".join(lines[start:end])
            return ToolResult(success=True, message="File read", data={"content": content})
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_exists(self, path: str) -> ToolResult:
        try:
            result = await self._sandbox.commands.run(
                f"test -e '{path}' && echo 'exists' || echo 'not_exists'"
            )
            exists = "exists" in (result.stdout or "")
            return ToolResult(success=True, message="File exists check", data={"exists": exists})
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_delete(self, path: str) -> ToolResult:
        try:
            await self._sandbox.commands.run(f"rm -rf '{path}'")
            return ToolResult(success=True, message="File deleted")
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_list(self, path: str) -> ToolResult:
        try:
            files = await self._sandbox.files.list(path)
            items = []
            for f in files:
                items.append({
                    "name": f.name if hasattr(f, 'name') else str(f),
                    "type": f.type if hasattr(f, 'type') else "unknown"
                })
            return ToolResult(success=True, message="Directory listed", data=items)
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_replace(self, file: str, old_str: str, new_str: str, sudo: bool = False) -> ToolResult:
        try:
            content = await self._sandbox.files.read(file)
            new_content = content.replace(old_str, new_str, 1)
            await self._sandbox.files.write(file, new_content)
            return ToolResult(success=True, message="File replaced")
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_search(self, file: str, regex: str, sudo: bool = False) -> ToolResult:
        try:
            result = await self._sandbox.commands.run(f"grep -n '{regex}' '{file}' 2>&1 || true")
            return ToolResult(success=True, message="Search done", data={"matches": result.stdout or ""})
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_find(self, path: str, glob_pattern: str) -> ToolResult:
        try:
            result = await self._sandbox.commands.run(
                f"find '{path}' -name '{glob_pattern}' 2>/dev/null || true"
            )
            files = [f for f in (result.stdout or "").split("\n") if f.strip()]
            return ToolResult(success=True, message="Files found", data=files)
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_upload(self, file_data: BinaryIO, path: str, filename: str = None) -> ToolResult:
        try:
            content = file_data.read()
            await self._sandbox.files.write(path, content)
            return ToolResult(success=True, message="File uploaded")
        except Exception as e:
            return ToolResult(success=False, message=str(e))

    async def file_download(self, path: str) -> BinaryIO:
        content = await self._sandbox.files.read(path, format="bytes")
        return io.BytesIO(content)

    async def destroy(self) -> bool:
        try:
            await self._sandbox.kill()
            return True
        except Exception as e:
            logger.error(f"Failed to destroy E2B sandbox: {e}")
            return False

    async def get_browser(self):
        raise NotImplementedError("Browser via VNC is not supported in E2B sandbox mode")

    @classmethod
    async def create(cls) -> 'E2BSandbox':
        settings = get_settings()
        api_key = settings.e2b_api_key
        sandbox = await E2BSandboxSDK.create(
            api_key=api_key,
            timeout=3600,
        )
        sandbox_id = sandbox.sandbox_id if hasattr(sandbox, 'sandbox_id') else str(id(sandbox))
        logger.info(f"Created E2B sandbox: {sandbox_id}")
        return cls(sandbox=sandbox, sandbox_id=sandbox_id)

    @classmethod
    async def get(cls, sandbox_id: str) -> 'E2BSandbox':
        settings = get_settings()
        api_key = settings.e2b_api_key
        sandbox = await E2BSandboxSDK.connect(
            sandbox_id=sandbox_id,
            api_key=api_key,
        )
        logger.info(f"Connected to E2B sandbox: {sandbox_id}")
        return cls(sandbox=sandbox, sandbox_id=sandbox_id)
