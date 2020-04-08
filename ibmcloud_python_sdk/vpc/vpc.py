import json

from ibmcloud_python_sdk.config import params
from ibmcloud_python_sdk.auth import get_headers as headers
from ibmcloud_python_sdk.utils.common import query_wrapper as qw
from ibmcloud_python_sdk.utils.common import resource_not_found
from ibmcloud_python_sdk.utils.common import resource_deleted
from ibmcloud_python_sdk import resource_group


class Vpc():

    def __init__(self):
        self.cfg = params()
        self.rg = resource_group.Resource()

    def get_vpcs(self):
        """
        Retrieve VPC list
        """
        try:
            # Connect to api endpoint for vpcs
            path = ("/v1/vpcs?version={}&generation={}".format(
                self.cfg["version"], self.cfg["generation"]))

            # Return data
            return qw("iaas", "GET", path, headers())["data"]

        except Exception as error:
            print("Error fetching VPC. {}".format(error))
            raise

    def get_vpc(self, vpc):
        """
        Retrieve specific VPC by name or by ID
        :param vpc: VPC name or ID
        """
        by_name = self.get_vpc_by_name(vpc)
        if "errors" in by_name:
            for key_name in by_name["errors"]:
                if key_name["code"] == "not_found":
                    by_id = self.get_vpc_by_id(vpc)
                    if "errors" in by_id:
                        return by_id
                    return by_id
                else:
                    return by_name
        else:
            return by_name

    def get_vpc_by_id(self, id):
        """
        Retrieve specific VPC by ID
        :param id: VPC ID
        """
        try:
            # Connect to api endpoint for vpcs
            path = ("/v1/vpcs/{}?version={}&generation={}".format(
                id, self.cfg["version"], self.cfg["generation"]))

            # Return data
            return qw("iaas", "GET", path, headers())["data"]

        except Exception as error:
            print("Error fetching VPC with ID {}. {}".format(id, error))
            raise

    def get_vpc_by_name(self, name):
        """
        Retrieve specific VPC by name
        :param name: VPC name
        """
        try:
            # Retrieve VPCs
            data = self.get_vpcs()
            if "errors" in data:
                return data

            # Loop over VPCs until filter match
            for vpc in data['vpcs']:
                if vpc["name"] == name:
                    # Return data
                    return vpc

            # Return error if no VPC is found
            return resource_not_found()

        except Exception as error:
            print("Error fetching VPC with name {}. {}".format(name, error))
            raise

    def get_default_network_acl(self, vpc):
        """
        Retrieve VPC's default network ACL
        :param vpc: VPC name or ID
        """
        # Check if VPC exists and get information
        vpc_info = self.get_vpc(vpc)
        if "errors" in vpc_info:
            return vpc_info

        try:
            # Connect to api endpoint for vpcs
            path = ("/v1/vpcs/{}/default_network_acl?version={}"
                    "&generation={}".format(vpc_info["id"],
                                            self.cfg["version"],
                                            self.cfg["generation"]))

            # Return data
            return qw("iaas", "GET", path, headers())["data"]

        except Exception as error:
            print("Error fetching default network ACL for VPC"
                  " {}. {}".format(vpc, error))
            raise

    def get_default_security_group(self, vpc):
        """
        Retrieve VPC's default security group
        :param vpc: VPC name or ID
        """
        # Check if VPC exists and get information
        vpc_info = self.get_vpc(vpc)
        if "errors" in vpc_info:
            return vpc_info

        try:
            # Connect to api endpoint for vpcs
            path = ("/v1/vpcs/{}/default_security_group?version={}"
                    "&generation={}".format(vpc_info["id"],
                                            self.cfg["version"],
                                            self.cfg["generation"]))

            # Return data
            return qw("iaas", "GET", path, headers())["data"]

        except Exception as error:
            print("Error fetching default security group for VPC"
                  " {}. {}".format(vpc, error))
            raise

    def create_vpc(self, **kwargs):
        """
        Create VPC (Virtual Private Cloud)
        :param name: Optional. The unique user-defined name for this VPC.

        :param resource_group: Optional. The resource group to use.

        :param address_prefix_management: Optional. Indicates whether a
        default address prefix should be automatically created for
        each zone in this VPC.

        :param classic_access: Optional. Indicates whether this VPC should
        be connected to Classic Infrastructure.
        """
        # Build dict of argument and assign default value when needed
        args = {
            'name': kwargs.get('name'),
            'resource_group': kwargs.get('resource_group'),
            'address_prefix_management': kwargs.get(
                'address_prefix_management', 'auto'),
            'classic_access': kwargs.get('classic_access', False),
        }

        # Construct payload
        payload = {}
        for key, value in args.items():
            if value is not None:
                if key == "resource_group":
                    rg_info = self.rg.get_resource_group(
                        args["resource_group"])
                    if "errors" in rg_info:
                        return rg_info
                    payload["resource_group"] = {"id": rg_info["id"]}
                else:
                    payload[key] = value

        try:
            # Connect to api endpoint for vpcs
            path = ("/v1/vpcs?version={}&generation={}".format(
                self.cfg["version"], self.cfg["generation"]))

            # Return data
            return qw("iaas", "POST", path, headers(),
                      json.dumps(payload))["data"]

        except Exception as error:
            print("Error creating VPC. {}".format(error))
            raise

    def delete_vpc(self, vpc):
        """
        Delete VPC
        :param vpc: VPC name or ID
        """
        # Check if VPC exists and get information
        vpc_info = self.get_vpc(vpc)
        if "errors" in vpc_info:
            return vpc_info

        try:
            # Connect to api endpoint for vpcs
            path = ("/v1/vpcs/{}?version={}&generation={}".format(
                vpc_info["id"], self.cfg["version"], self.cfg["generation"]))

            data = qw("iaas", "DELETE", path, headers())

            # Return data
            if data["response"].status != 204:
                return data["data"]

            # Return status
            return resource_deleted()

        except Exception as error:
            print("Error deleting VPC {}. {}".format(vpc, error))
            raise
