# -*- mode: ruby -*-
# vi: set ft=ruby :


# This Vagrant configuration sets up Ubuntu 16.04 LTS (Xenial) with Drop
# installed.
#
# The password for user ubuntu will be set to "drop".
#

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = true
  
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
  end

  config.vm.provision "shell", inline: <<-SHELL
    set -e
    apt-get update
    apt-get -y install lightdm i3 xfce4 terminator
  SHELL

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    /vagrant/install-on-ubuntu.sh
  SHELL

  config.vm.provision "shell", inline: <<-SHELL
    set -e
    echo -en "drop\ndrop\n" | passwd ubuntu
    systemctl restart lightdm
  SHELL
end
