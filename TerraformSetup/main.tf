provider "google" {
  project = "csb-2023"
  region = "europe-west3"
  zone = "europe-west3-c"
}

### NETWORK
resource "google_compute_network" "vpc_network" {
  name = "rabbitmq-network"
  auto_create_subnetworks = true
}

### FIREWALL
resource "google_compute_firewall" "all" {
  name = "allow-all"
  allow {
    protocol = "tcp"
    ports = ["0-65535"]
  }
  network = google_compute_network.vpc_network.id
  source_ranges = ["0.0.0.0/0"]
  ###target_tags = ["http-server","https-server"]
}

### Nodes
resource "google_compute_instance" "node" {
  count        = 2
  name         = "node${count.index + 1}"
  machine_type = "e2-standard-2"

  boot_disk {
    initialize_params {
	  size = 40
      image = "ubuntu-2204-jammy-v20231030"
    }
  }
  metadata_startup_script = file("startup_SlaveNode.sh")




  network_interface {
    network = google_compute_network.vpc_network.id
    access_config {
      # Include this section to give the VM an external IP address
    }
  }
}

### Nodes
resource "google_compute_instance" "node0" {
  name         = "node0"
  machine_type = "e2-standard-2"

  boot_disk {
    initialize_params {
	  size = 40
      image = "ubuntu-2204-jammy-v20231030"
    }
  }
  metadata_startup_script = file("startup_MasterNode.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
    access_config {
      # Include this section to give the VM an external IP address
    }
  }
}

resource "google_compute_instance" "loadbalancer" {
  name         = "loadbalancer"
  machine_type = "e2-standard-2"

  boot_disk {
    initialize_params {
	  size = 40
      image = "ubuntu-2204-jammy-v20231030"
    }
  }
  metadata_startup_script = file("startup_LoadBalancer.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
    access_config {
      # Include this section to give the VM an external IP address
    }
  }
}


### Client
resource "google_compute_instance" "client" {
  name         = "client"
  machine_type = "e2-highcpu-16"

  boot_disk {
    initialize_params {
      image = "ubuntu-2204-jammy-v20231030"
	  size = 40
    }
  }
  metadata_startup_script = file("startup_client.sh")


  network_interface {
    network = google_compute_network.vpc_network.id
    access_config {
      # Include this section to give the VM an external IP address
    }
  }

   service_account {
    email  = "email" # Create service account and add email otherwise the fileupload won't work
    scopes = ["cloud-platform"]
  }
}

