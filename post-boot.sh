#!/usr/bin/env bash
#
# (C) Copyright 2019, Xilinx, Inc.
#
#!/usr/bin/env bash

install_nic_driver() {
    echo "Download 100G Mellanox NIC driver"
    wget -cO - "https://content.mellanox.com/ofed/MLNX_OFED-5.8-1.0.1.1/${NIC_PACKAGE}.tgz" > /tmp/${NIC_PACKAGE}.tgz
    echo "Untar the NIC package. "
    tar xzvf /tmp/${NIC_PACKAGE}.tgz -C /tmp/
    rm /tmp/${NIC_PACKAGE}.tgz
    sudo /tmp/${NIC_PACKAGE}/mlnxofedinstall -q #--without-fw-update
}

install_xrt() {
    echo "Download XRT installation package"
    wget -cO - "https://www.xilinx.com/bin/public/openDownload?filename=$XRT_PACKAGE" > /tmp/$XRT_PACKAGE
    
    echo "Install XRT"
    if [[ "$OSVERSION" == "ubuntu-16.04" ]] || [[ "$OSVERSION" == "ubuntu-18.04" ]] || [[ "$OSVERSION" == "ubuntu-20.04" ]]; then
        echo "Ubuntu XRT install"
        echo "Installing XRT dependencies..."
        apt update
        echo "Installing XRT package..."
        apt install -y /tmp/$XRT_PACKAGE
    elif [[ "$OSVERSION" == "centos-7" ]] ; then
        echo "CentOS 7 XRT install"
        echo "Installing XRT dependencies..."
        yum install -y epel-release
        echo "Installing XRT package..."
        yum install -y /tmp/$XRT_PACKAGE
    elif [[ "$OSVERSION" == "centos-8" ]]; then
        echo "CentOS 8 XRT install"
        echo "Installing XRT dependencies..."
        #sudo yum remove -y xrt
        yum config-manager --set-enabled powertools
        yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
        yum config-manager --set-enabled appstream
        echo "Installing XRT package..."
        sudo yum install -y /tmp/$XRT_PACKAGE
    fi
    #rm /tmp/$XRT_PACKAGE
}

install_shellpkg() {
if [[ "$SHELL" == 1 ]]; then
    if [[ "$U280" == 0 ]]; then
        echo "[WARNING] No FPGA Board Detected. Skip shell flash."
        exit 1;
    fi
     
    for PF in U280; do
        if [[ "$(($PF))" != 0 ]]; then
            echo "You have $(($PF)) $PF card(s). "
            PLATFORM=`echo "alveo-$PF" | awk '{print tolower($0)}'`
            install_u280_shell
        fi
    done
fi
}

check_shellpkg() {
    if [[ "$OSVERSION" == "ubuntu-16.04" ]] || [[ "$OSVERSION" == "ubuntu-18.04" ]] || [[ "$OSVERSION" == "ubuntu-20.04" ]]; then
        PACKAGE_INSTALL_INFO=`apt list --installed 2>/dev/null | grep "$PACKAGE_NAME" | grep "$PACKAGE_VERSION"`
    elif [[ "$OSVERSION" == "centos-7" ]] || [[ "$OSVERSION" == "centos-8" ]]; then
        PACKAGE_INSTALL_INFO=`yum list installed 2>/dev/null | grep "$PACKAGE_NAME" | grep "$PACKAGE_VERSION"`
    fi
}

check_xrt() {
    if [[ "$OSVERSION" == "ubuntu-16.04" ]] || [[ "$OSVERSION" == "ubuntu-18.04" ]] || [[ "$OSVERSION" == "ubuntu-20.04" ]]; then
        XRT_INSTALL_INFO=`apt list --installed 2>/dev/null | grep "xrt" | grep "$XRT_VERSION"`
    elif [[ "$OSVERSION" == "centos-7" ]] || [[ "$OSVERSION" == "centos-8" ]]; then
        XRT_INSTALL_INFO=`yum list installed 2>/dev/null | grep "xrt" | grep "$XRT_VERSION"`
    fi
}

check_requested_shell() {
    if [[ "$TOOLVERSION" == "2022.1" ]]; then 
        SHELL_INSTALL_INFO=`/opt/xilinx/xrt/bin/xbmgmt examine | grep "$DSA"`
    else
        SHELL_INSTALL_INFO=`/opt/xilinx/xrt/bin/xbmgmt flash --scan | grep "$DSA"`
    fi
}

check_factory_shell() {
    if [[ "$TOOLVERSION" == "2022.1" ]]; then   
        SHELL_INSTALL_INFO=`/opt/xilinx/xrt/bin/xbmgmt examine | grep "$FACTORY_SHELL"`
    else
        SHELL_INSTALL_INFO=`/opt/xilinx/xrt/bin/xbmgmt flash --scan | grep "$FACTORY_SHELL"`
    fi
}

