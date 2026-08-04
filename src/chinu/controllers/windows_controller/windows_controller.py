"""Controller for Windows-specific operations."""

import os
import subprocess

import psutil
import win32api
import win32con
from comtypes import CLSCTX_ALL
from ctpy import AudioUtilities, IAudioEndpointVolume
from screen_brightness_control import get_brightness, set_brightness

from chinu.controllers.windows_controller.models import ActionResponse, ProcessResponse
from chinu.logging_system.logger import get_logger

logger = get_logger("windows_controller")


class WindowsController:
    """Manages Windows OS-level operations."""

    def open_application(self, app_name: str) -> ProcessResponse:
        """Open an application by its name."""
        try:
            # Use start command to find the app in PATH or as a registered app
            process = subprocess.Popen(f'start "" "{app_name}"', shell=True)
            logger.info(f"Attempted to start application: {app_name}")
            # We don't have the PID directly, but this is a common limitation
            return ProcessResponse(
                success=True,
                message=f"Attempted to open '{app_name}'.",
                process_name=app_name,
            )
        except Exception as e:
            logger.error(f"Failed to open application {app_name}: {e}", exc_info=True)
            return ProcessResponse(
                success=False,
                message=f"Failed to open '{app_name}': {e}",
                process_name=app_name,
            )

    def close_application(self, app_name: str) -> ProcessResponse:
        """Close an application by its process name."""
        if not app_name.endswith(".exe"):
            app_name += ".exe"

        found_pids = []
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"].lower() == app_name.lower():
                try:
                    p = psutil.Process(proc.info["pid"])
                    p.terminate()
                    found_pids.append(proc.info["pid"])
                except psutil.Error as e:
                    logger.warning(f"Failed to terminate {app_name} (PID: {proc.info['pid']}): {e}")

        if not found_pids:
            return ProcessResponse(
                success=False,
                message=f"Application '{app_name}' not found.",
                process_name=app_name,
            )

        logger.info(f"Terminated {app_name} (PIDs: {found_pids}).")
        return ProcessResponse(
            success=True,
            message=f"Successfully terminated '{app_name}'.",
            process_name=app_name,
            pid=found_pids[0],  # Return first PID for simplicity
        )

    def lock_pc(self) -> ActionResponse:
        """Lock the computer."""
        try:
            win32api.LockWorkStation()
            return ActionResponse(success=True, message="PC locked successfully.")
        except Exception as e:
            logger.error(f"Failed to lock PC: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Failed to lock PC: {e}")

    def shutdown(self, force: bool = False) -> ActionResponse:
        """Shut down the computer."""
        command = "shutdown /s /t 1"
        if force:
            command += " /f"
        try:
            os.system(command)
            return ActionResponse(success=True, message="Shutdown initiated.")
        except Exception as e:
            logger.error(f"Failed to initiate shutdown: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Failed to initiate shutdown: {e}")

    def restart(self, force: bool = False) -> ActionResponse:
        """Restart the computer."""
        command = "shutdown /r /t 1"
        if force:
            command += " /f"
        try:
            os.system(command)
            return ActionResponse(success=True, message="Restart initiated.")
        except Exception as e:
            logger.error(f"Failed to initiate restart: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Failed to initiate restart: {e}")

    def set_volume(self, level: int) -> ActionResponse:
        """Set the system volume."""
        if not 0 <= level <= 100:
            return ActionResponse(success=False, message="Volume must be between 0 and 100.")
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return ActionResponse(success=True, message=f"Volume set to {level}%.")
        except Exception as e:
            logger.error(f"Failed to set volume: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Failed to set volume: {e}")

    def set_brightness(self, level: int) -> ActionResponse:
        """Set the screen brightness."""
        if not 0 <= level <= 100:
            return ActionResponse(success=False, message="Brightness must be between 0 and 100.")
        try:
            set_brightness(level)
            return ActionResponse(success=True, message=f"Brightness set to {level}%.")
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Failed to set brightness: {e}")