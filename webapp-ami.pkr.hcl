packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0, <2.0.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "AWS_REGION" {
  type = string
}

variable "ec2_instance_type" {
  type    = string
  default = "t2.micro"
}

// Ubuntu Canonical account ID
variable "source_ami_owner_id" {
  type    = string
  default = "099720109477"
}

variable "DEV_DEFAUTLT_VPC_ID" {
  type = string
}

variable "AWS_DEMO_ACCOUNT_ID" {
  type = string
}

source "amazon-ebs" "ubuntu" {
  ami_name        = "csye6225_webapp_ubuntu_24_04_${formatdate("YYYY_MM_DD", timestamp())}"
  ami_description = "Custom Ubuntu 24.04 AMI for Webapp Assignment04"
  ami_users       = [var.AWS_DEMO_ACCOUNT_ID]
  instance_type   = var.ec2_instance_type
  region          = var.AWS_REGION

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-noble-24.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = [var.source_ami_owner_id]
  }
  ssh_username = "ubuntu"
  vpc_id       = var.DEV_DEFAUTLT_VPC_ID
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
