"""
SSH Client Utilities
Common SSH operations for ECS management.
"""

import json
import logging
import posixpath
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Union
import codetiming
import paramiko

# Default encoding for subprocess on Windows
ENCODING = "utf-8"


@dataclass
class ProxyConfig:
    """
    SSH proxy configuration supporting SOCKS5 and HTTP proxies.
    
    Supports JSON serialization/deserialization for configuration files.
    
    Example JSON format:
        {
            "type": "socks5",
            "host": "127.0.0.1",
            "port": 1080,
            "username": "user",      // optional
            "password": "pass"       // optional
        }
    """
    
    type: Literal["socks5", "http", "direct"] = "direct"
    host: str = "127.0.0.1"
    port: int = 1080
    username: Optional[str] = None
    password: Optional[str] = None
    
    @classmethod
    def from_json(cls, json_str: Union[str, dict]) -> "ProxyConfig":
        """
        Create ProxyConfig from JSON string or dict.
        
        Args:
            json_str: JSON string or dict containing proxy configuration
        
        Returns:
            ProxyConfig instance
        """
        if isinstance(json_str, str):
            data = json.loads(json_str)
        else:
            data = json_str
        return cls(
            type=data.get("type", "direct"),
            host=data.get("host", "127.0.0.1"),
            port=data.get("port", 1080),
            username=data.get("username"),
            password=data.get("password"),
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            "type": self.type,
            "host": self.host,
            "port": self.port,
        }
        if self.username:
            data["username"] = self.username
        if self.password:
            data["password"] = self.password
        return json.dumps(data)
    
    def create_socket(self, target_host: str, target_port: int, timeout: float = 30.0) -> socket.socket:
        """
        Create a socket connection through the proxy.
        
        Args:
            target_host: Target SSH server hostname
            target_port: Target SSH server port
            timeout: Socket timeout in seconds
        
        Returns:
            Connected socket object
        
        Raises:
            ImportError: If required proxy library is not installed
            ConnectionError: If connection fails
        """
        if self.type == "direct":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((target_host, target_port))
            return sock
        
        try:
            import socks
        except ImportError:
            raise ImportError(
                "PySocks is required for proxy connections. Install with: pip install PySocks"
            )
        
        # Create proxy socket using PySocks
        sock = socks.socksocket()
        sock.settimeout(timeout)
        
        if self.type == "socks5":
            proxy_type = socks.SOCKS5
            sock.set_proxy(
                proxy_type=proxy_type,
                addr=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                rdns=True,  # Use remote DNS resolution
            )
        elif self.type == "http":
            proxy_type = socks.HTTP
            sock.set_proxy(
                proxy_type=proxy_type,
                addr=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
            )
        else:
            raise ValueError(f"Unsupported proxy type: {self.type}")
        
        # Connect to target through proxy
        sock.connect((target_host, target_port))
        return sock


class SSHKeyManager:
    """Manage SSH key generation and public key operations."""

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.logger = logger or logging.getLogger("ssh-key")

    def generate(
        self,
        local_key_path: Path,
        key_type: str = "ed25519",
        comment: str = "generated-by-aliyun-ops",
        force: bool = False,
    ) -> Path:
        """
        Generate SSH key pair locally if not exists.
        
        Args:
            local_key_path: Path to store the private key
            key_type: Key type (ed25519, rsa, etc.)
            comment: Comment for the key
            force: Force regenerate even if key exists
        
        Returns:
            Path to the generated private key
        """
        if local_key_path.exists() and not force:
            self.logger.info("SSH key already exists: %s", local_key_path)
            return local_key_path

        self.logger.info("Generating new SSH key pair: %s", local_key_path)
        
        # Ensure .ssh directory exists
        local_key_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate key pair (no passphrase for automation)
        cmd = [
            "ssh-keygen",
            "-t", key_type,
            "-f", str(local_key_path),
            "-N", "",  # No passphrase
            "-C", comment
        ]
        
        result = subprocess.run(cmd, capture_output=True, encoding=ENCODING)
        if result.returncode != 0:
            self.logger.error("Failed to generate SSH key: %s", result.stderr)
            raise RuntimeError(f"ssh-keygen failed: {result.stderr}")
        
        self.logger.info("SSH key generated successfully!")
        return local_key_path

    def read_public_key(self, local_key_path: Path) -> str:
        """
        Read the public key content.
        
        Args:
            local_key_path: Path to the private key
        
        Returns:
            Public key content as string
        """
        pub_key_path = Path(str(local_key_path) + ".pub")
        
        if not pub_key_path.exists():
            self.logger.error("Public key not found: %s", pub_key_path)
            raise FileNotFoundError(f"Public key not found: {pub_key_path}")
        
        content = pub_key_path.read_text(encoding=ENCODING).strip()
        self.logger.debug("Public key: %s...", content[:50])
        return content


