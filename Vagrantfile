Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"

  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
  end

  config.vm.define "db" do |db|
    db.vm.hostname = "db"
    db.vm.network "private_network", ip: "192.168.56.11"

    db.vm.provider "virtualbox" do |vb|
      vb.name = "netflix-db"
      vb.memory = 1024
      vb.cpus = 1
    end

    db.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "infra/ansible/db.yml"
      ansible.install = true
      ansible.verbose = "v"
    end
  end

  config.vm.define "backend" do |backend|
    backend.vm.hostname = "backend"
    backend.vm.network "private_network", ip: "192.168.56.12"

    backend.vm.provider "virtualbox" do |vb|
      vb.name = "netflix-backend"
      vb.memory = 1024
      vb.cpus = 1
    end

    backend.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "infra/ansible/backend.yml"
      ansible.install = true
      ansible.verbose = "v"
    end
  end

  config.vm.define "frontend", primary: true do |frontend|
    frontend.vm.hostname = "frontend"
    frontend.vm.network "private_network", ip: "192.168.56.13"
    frontend.vm.network "forwarded_port",
      guest: 80,
      host: 8080,
      host_ip: "127.0.0.1",
      auto_correct: true

    frontend.vm.provider "virtualbox" do |vb|
      vb.name = "netflix-frontend"
      vb.memory = 1024
      vb.cpus = 1
    end

    frontend.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "infra/ansible/frontend.yml"
      ansible.install = true
      ansible.verbose = "v"
    end
  end
end