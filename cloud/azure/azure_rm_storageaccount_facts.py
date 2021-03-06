##!/usr/bin/python
#
# Copyright (c) 2016 Matt Davis, <mdavis@ansible.com>
#                    Chris Houseknecht, <house@redhat.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: azure_rm_storageaccount_facts

version_added: "2.1"

short_description: Get storage account facts.

description:
    - Get facts for one storage account or all storage accounts within a resource group.

options:
    name:
        description:
            - Only show results for a specific account.
        required: false
        default: null
    resource_group:
        description:
            - Limit results to a resource group. Required when filtering by name.
        required: false
        default: null
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.
        required: false
        default: null

extends_documentation_fragment:
    - azure

author:
    - "Chris Houseknecht (@chouseknecht)"
    - "Matt Davis (@nitzmahone)"

'''

EXAMPLES = '''
    - name: Get facts for one account
      azure_rm_storageaccount_facts:
        resource_group: Testing
        name: clh0002

    - name: Get facts for all accounts in a resource group
      azure_rm_storageaccount_facts:
        resource_group: Testing

    - name: Get facts for all accounts by tags
      azure_rm_storageaccount_facts:
        tags:
          - testing
          - foo:bar
'''

RETURN = '''
changed:
    description: Whether or not the object was changed.
    returned: always
    type: bool
    sample: False
objects:
    description: List containing a set of facts for each selected object.
    returned: always
    type: list
    sample: [{
        "id": "/subscriptions/XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX/resourceGroups/testing/providers/Microsoft.Storage/storageAccounts/testaccount001",
        "location": "eastus2",
        "name": "testaccount001",
        "properties": {
            "accountType": "Standard_LRS",
            "creationTime": "2016-03-28T02:46:58.290113Z",
            "primaryEndpoints": {
                "blob": "https://testaccount001.blob.core.windows.net/",
                "file": "https://testaccount001.file.core.windows.net/",
                "queue": "https://testaccount001.queue.core.windows.net/",
                "table": "https://testaccount001.table.core.windows.net/"
            },
            "primaryLocation": "eastus2",
            "provisioningState": "Succeeded",
            "statusOfPrimary": "Available"
        },
        "tags": {},
        "type": "Microsoft.Storage/storageAccounts"
    }]
'''

AZURE_OBJECT_CLASS = 'StorageAccount'


from ansible.module_utils.basic import *
from ansible.module_utils.azure_rm_common import *

try:
    from msrestazure.azure_exceptions import CloudError
    from azure.common import AzureMissingResourceHttpError, AzureHttpError
except:
    # This is handled in azure_rm_common
    pass


class AzureRMStorageAccountFacts(AzureRMModuleBase):
    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str'),
            resource_group=dict(type='str'),
            tags=dict(type='list'),
        )

        self.results = dict(
            changed=False,
            objects=[]
        )

        self.name = None
        self.resource_group = None
        self.tags = None

        super(AzureRMStorageAccountFacts, self).__init__(self.module_arg_spec,
                                                         supports_tags=False,
                                                         facts_module=True)

    def exec_module(self, **kwargs):

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.name and not self.resource_group:
            self.fail("Parameter error: resource group required when filtering by name.")

        if self.name:
            self.results['objects'] = self.get_account()
        elif self.resource_group:
            self.results['objects'] = self.list_resource_group()
        else:
            self.results['objects'] = self.list_all()

        return self.results

    def get_account(self):
        self.log('Get properties for account {0}'.format(self.name))
        account = None
        result = []

        try:
            account = self.storage_client.storage_accounts.get_properties(self.resource_group, self.name)
        except CloudError:
            pass

        if account and self.has_tags(account.tags, self.tags):
            result = [self.serialize_obj(account, AZURE_OBJECT_CLASS)]

        return result

    def list_resource_group(self):
        self.log('List items')
        try:
            response = self.storage_client.storage_accounts.list_by_resource_group(self.resource_group)
        except Exception as exc:
            self.fail("Error listing for resource group {0} - {1}".format(self.resource_group, str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                results.append(self.serialize_obj(item, AZURE_OBJECT_CLASS))
        return results

    def list_all(self):
        self.log('List all items')
        try:
            response = self.storage_client.storage_accounts.list_by_resource_group(self.resource_group)
        except Exception as exc:
            self.fail("Error listing all items - {0}".format(str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                results.append(self.serialize_obj(item, AZURE_OBJECT_CLASS))
        return results


def main():
    AzureRMStorageAccountFacts()

if __name__ == '__main__':
    main()