class SSHClientV2:
    """
    SSH client implementation using Paramiko with Fabric-style API.
    Provides SSH functionality with proxy support via PySocks.
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        host: str = "",
        user: str = "",
        ssh_key: Optional[Path] = None,
        proxy: Optional[ProxyConfig] = None,
        port: int = 22,
    ) -> None:
        self.logger = logger or logging.getLogger("ssh-client-v2")
        self.host = host
        self.user = user
        self.ssh_key = ssh_key
        self.proxy = proxy or ProxyConfig()
        self.port = port
        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._transport: Optional[paramiko.Transport] = None
        self._sftp: Optional[paramiko.SFTPClient] = None
        self._remote_home: Optional[str] = None

    def configure(
        self,
        host: str,
        user: str,
        ssh_key: Path,
        proxy: Optional[Union[ProxyConfig, dict, str]] = None,
        port: int = 22,
    ) -> None:
        """
        Configure SSH connection parameters.
        
        Args:
            host: SSH host address
            user: SSH username
            ssh_key: Path to SSH private key
            proxy: Proxy configuration (ProxyConfig, dict, or JSON string)
            port: SSH port (default: 22)
        """
        self.host = host
        self.user = user
        self.ssh_key = ssh_key
        self.port = port
        
        # Handle proxy configuration
        if proxy is not None:
            if isinstance(proxy, ProxyConfig):
                self.proxy = proxy
            elif isinstance(proxy, dict):
                self.proxy = ProxyConfig(**proxy)
            elif isinstance(proxy, str):
                self.proxy = ProxyConfig.from_json(proxy)
            else:
                raise TypeError(f"Invalid proxy type: {type(proxy)}")
        else:
            self.proxy = ProxyConfig()
        
        # Reset connection when configuration changes
        self.close()

    def _get_transport(self) -> paramiko.Transport:
        """Get or create Paramiko Transport with proxy support."""
        if self._transport is None or not self._transport.is_active():
            if not self.ssh_key:
                raise ValueError("SSH key not configured")
            
            self.logger.debug("Creating SSH transport to %s@%s:%d", self.user, self.host, self.port)
            
            # Create socket (possibly through proxy)
            if self.proxy.type != "direct":
                self.logger.debug("Using proxy: %s %s:%d", self.proxy.type, self.proxy.host, self.proxy.port)
                sock = self.proxy.create_socket(self.host, self.port)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30.0)
                sock.connect((self.host, self.port))
            
            # Create transport from socket
            self._transport = paramiko.Transport(sock)
            
            # Load host keys
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.load_system_host_keys()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Load private key
            try:
                private_key = paramiko.RSAKey.from_private_key_file(str(self.ssh_key))
            except paramiko.SSHException:
                # Try other key types
                try:
                    private_key = paramiko.Ed25519Key.from_private_key_file(str(self.ssh_key))
                except paramiko.SSHException:
                    private_key = paramiko.ECDSAKey.from_private_key_file(str(self.ssh_key))
            
            # Connect
            self._transport.connect(username=self.user, pkey=private_key)
        
        return self._transport

    def run(self, command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute command on remote host via SSH."""
        self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.logger.info("🔧 [SSH] Executing: %s", command)
        self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        with codetiming.Timer(name="ssh-run", text="⏱️ Elapsed: {:.4f}s", logger=self.logger.info):
            try:
                transport = self._get_transport()
                channel = transport.open_session()
                channel.settimeout(timeout)
                channel.exec_command(command)
                
                # Read stdout
                stdout_chunks = []
                stderr_chunks = []
                
                # Collect output with real-time logging
                while not channel.exit_status_ready():
                    if channel.recv_ready():
                        chunk = channel.recv(4096)
                        stdout_chunks.append(chunk)
                        decoded = chunk.decode(ENCODING)
                        self.logger.info("📤 [SSH stdout] %s", decoded.rstrip())
                    if channel.recv_stderr_ready():
                        chunk = channel.recv_stderr(4096)
                        stderr_chunks.append(chunk)
                        decoded = chunk.decode(ENCODING)
                        self.logger.warning("📥 [SSH stderr] %s", decoded.rstrip())
                
                # Read remaining output
                while channel.recv_ready():
                    chunk = channel.recv(4096)
                    stdout_chunks.append(chunk)
                    decoded = chunk.decode(ENCODING)
                    self.logger.info("📤 [SSH stdout] %s", decoded.rstrip())
                while channel.recv_stderr_ready():
                    chunk = channel.recv_stderr(4096)
                    stderr_chunks.append(chunk)
                    decoded = chunk.decode(ENCODING)
                    self.logger.warning("📥 [SSH stderr] %s", decoded.rstrip())
                
                stdout = b"".join(stdout_chunks).decode(ENCODING)
                stderr = b"".join(stderr_chunks).decode(ENCODING)
                returncode = channel.recv_exit_status()
                
                channel.close()
                
                # Return result with appropriate icon based on exit code
                icon = "✅" if returncode == 0 else "❌"
                self.logger.info("%s [SSH] Exit code: %d", icon, returncode)
                self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                return subprocess.CompletedProcess(
                    args=command,
                    returncode=returncode,
                    stdout=stdout,
                    stderr=stderr
                )
            except Exception as e:
                self.logger.error("❌ [SSH] Execution error: %s", e)
                self.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                raise

    def run_sudo(self, command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute command with sudo on remote host."""
        return self.run(f"sudo {command}", timeout)

    def test_login(self, timeout: int = 15) -> bool:
        """
        Test SSH login to remote host.
        
        Args:
            timeout: Connection timeout in seconds
        
        Returns:
            True if login successful, False otherwise
        """
        self.logger.info("Testing SSH login for %s@%s...", self.user, self.host)
        
        try:
            result = self.run("echo 'SSH login successful!' && whoami", timeout)
            if result.returncode == 0:
                self.logger.info("SUCCESS: %s", result.stdout.strip())
                return True
            else:
                self.logger.warning("SSH login test failed: %s", result.stderr.strip())
                return False
        except Exception as e:
            self.logger.error("SSH login test error: %s", e)
            return False

    def _get_sftp(self) -> paramiko.SFTPClient:
        """Get or create SFTP client."""
        if self._sftp is None:
            transport = self._get_transport()
            sftp_client = transport.open_sftp_client()
            assert sftp_client is not None
            self._sftp = sftp_client
        return self._sftp

    def _ensure_remote_home(self) -> str:
        """Get remote home directory, caching for performance."""
        if self._remote_home is None:
            result = self.run("echo $HOME")
            stdout = result.stdout
            if stdout is None:
                stdout = ""
            home = stdout.strip()
            if not home:
                raise ValueError("Failed to get remote home directory")
            self._remote_home = home
        return self._remote_home

    def upload(self, local_path: Path, remote_path: str) -> None:
        """Upload file to remote host via SFTP with smart path handling."""
        # 1. Normalize local path
        local_p = Path(local_path).expanduser().resolve()
        if not local_p.exists():
            raise FileNotFoundError(local_p)

        try:
            sftp = self._get_sftp()
            remote_home = self._ensure_remote_home()

            # 2. Smart path handling
            r_path = str(remote_path).replace("\\", "/")
            if r_path.startswith("~"):
                r_path = r_path.replace("~", remote_home, 1)
            
            # Ensure absolute path
            if not r_path.startswith("/"):
                r_path = posixpath.join(remote_home, r_path)

            # 3. Create remote directory
            remote_dir = posixpath.dirname(r_path)
            if remote_dir and remote_dir not in ["/", "."]:
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    # Directory doesn't exist, create it
                    self.run(f'mkdir -p "{remote_dir}"', timeout=10)

            # 4. Upload file
            with codetiming.Timer(name="ssh-upload", text="⏱️ Elapsed: {:.4f}s", logger=self.logger.debug):
                sftp.put(str(local_p), r_path)
                self.logger.info("✅ Upload completed: %s", r_path)

        except Exception as e:
            self.logger.error("❌ SFTP upload failed: %s -> %s", local_p, r_path)
            self.logger.error("📝 Error detail: %s", e)
            raise
    
    def download(self, remote_path: str, local_path: Path) -> None:
        """Download file from remote host via SFTP."""
        self.logger.info("Downloading %s:%s to %s", self.user, remote_path, local_path)
        
        try:
            sftp = self._get_sftp()
            sftp.get(remote_path, str(local_path))
            self.logger.info("Download completed successfully")
        except Exception as e:
            self.logger.error("SFTP download failed: %s:%s -> %s", self.user, remote_path, local_path)
            self.logger.error("Error: %s", e)
            raise

    def test_connection(self) -> bool:
        """Test SSH connection to remote host."""
        try:
            self.run("echo 'connection test'")
            return True
        except Exception as e:
            self.logger.error("SSH connection failed: %s", e)
            return False

    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists on remote host."""
        try:
            sftp = self._get_sftp()
            sftp.stat(remote_path)
            return True
        except IOError:
            return False

    def read_remote_file(self, remote_path: str) -> str:
        """Read content of remote file."""
        try:
            sftp = self._get_sftp()
            with sftp.open(remote_path, "r") as remote_file:
                content = remote_file.read().decode(ENCODING)
            return content
        except Exception as e:
            self.logger.error("Failed to read remote file: %s", remote_path)
            self.logger.error("Error: %s", e)
            raise

    def write_remote_file(self, remote_path: str, content: str) -> None:
        """Write content to remote file."""
        try:
            sftp = self._get_sftp()
            with sftp.open(remote_path, "w") as remote_file:
                remote_file.write(content.encode(ENCODING))
            self.logger.debug("File written successfully: %s", remote_path)
        except Exception as e:
            self.logger.error("Failed to write remote file: %s", remote_path)
            self.logger.error("Error: %s", e)
            raise

    def close(self) -> None:
        """Close the SSH connection."""
        if self._sftp is not None:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None
        
        if self._transport is not None:
            try:
                self._transport.close()
            except Exception:
                pass
            self._transport = None
        
        self._ssh_client = None
        self._remote_home = None
        self.logger.debug("Connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
