Certainly! I'll create an uninstall script that reverses the actions of the installation script. Here's a script that will uninstall the components we installed:

```bash
#!/bin/bash

# Function to run sudo commands
run_sudo() {
    if ! sudo -n "$@"; then
        echo "Failed to run: sudo $*"
        echo "Make sure the user has NOPASSWD sudo permissions."
        exit 1
    fi
}

echo "Starting uninstallation process..."

# 1. Remove Python 3.12
run_sudo apt remove -y python3.12 python3.12-venv python3.12-dev
run_sudo add-apt-repository -y --remove ppa:deadsnakes/ppa

# 2. Remove PostgreSQL
run_sudo apt remove -y postgresql postgresql-contrib

# 3. Remove pip and any globally installed packages
run_sudo apt remove -y python3-pip

# 4. Remove the .local/bin directory and its contents
rm -rf ~/.local/bin

# 5. Remove the PATH addition from .profile
sed -i '/# set PATH so it includes user'"'"'s private bin if it exists/d' ~/.profile
sed -i '/if \[ -d "$HOME\/.local\/bin" \] ; then/d' ~/.profile
sed -i '/    PATH="$HOME\/.local\/bin:$PATH"/d' ~/.profile
sed -i '/fi/d' ~/.profile

# 6. Clean up any leftover dependencies
run_sudo apt autoremove -y

# 7. Remove the requirements.txt file if it exists
if [ -f "requirements.txt" ]; then
    rm requirements.txt
    echo "Removed requirements.txt file."
fi

echo "Uninstallation completed. Please note:"
echo "1. This script doesn't remove user data or configurations in the home directory."
echo "2. Database data from PostgreSQL may still exist. To completely remove it, use: sudo apt purge postgresql*"
echo "3. You may need to manually remove any remaining files or configurations."
echo "4. Log out and log back in for all changes to take effect."
```

To use this uninstall script:

1. Save it as `uninstall.sh` (or any name you prefer).
2. Make it executable with `chmod +x uninstall.sh`.
3. Run it with `./uninstall.sh`.

Please note:

1. This script attempts to remove the software and configurations we added, but it may not catch everything, especially if you've made additional changes or installations.
2. It doesn't remove user data or configurations in the home directory, other than the `.local/bin` directory.
3. For PostgreSQL, this script only removes the packages. If you want to completely remove all data and configurations, you'd need to use `sudo apt purge postgresql*` instead of `remove`.
4. The script removes the PATH modification from `.profile`, but you'll need to log out and log back in (or source the `.profile` file) for this change to take effect.
5. If you've installed any Python packages globally or in a virtual environment, you may need to remove those manually.
6. Always review an uninstall script carefully before running it, especially one that uses sudo commands, to ensure it's doing exactly what you want.

After running this script, it's a good idea to reboot your system to ensure all changes have taken effect and no remnants of the removed software are still running in memory.