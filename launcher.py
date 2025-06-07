#!/usr/bin/env python3
"""
Unified Backend & Frontend Launcher for FastAPI + Next.js Dashboard System

This script provides a unified interface to launch both backend and frontend
services for development and production environments.
"""

import os
import sys
import subprocess
import signal
import time
import argparse
import json
from pathlib import Path
from typing import List, Optional
import threading
import webbrowser


class Color:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class UnifiedLauncher:
    """Unified launcher for backend and frontend services"""

    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "app"
        self.frontend_dir = self.project_root / "dashboard"

    def log(self, message: str, level: str = "INFO"):
        """Colored logging output"""
        colors = {
            "INFO": Color.OKBLUE,
            "SUCCESS": Color.OKGREEN,
            "WARNING": Color.WARNING,
            "ERROR": Color.FAIL,
            "HEADER": Color.HEADER,
        }
        color = colors.get(level, Color.ENDC)
        print(f"{color}[{level}]{Color.ENDC} {message}")

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        self.log("Checking dependencies...", "INFO")

        # Check Python dependencies
        if not (self.backend_dir / "requirements.txt").exists():
            self.log("Backend requirements.txt not found", "ERROR")
            return False

        # Check if uv is available (faster Python package manager)
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            self.log("Using uv for Python package management", "SUCCESS")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("uv not found, using pip", "WARNING")

        # Check Node.js dependencies
        if not (self.frontend_dir / "package.json").exists():
            self.log("Frontend package.json not found", "ERROR")
            return False

        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("Node.js or npm not found", "ERROR")
            return False

        self.log("All dependencies check passed", "SUCCESS")
        return True

    def install_backend_deps(self):
        """Install backend dependencies"""
        self.log("Installing backend dependencies...", "INFO")

        # Try uv first, fall back to pip
        try:
            subprocess.run(
                ["uv", "pip", "install", "-r", "requirements.txt"],
                cwd=self.backend_dir,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=self.backend_dir,
                check=True,
            )

        self.log("Backend dependencies installed", "SUCCESS")

    def install_frontend_deps(self):
        """Install frontend dependencies"""
        self.log("Installing frontend dependencies...", "INFO")

        subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
        self.log("Frontend dependencies installed", "SUCCESS")

    def setup_environment(self):
        """Setup environment files if they don't exist"""
        self.log("Setting up environment...", "INFO")

        # Backend .env
        backend_env = self.project_root / ".env"
        backend_env_example = self.project_root / ".env.example"

        if not backend_env.exists() and backend_env_example.exists():
            backend_env.write_text(backend_env_example.read_text())
            self.log("Created .env from .env.example", "SUCCESS")

        # Frontend .env.local
        frontend_env = self.frontend_dir / ".env.local"
        frontend_env_example = self.frontend_dir / ".env.example"

        if not frontend_env.exists() and frontend_env_example.exists():
            frontend_env.write_text(frontend_env_example.read_text())
            self.log("Created dashboard/.env.local from .env.example", "SUCCESS")

    def run_database_migrations(self):
        """Run database migrations"""
        self.log("Running database migrations...", "INFO")

        try:
            # Change to project root for alembic
            subprocess.run(
                ["alembic", "upgrade", "head"], cwd=self.project_root, check=True
            )
            self.log("Database migrations completed", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log(f"Migration failed: {e}", "WARNING")
            self.log("Database will be created on first backend start", "INFO")

    def start_backend(self, mode: str = "dev") -> subprocess.Popen:
        """Start the backend service"""
        self.log("Starting backend service...", "INFO")

        if mode == "dev":
            cmd = [
                "uvicorn",
                "app.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ]
        else:
            cmd = [
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--workers",
                "4",
            ]

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)

        process = subprocess.Popen(
            cmd,
            cwd=self.project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        # Start thread to handle backend output
        threading.Thread(
            target=self._handle_process_output,
            args=(process, "BACKEND", Color.OKCYAN),
            daemon=True,
        ).start()

        return process

    def start_frontend(self, mode: str = "dev") -> subprocess.Popen:
        """Start the frontend service"""
        self.log("Starting frontend service...", "INFO")

        if mode == "dev":
            cmd = ["npm", "run", "dev"]
        else:
            # Build first, then start
            subprocess.run(["npm", "run", "build"], cwd=self.frontend_dir, check=True)
            cmd = ["npm", "run", "start"]

        process = subprocess.Popen(
            cmd,
            cwd=self.frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        # Start thread to handle frontend output
        threading.Thread(
            target=self._handle_process_output,
            args=(process, "FRONTEND", Color.OKGREEN),
            daemon=True,
        ).start()

        return process

    def _handle_process_output(
        self, process: subprocess.Popen, service: str, color: str
    ):
        """Handle process output in separate thread"""
        for line in iter(process.stdout.readline, ""):
            if line:
                print(f"{color}[{service}]{Color.ENDC} {line.rstrip()}")

    def wait_for_services(self, timeout: int = 60):
        """Wait for services to be ready"""
        self.log("Waiting for services to be ready...", "INFO")

        backend_ready = False
        frontend_ready = False
        start_time = time.time()

        while time.time() - start_time < timeout:
            if not backend_ready:
                try:
                    import requests

                    response = requests.get("http://localhost:8000/", timeout=1)
                    if response.status_code == 200:
                        backend_ready = True
                        self.log("Backend service is ready!", "SUCCESS")
                except:
                    pass

            if not frontend_ready:
                try:
                    import requests

                    response = requests.get("http://localhost:3000/", timeout=1)
                    if response.status_code in [200, 404]:  # 404 is ok for Next.js dev
                        frontend_ready = True
                        self.log("Frontend service is ready!", "SUCCESS")
                except:
                    pass

            if backend_ready and frontend_ready:
                break

            time.sleep(2)

        if backend_ready and frontend_ready:
            self.log("All services are ready!", "SUCCESS")
            self.log("Backend API: http://localhost:8000", "INFO")
            self.log("Frontend Dashboard: http://localhost:3000", "INFO")
            self.log("API Documentation: http://localhost:8000/docs", "INFO")
            return True
        else:
            self.log("Services did not start within timeout", "WARNING")
            return False

    def open_browser(self):
        """Open browser with the application"""
        try:
            webbrowser.open("http://localhost:3000")
            self.log("Opened dashboard in browser", "SUCCESS")
        except:
            self.log("Could not open browser automatically", "WARNING")

    def cleanup(self):
        """Clean up processes on exit"""
        self.log("Shutting down services...", "WARNING")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        self.log("All services stopped", "SUCCESS")

    def run(
        self,
        mode: str = "dev",
        install_deps: bool = True,
        migrate: bool = True,
        open_browser: bool = True,
    ):
        """Main launcher method"""

        self.log(f"🚀 Starting FastAPI + Next.js Dashboard ({mode} mode)", "HEADER")

        try:
            # Check dependencies
            if not self.check_dependencies():
                return False

            # Install dependencies if requested
            if install_deps:
                self.install_backend_deps()
                self.install_frontend_deps()

            # Setup environment
            self.setup_environment()

            # Run migrations if requested
            if migrate:
                self.run_database_migrations()

            # Start services
            backend_process = self.start_backend(mode)
            self.processes.append(backend_process)

            frontend_process = self.start_frontend(mode)
            self.processes.append(frontend_process)

            # Wait for services to be ready
            if self.wait_for_services():
                if open_browser and mode == "dev":
                    self.open_browser()

                self.log("Press Ctrl+C to stop all services", "INFO")

                # Keep the main thread alive
                while True:
                    time.sleep(1)
                    # Check if processes are still running
                    for process in self.processes:
                        if process.poll() is not None:
                            self.log(
                                f"Service stopped unexpectedly (exit code: {process.returncode})",
                                "ERROR",
                            )
                            return False

            return True

        except KeyboardInterrupt:
            self.log("Received interrupt signal", "WARNING")
            return True
        except Exception as e:
            self.log(f"Error: {e}", "ERROR")
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Unified Backend & Frontend Launcher")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod"],
        default="dev",
        help="Launch mode (default: dev)",
    )
    parser.add_argument(
        "--no-install", action="store_true", help="Skip dependency installation"
    )
    parser.add_argument(
        "--no-migrate", action="store_true", help="Skip database migrations"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

    args = parser.parse_args()

    launcher = UnifiedLauncher()

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        launcher.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    success = launcher.run(
        mode=args.mode,
        install_deps=not args.no_install,
        migrate=not args.no_migrate,
        open_browser=not args.no_browser,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
