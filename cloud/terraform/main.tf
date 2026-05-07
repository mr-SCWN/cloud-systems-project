resource "google_compute_network" "netflix_vpc" {
  name                    = "netflix-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "netflix_subnet" {
  name          = "netflix-subnet"
  ip_cidr_range = "10.10.0.0/24"
  region        = var.region
  network       = google_compute_network.netflix_vpc.id
}

resource "google_compute_firewall" "allow_ssh_http" {
  name    = "netflix-allow-ssh-http"
  network = google_compute_network.netflix_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["netflix-app"]
}

resource "google_compute_instance" "netflix_vm" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone
  tags         = ["netflix-app"]

  boot_disk {
    initialize_params {
      image = "projects/ubuntu-os-cloud/global/images/family/ubuntu-minimal-2204-lts"
      size  = 20
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.netflix_subnet.id

    access_config {
    }
  }

  metadata = {
    ssh-keys = "${var.gcp_user}:${file("${path.module}/../ansible/gcp_vm_key.pub")}"
  }
}