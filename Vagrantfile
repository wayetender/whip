# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  config.vm.box = "ubuntu/trusty64"

  config.vm.provider "virtualbox" do |v|
     v.memory = 1024
     v.cpus = 2
  end

  config.vm.provider "vmware_fusion" do |v|
     v.vmx["memsize"] = "1024"
     v.vmx["numvcpus"] = "2"
  end
  config.vm.network "private_network", ip: "192.168.34.11"

  config.vm.synced_folder ".", "/vagrant", disabled: false

  config.vm.provision "shell", inline: <<-SHELL
     sudo apt-get update
     sudo apt-get install -y python git python-pip libsasl2-dev libxml2-dev libxslt1-dev python-dev libldap2-dev libssl-dev
     sudo pip install virtualenv
     sudo apt-get install -y libboost-dev libboost-test-dev libboost-program-options-dev libboost-system-dev libboost-filesystem-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev
     cd /tmp 
     curl http://archive.apache.org/dist/thrift/0.9.2/thrift-0.9.2.tar.gz | tar zx 
     cd thrift-0.9.2/ 
     ./configure 
     make
     sudo make install
  SHELL
end
