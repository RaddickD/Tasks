variable "location" {
  default = "East US"
}

variable "prefix" {
  default = "demo"
}

variable "admin_username" {
  default = "azureuser"
}

variable "admin_password" {
  description = "Admin password for VMs"
  type        = string
}

variable "db_username" {
  default = "pgadmin"
}

variable "db_password" {
  description = "Password for Postgres DB"
  type        = string
}
