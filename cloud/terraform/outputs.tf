output "vm_name" {
  value = google_compute_instance.netflix_vm.name
}

output "external_ip" {
  value = google_compute_instance.netflix_vm.network_interface[0].access_config[0].nat_ip
}

output "ssh_command_wsl" {
  value = "ssh -i /mnt/c/vagrant/cloud-systems-project/cloud/ansible/gcp_vm_key ${var.gcp_user}@${google_compute_instance.netflix_vm.network_interface[0].access_config[0].nat_ip}"
}