"""TODO: module docstring."""
from marmoset import config as config_reader
from marmoset import validation
from .isc_dhcp_ldap_config import ISCDhcpLdapConfig


CONFIG = config_reader.load_config()


class DhcpConfig:
    """Model for a DHCP object."""

    def __init__(self, mac, ip_address, gateway=None, networkmask=None):
        """Initialize all attributes with default values."""
        self.additional_statements = {}

        self.mac = None
        self.ip_address = None
        self.gateway = None
        self.networkmask = None
        self.dhcp_hostname = None

        self.set_settings(True, mac, ip_address, gateway, networkmask)

    def set_settings(
            self,
            allow_none_value_for_not_required_parameter=False,
            mac=None,
            ip_address=None,
            gateway=None,
            networkmask=None):
        """TODO: docstring."""
        # pylint: disable-msg=too-many-arguments
        self.mac = mac

        if gateway is not None or allow_none_value_for_not_required_parameter:
            self.gateway = gateway

        if networkmask is not None \
                or allow_none_value_for_not_required_parameter:
            self.networkmask = networkmask

        if validation.is_cidr(ip_address):
            self.ip_address = validation.get_ip_from_cidr(ip_address)

            if self.networkmask is None:
                self.networkmask = validation.get_nm_from_cidr(ip_address)

            if self.gateway is None and CONFIG[
                    'DHCPConfig'].getboolean('force_gateway'):
                self.gateway = validation.get_gw_from_cidr(ip_address)
        else:
            self.ip_address = ip_address

        self.dhcp_hostname = CONFIG['Common'].get('FQDN')

    def add_additional_statement(self, key, value):
        """TODO: docstring."""
        self.additional_statements[key] = value

    def create_isc_ldap(self):
        """TODO: docstring."""
        isc_dhcp_config = ISCDhcpLdapConfig(self)
        isc_dhcp_config.save()

    def remove_by_ipv4(self):
        """TODO: docstring."""
        return ISCDhcpLdapConfig.remove_by_ipv4(self.ip_address) > 0

    def remove_by_mac(self):
        """TODO: docstring."""
        return ISCDhcpLdapConfig.remove_by_mac(self.mac) > 0

    def remove_all(self):
        """TODO: docstring."""
        ipv4_removed_count = ISCDhcpLdapConfig.remove_by_ipv4(self.ip_address)
        mac_removed_count = ISCDhcpLdapConfig.remove_by_mac(self.mac)

        return (ipv4_removed_count + mac_removed_count) > 0

    @staticmethod
    def all():
        """TODO: docstring."""
        return ISCDhcpLdapConfig.get_all_db_entries()

    @staticmethod
    def get_by_ip(ip_address):
        """TODO: docstring."""
        return ISCDhcpLdapConfig.get_by_ip(ip_address)

    @staticmethod
    def get_by_mac(mac):
        """TODO: docstring."""
        return ISCDhcpLdapConfig.get_by_mac(mac)

    @staticmethod
    def exists_ipv4(ip_address):
        """TODO: docstring."""
        return ISCDhcpLdapConfig.get_by_ip(ip_address) is not None

    @staticmethod
    def exists_mac(mac_address):
        """TODO: docstring."""
        return ISCDhcpLdapConfig.get_by_mac(mac_address) is not None