install_u280_shell() {
    check_shellpkg
    if [[ $? != 0 ]]; then
        echo "Download Shell package"
        wget -cO - "https://www.xilinx.com/bin/public/openDownload?filename=$SHELL_PACKAGE" > /tmp/$SHELL_PACKAGE
        if [[ $SHELL_PACKAGE == *.tar.gz ]]; then
            echo "Untar the package. "
            tar xzvf /tmp/$SHELL_PACKAGE -C /tmp/
            rm /tmp/$SHELL_PACKAGE
        fi
        echo "Install Shell"
        if [[ "$OSVERSION" == "ubuntu-16.04" ]] || [[ "$OSVERSION" == "ubuntu-18.04" ]] || [[ "$OSVERSION" == "ubuntu-20.04" ]]; then
            echo "Install Ubuntu shell package"
            apt-get install -y /tmp/xilinx*
        elif [[ "$OSVERSION" == "centos-7" ]] || [[ "$OSVERSION" == "centos-8" ]]; then
            echo "Install CentOS shell package"
            yum install -y /tmp/xilinx*
        fi
        rm /tmp/xilinx*
        #if [[ -f /tmp/$SHELL_PACKAGE ]]; then rm /tmp/$SHELL_PACKAGE; fi
    else
        echo "The package is already installed. "
    fi
}

flash_card() {
    echo "Flash Card(s). "
    if [[ "$TOOLVERSION" == "2022.1" ]]; then
        /opt/xilinx/xrt/bin/xbmgmt program --base --device 0000:3b:00.0
    else
        /opt/xilinx/xrt/bin/xbmgmt flash --update --shell $DSA --force
    fi
}

detect_cards() {
    lspci > /dev/null
    if [ $? != 0 ] ; then
        if [[ "$OSVERSION" == "ubuntu-16.04" ]] || [[ "$OSVERSION" == "ubuntu-18.04" ]] || [[ "$OSVERSION" == "ubuntu-20.04" ]]; then
            apt-get install -y pciutils
        elif [[ "$OSVERSION" == "centos-7" ]] || [[ "$OSVERSION" == "centos-8" ]]; then
            yum install -y pciutils
        fi
    fi

    for DEVICE_ID in $(lspci  -d 10ee: | grep " Processing accelerators" | grep "Xilinx" | grep ".0 " | cut -d" " -f7); do
        if [[ "$DEVICE_ID" == "5008" ]] || [[ "$DEVICE_ID" == "d008" ]] || [[ "$DEVICE_ID" == "500c" ]] || [[ "$DEVICE_ID" == "d00c" ]]; then
            U280=$((U280 + 1))
        fi
    done
}

verify_install() {
    errors=0
    check_xrt
    if [ $? == 0 ] ; then
        echo "XRT installation verified."
    else
        echo "XRT installation could not be verified."
        errors=$((errors+1))
    fi
    check_shellpkg
    if [ $? == 0 ] ; then
        echo "Shell package installation verified."
    else
        echo "Shell package installation could not be verified."
        errors=$((errors+1))
    fi
    return $errors
}
SHELL=1
OSVERSION=`grep '^ID=' /etc/os-release | awk -F= '{print $2}'`
OSVERSION=`echo $OSVERSION | tr -d '"'`
VERSION_ID=`grep '^VERSION_ID=' /etc/os-release | awk -F= '{print $2}'`
VERSION_ID=`echo $VERSION_ID | tr -d '"'`
OSVERSION="$OSVERSION-$VERSION_ID"
TOOLVERSION=$1
SCRIPT_PATH=/local/repository
COMB="${TOOLVERSION}_${OSVERSION}"
XRT_PACKAGE=`grep ^$COMB: $SCRIPT_PATH/spec.txt | awk -F':' '{print $2}' | awk -F';' '{print $1}' | awk -F= '{print $2}'`
SHELL_PACKAGE=`grep ^$COMB: $SCRIPT_PATH/spec.txt | awk -F':' '{print $2}' | awk -F';' '{print $2}' | awk -F= '{print $2}'`
DSA=`grep ^$COMB: $SCRIPT_PATH/spec.txt | awk -F':' '{print $2}' | awk -F';' '{print $3}' | awk -F= '{print $2}'`
PACKAGE_NAME=`grep ^$COMB: $SCRIPT_PATH/spec.txt | awk -F':' '{print $2}' | awk -F';' '{print $5}' | awk -F= '{print $2}'`
PACKAGE_VERSION=`grep ^$COMB: $SCRIPT_PATH/spec.txt | awk -F':' '{print $2}' | awk -F';' '{print $6}' | awk -F= '{print $2}'`
XRT_VERSION=`grep ^$COMB: $SCRIPT_PATH/spec.txt | awk -F':' '{print $2}' | awk -F';' '{print $7}' | awk -F= '{print $2}'`
FACTORY_SHELL="xilinx_u280_GOLDEN_8"

NIC_PACKAGE="MLNX_OFED_LINUX-5.8-1.0.1.1-ubuntu18.04-x86_64"

if [ ! -f ~/boot_flag ]; then
    #install_nic_driver
    detect_cards
    install_xrt
    install_shellpkg
    verify_install
    
    if [ $? == 0 ] ; then
        echo "XRT and shell package installation successful."
        flash_card
    else
        echo "XRT and/or shell package installation failed."
        exit 1
    fi
    
    if check_factory_shell ; then
        echo "Shell is in factory reset state. Cold reboot required."   
        $SCRIPT_PATH/cold-boot-init.sh &
    elif check_requested_shell ; then
        echo "Shell is already up to date. Cold reboot not required."
        touch ~/boot_flag
    else
        echo "FPGA shell could not be verified."
        exit 1
    fi
    echo "Done running startup script."
    exit 0
else
    echo "Rebooted the node."
    #This is only supposed to update the SC since the shell is already updated.
    /opt/xilinx/xrt/bin/xbmgmt flash --update --force
fi
