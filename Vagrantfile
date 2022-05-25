## -*- mode: ruby -*-
## vi: set ft=ruby :

# Set the box image to use
BOX_IMAGE = "ubuntu/focal64"

# Set the amount of nodes to create with seed node
NETWORK_SIZE = 0

Vagrant.configure("2") do |config|

  # seed node config
  config.vm.define "seed" do |subconfig|
    subconfig.vm.box = BOX_IMAGE
    subconfig.vm.hostname = "seed"
    subconfig.vm.network :private_network, ip: "10.0.0.10"
  end

  # node config
  (1..NETWORK_SIZE).each do |i|
    config.vm.define "node#{i}" do |subconfig|
      subconfig.vm.box = BOX_IMAGE
      subconfig.vm.hostname = "node#{i}"
      subconfig.vm.network :private_network, ip: "10.0.0.#{10 + i * 10}"
    end
  end

  # vm settings
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 1
  end

  # Enable provisioning with a shell script for all machines
  # path is relative to project directory (where Vagrantfile is)
  config.vm.provision "shell", path: "provision.sh"
end