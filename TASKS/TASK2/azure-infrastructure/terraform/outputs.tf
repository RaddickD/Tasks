output "lb_public_ip" {
  value = azurerm_public_ip.lb_public_ip.ip_address
}

output "vm_names" {
  value = azurerm_linux_virtual_machine.vm[*].name
}

output "db_fqdn" {
  value = azurerm_postgresql_flexible_server.db.fqdn
}
