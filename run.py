import subprocess
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_services():
    # Get the root directory
    root_dir = Path(__file__).parent
    
    # Commands to run
    commands = [
        {
            'name': 'Server',
            'cmd': [sys.executable, '-m', 'uvicorn', 'main:app', '--reload', '--port', '8888'],
            'cwd': root_dir / 'server'
        },
        {
            'name': 'UI',
            'cmd': ['npm', 'run', 'dev', '--', '--port', '3001'],
            'cwd': root_dir / 'ui'
        }
    ]
    
    # Start all processes
    processes = []
    for command in commands:
        try:
            process = subprocess.Popen(
                command['cmd'],
                cwd=command['cwd'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            processes.append({
                'name': command['name'],
                'process': process
            })
            logger.info(f"Started {command['name']} service")
            logger.info(f"{command['name']} command: {' '.join(command['cmd'])}")
        except Exception as e:
            logger.error(f"Failed to start {command['name']}: {e}")
            # Kill all started processes
            for p in processes:
                p['process'].kill()
            sys.exit(1)
    
    # Monitor output
    try:
        while True:
            for p in processes:
                output = p['process'].stdout.readline()
                if output:
                    logger.info(f"[{p['name']}] {output.strip()}")
                
                error = p['process'].stderr.readline()
                if error:
                    logger.error(f"[{p['name']}] {error.strip()}")
                
                # Check if process is still running
                if p['process'].poll() is not None:
                    logger.warning(f"{p['name']} service exited with code {p['process'].returncode}")
                    # Kill all other processes
                    for other_p in processes:
                        if other_p['process'].poll() is None:
                            other_p['process'].kill()
                    sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("\nShutting down all services...")
        for p in processes:
            p['process'].kill()
        sys.exit(0)

if __name__ == "__main__":
    run_services()
