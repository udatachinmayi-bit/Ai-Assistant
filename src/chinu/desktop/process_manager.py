import logging
import psutil
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessManager:
    """
    A manager for handling system processes using psutil.
    Provides functionalities to find, list, and kill processes,
    as well as fetch system resource usage statistics.
    """

    def kill_process(self, name: str) -> bool:
        """
        Terminates a process by its name.

        Args:
            name (str): The name of the process to kill.

        Returns:
            bool: True if the process was killed, False otherwise.
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and name.lower() in proc.info['name'].lower():
                    logger.info(f"Found process {proc.info['name']} with PID {proc.info['pid']}. Terminating.")
                    p = psutil.Process(proc.info['pid'])
                    p.kill()
                    return True
            logger.warning(f"Process with name '{name}' not found.")
            return False
        except psutil.NoSuchProcess:
            logger.error(f"Process with name '{name}' not found for termination.")
            return False
        except psutil.AccessDenied:
            logger.error(f"Access denied to terminate process with name '{name}'.")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while trying to kill process '{name}': {e}", exc_info=True)
            return False

    def find_process(self, name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Finds processes by name.

        Args:
            name (str): The name of the process to find.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of dictionaries with process info, or None if not found.
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                if proc.info['name'] and name.lower() in proc.info['name'].lower():
                    processes.append(proc.info)
            if not processes:
                logger.info(f"No process found with name containing '{name}'.")
                return None
            return processes
        except Exception as e:
            logger.error(f"An error occurred while searching for process '{name}': {e}", exc_info=True)
            return None

    def list_processes(self) -> List[Dict[str, Any]]:
        """
        Lists all running processes.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a process.
        """
        try:
            return [proc.as_dict(attrs=['pid', 'name', 'username']) for proc in psutil.process_iter()]
        except Exception as e:
            logger.error(f"Failed to list processes: {e}", exc_info=True)
            return []

    def cpu_usage(self) -> float:
        """
        Gets the current system-wide CPU utilization.

        Returns:
            float: The CPU usage percentage.
        """
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(f"Failed to get CPU usage: {e}", exc_info=True)
            return 0.0

    def memory_usage(self) -> Dict[str, Any]:
        """
        Gets the system memory usage statistics.

        Returns:
            Dict[str, Any]: A dictionary with memory usage details.
        """
        try:
            return psutil.virtual_memory()._asdict()
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}", exc_info=True)
            return {}

    def disk_usage(self) -> Dict[str, Any]:
        """
        Gets the system disk usage statistics for the root partition.

        Returns:
            Dict[str, Any]: A dictionary with disk usage details.
        """
        try:
            return psutil.disk_usage('/')._asdict()
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}", exc_info=True)
            return {}

if __name__ == '__main__':
    # Example usage of the ProcessManager
    manager = ProcessManager()

    print("CPU Usage:", manager.cpu_usage())
    print("Memory Usage:", manager.memory_usage())
    print("Disk Usage:", manager.disk_usage())

    # Find a common process like 'python' or 'chrome'
    process_name_to_find = "chrome"
    found_processes = manager.find_process(process_name_to_find)
    if found_processes:
        print(f"Found processes for '{process_name_to_find}': {found_processes}")
    else:
        print(f"No processes found for '{process_name_to_find}'.")

    # List all processes (can be a very long list)
    # all_processes = manager.list_processes()
    # print(f"Total running processes: {len(all_processes)}")

    # Example of killing a process (use with caution)
    # Note: Replace 'notepad.exe' with a safe process to test, like an instance of notepad.
    # if manager.kill_process("notepad.exe"):
    #     print("Notepad process killed successfully.")
    # else:
    #     print("Failed to kill Notepad process.")