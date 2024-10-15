packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0, <2.0.0"
      source  = "github.com/hashicorp/amazon"
    }
   }
 }

source "amazon-ebs" "ubuntu" {
  ami_name        = "csye6225_webapp_ubuntu_24_04_${formatdate("YYYY_MM_DD", timestamp())}"
  ami_description = "Custom Ubuntu 24.04 AMI for Webapp Assignment04"

  instance_type = "t2.micro"
  region        = "us-east-1"
  profile       = "dev-neu"

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-noble-24.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"] // Ubuntu Canonical account ID
  }
  ssh_username = "ubuntu"
  vpc_id       = "vpc-07108049450771ba0"
}

build {
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "shell" {
    script = "scripts/app_update_os.sh"
  }

  provisioner "shell" {
    script = "scripts/app_directory.sh"
  }

  provisioner "file" {
    source      = "app"
    destination = "/tmp/app"
  }

  provisioner "file" {
    source      = ".env"
    destination = "/tmp/.env"
  }

  provisioner "file" {
    source      = "requirements.txt"
    destination = "/tmp/requirements.txt"
  }

  provisioner "file" {
    source      = "webapp-systemd.service"
    destination = "/tmp/webapp-systemd.service"
  }

  provisioner "shell" {
    script = "scripts/app_setup.sh"
  }
}
