#!/usr/bin/env python3
# oneclicksetup/cli.py

import argparse
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

from oneclicksetup.env_utils import detect_platform, load_environment

logger = logging.getLogger(__name__)

# 📌 Define default dependencies per OS
if platform.system().lower() == 'darwin':  # macOS
    DEFAULT_PY_DEPS = [
        "torch",
        "torchvision",
        "torchaudio",
        "tensorflow-macos==2.12.0",
        "keras==2.12.0",
        "ml-dtypes~=0.3.1",
        "scikit-learn",
        "opencv-python",
        "pillow",
        "numpy",
        "scipy",
        "pandas",
    ]
else:  # Linux (Ubuntu)
    DEFAULT_PY_DEPS = [
        "torch",
        "torchvision",
        "torchaudio",
        "tensorflow==2.16.2",
        "keras>=3.0.0,<3.1.0",
        "tensorboard>=2.16,<2.17",
        "ml-dtypes~=0.3.1",
        "scikit-learn",
        "opencv-python",
        "pillow",
        "numpy",
        "scipy",
        "pandas",
    ]

def setup_logging():
    """Configure logger formatting and level."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def get_script_path(script_name):
    """Return the path to a script in the 'scripts' folder."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "scripts", script_name)

def resolve_conflicts():
    """
    📌 Force uninstall conflicting packages before installation.
    This prevents issues where pip cannot downgrade/upgrade properly.
    """
    pip_cmd = "pip3"
    logger.info("🔧 Uninstalling conflicting versions of keras and tensorboard...")
    subprocess.call([pip_cmd, "uninstall", "-y", "keras", "tensorboard"])

def manage_python_deps(add, remove, uninstall):
    """
    📌 Install or force-reinstall the default Python dependencies.
    - First uninstalls keras and tensorboard to avoid version conflicts.
    - Then installs the final list (modified by --add/--remove).
    - If --uninstall flag is provided, removes specified packages.
    """
    final_deps = list(DEFAULT_PY_DEPS)
    
    for pkg in remove:
        if pkg in final_deps:
            final_deps.remove(pkg)
    final_deps += add

    logger.info(f"📦 Final list of Python packages to install: {final_deps}")
    pip_cmd = "pip3"
    subprocess.check_call([pip_cmd, "install", "--upgrade", "pip"])

    # 🔧 Force uninstall conflicts before installing dependencies
    resolve_conflicts()

    # 🚀 Install dependencies (force-reinstall to ensure correctness)
    if final_deps:
        logger.info("📥 Installing (or reinstalling) selected packages...")
        subprocess.check_call([pip_cmd, "install", "--upgrade", "--force-reinstall"] + final_deps)
    else:
        logger.info("✅ No packages selected for installation.")

    # 🗑️ Uninstall user-specified packages if --uninstall is passed
    if uninstall and remove:
        for pkg in remove:
            logger.info(f"🗑️ Uninstalling {pkg}...")
            subprocess.check_call([pip_cmd, "uninstall", "-y", pkg])

def install_dependencies(add=None, remove=None, uninstall=False):
    """
    📌 Run the OS-level install script (macOS or Ubuntu), then install Python dependencies.
    """
    if add is None:
        add = []
    if remove is None:
        remove = []

    plat = detect_platform()
    logger.info(f"🖥️ Detected platform: {plat}")

    if plat == 'macos':
        script = get_script_path("install_deps_macos.sh")
    elif plat == 'linux':
        script = get_script_path("install_deps_ubuntu.sh")
    else:
        logger.error("❌ Unsupported or unknown platform for ML dependencies.")
        return

    logger.info("🔧 Installing system + ML dependencies (OS-level)...")
    subprocess.check_call(['bash', script])
    logger.info("✅ System + ML dependencies installed successfully.")

    manage_python_deps(add=add, remove=remove, uninstall=uninstall)

def setup_ssh_keys():
    """
    📌 Check for existing SSH keys and generate them if needed.
    """
    key_type = os.getenv("SSH_KEY_TYPE", "rsa")
    key_bits = "4096"
    logger.info(f"🔑 SSH_KEY_TYPE={key_type}")
    ssh_dir = Path.home() / ".ssh"
    private_key_path = ssh_dir / f"id_{key_type}"
    
    if not ssh_dir.exists():
        logger.info(f"📂 Creating {ssh_dir} with 700 permissions.")
        ssh_dir.mkdir(mode=0o700, exist_ok=True)

    if private_key_path.exists():
        logger.info(f"✅ {private_key_path.name} already exists; skipping creation.")
    else:
        logger.info(f"🛠️ Generating new SSH key pair using '{key_type}'...")
        cmd = ["ssh-keygen", "-t", key_type, "-b", key_bits, "-N", "", "-f", str(private_key_path), "-C", "mykey"]
        subprocess.check_call(cmd)
        private_key_path.chmod(0o600)
        logger.info("🔐 SSH keys generated and permissions set.")

def print_post_install_instructions():
    """📌 Print useful pip commands after installation."""
    print("\n🚀 Installation complete!")
    print("🛠️ Useful pip commands:")
    print("  pip list                           # List installed packages")
    print("  pip install --upgrade <package>    # Upgrade a package")
    print("  pip install --upgrade --force-reinstall <package>  # Force reinstall a package")
    print("  mysetup install-deps --add <package1> <package2> ...  # Add extra packages")
    print("  mysetup install-deps --remove <package> --uninstall  # Remove and uninstall packages")
    print("  pip --version                      # Check pip version")
    print("")

def init_all(add=None, remove=None, uninstall=False):
    """
    📌 Run all setup tasks (OS-level dependencies, Python packages, SSH keys),
    then print useful post-installation instructions.
    """
    logger.info("🚀 Starting complete environment setup...")
    install_dependencies(add=add, remove=remove, uninstall=uninstall)
    setup_ssh_keys()
    logger.info("✅ All environment setup tasks have been completed successfully!")
    print_post_install_instructions()

def main():
    setup_logging()
    load_environment()

    parser = argparse.ArgumentParser(description="One-Click Environment Setup CLI")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    parser_install = subparsers.add_parser('install-deps', help='Install system + Python dependencies')
    parser_install.add_argument("--add", nargs='*', default=[], help="Add extra Python packages to the default list.")
    parser_install.add_argument("--remove", nargs='*', default=[], help="Remove certain Python packages from the default list.")
    parser_install.add_argument("--uninstall", action='store_true', help="Uninstall any packages listed in --remove.")

    parser_ssh = subparsers.add_parser('setup-ssh', help='Generate or verify SSH keys')

    parser_init = subparsers.add_parser('init', help='Run all setup tasks in one go')
    parser_init.add_argument("--add", nargs='*', default=[], help="Add extra Python packages.")
    parser_init.add_argument("--remove", nargs='*', default=[], help="Remove certain Python packages.")
    parser_init.add_argument("--uninstall", action='store_true', help="Uninstall any packages listed in --remove.")

    args = parser.parse_args()
    if args.command == 'install-deps':
        install_dependencies(add=args.add, remove=args.remove, uninstall=args.uninstall)
        print_post_install_instructions()
    elif args.command == 'setup-ssh':
        setup_ssh_keys()
    elif args.command == 'init':
        init_all(add=args.add, remove=args.remove, uninstall=args.uninstall)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

