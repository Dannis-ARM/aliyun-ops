import logging
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict

import requests


class FileDownloader:
    """A robust file downloader with proxy support and streaming download."""

    _DEFAULT_CLASH_PROXY: Dict[str, str] = {
        "http": "http://localhost:7890",
        "https": "http://localhost:7890"
    }
    _LOG_INTERVAL = 5 * 1024 * 1024  # Log every 5MB

    def __init__(
        self,
        proxy: Optional[Dict[str, str]] = None,
        timeout: int = 300,
        use_clash_proxy: bool = False
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = timeout
        self.chunk_size = 8192

        self.session = requests.Session()
        if use_clash_proxy:
            self.session.proxies.update(self._DEFAULT_CLASH_PROXY)
        if proxy:
            self.session.proxies.update(proxy)

    def __enter__(self) -> "FileDownloader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.session.close()

    def _get_default_path(self, url: str) -> Path:
        """Extract filename from URL and generate temp path."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        filename = parsed.path.split("/")[-1] if parsed.path else "downloaded_file"
        return Path(tempfile.gettempdir()) / (filename or "downloaded_file")

    def _should_log(self, downloaded: int) -> bool:
        """Check if we should log progress (every 5MB boundary)."""
        return downloaded % self._LOG_INTERVAL < self.chunk_size

    def download(
        self,
        url: str,
        output_path: Optional[Path | str] = None,
        overwrite: bool = False,
        resume: bool = False
    ) -> Path:
        """
        Execute download task.

        Args:
            url: Download URL
            output_path: Target path (directory or full file path)
            overwrite: Overwrite existing file
            resume: Resume interrupted download (if server supports Range header)

        Returns:
            Path: Final saved file path
        """
        # 1. Determine final storage path
        if not output_path:
            final_path = self._get_default_path(url)
        else:
            final_path = Path(output_path)
            if final_path.is_dir():
                final_path = final_path / self._get_default_path(url).name

        # 2. Check conflicts
        if final_path.exists() and not overwrite:
            if not resume:
                self.logger.info("File already exists, skipping: %s", final_path)
                return final_path

        self.logger.info("Downloading: %s -> %s", url, final_path)

        # 3. Determine write mode (resume support)
        mode = "ab" if resume and final_path.exists() else "wb"
        downloaded = final_path.stat().st_size if resume and final_path.exists() else 0
        headers = {"Range": f"bytes={downloaded}-"} if resume else None

        start_time = time.time()
        try:
            with self.session.get(
                url, stream=True, timeout=self.timeout, headers=headers
            ) as response:
                # Handle 206 Partial Content for resume
                if resume and response.status_code == 206:
                    self.logger.info("Resuming download from byte %d", downloaded)
                else:
                    response.raise_for_status()
                    downloaded = 0  # Reset if not resuming

                total_size = int(response.headers.get("content-length", 0)) + downloaded
                if total_size > 0:
                    self.logger.info("Total size: %.2f MB", total_size / (1024 * 1024))

                final_path.parent.mkdir(parents=True, exist_ok=True)

                with open(final_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            self._log_progress(downloaded, total_size)

                elapsed = time.time() - start_time
                speed = (downloaded / 1024 / 1024) / elapsed if elapsed > 0 else 0
                self.logger.info(
                    "Download complete: %s (%.2f MB in %.1fs, %.2f MB/s)",
                    final_path, downloaded / (1024 * 1024), elapsed, speed
                )
                return final_path

        except requests.RequestException as e:
            self.logger.error("Download failed: %s - %s", url, e)
            if final_path.exists() and final_path.stat().st_size == 0:
                final_path.unlink()
            raise

    def _log_progress(self, downloaded: int, total_size: int) -> None:
        """Internal progress logging (every 5MB)."""
        if self._should_log(downloaded) and total_size > 0:
            progress = (downloaded / total_size) * 100
            self.logger.info("Progress: %.1f%% (%d bytes)", progress, downloaded)
