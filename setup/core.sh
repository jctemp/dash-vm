#!/bin/bash

script_name="$(basename "$0")"
script_dir="$(cd "$(dirname "$0")" && pwd)"
script_active_dir="$(pwd)"

echo "[$script_name]:" "Setup core"


# CHECK IF DASH IS INSTALLED
if [ ! -f /usr/local/bin/dashd ]; then
    echo "> Downloading dashcore"
    mkdir "${script_active_dir}/tmp" && cd "${script_active_dir}/tmp" || return
    wget -q https://github.com/dashpay/dash/releases/download/v0.17.0.3/dashcore-0.17.0.3-x86_64-linux-gnu.tar.gz

    echo "> Copy files to /usr/local/bin"
    tar xf dashcore-*.tar.gz
    sudo install -t /usr/local/bin dashcore-*/bin/*

    cd ..
    sudo rm -rf "${ACTIVE_DIR}/tmp"
else
    echo "> dashcore already installed"
fi


# RENEW DASHCORE FOLDER
echo "> Create ${HOME}/.dashcore directory"
rm -rf "${HOME}/.dashcore" && mkdir "${HOME}/.dashcore"
cp -t "${HOME}/.dashcore" "${script_dir}/dash.conf"
chmod 666 "${HOME}/.dashcore/dash.conf"
sed -i 's/# externalip=/externalip='"$(hostname -I | awk -F" " '{print $2}')"'/' "$HOME/.dashcore/dash.conf"


# CRON JOB
if command -v crontab >/dev/null; then
    echo "> Configure Cron Job"
    crontab -l >cronJobs

    if ! grep -e dashd cronJobs >/dev/null; then
        echo "*/1 * * * * pgrep dashd || /usr/local/bin/dashd" >>cronJobs &&
            echo "> Successfully installed dashd cron job."
    else
        echo "> dashd cron job already installed."
    fi

    crontab cronJobs
    rm cronJobs
fi


echo "[$script_name]:" "Finished core setup"