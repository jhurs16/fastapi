# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

class BaseConfig(object):

    # Can be set to 'MasterUser' or 'ServicePrincipal'
    AUTHENTICATION_MODE = 'ServicePrincipal'

    # Workspace Id in which the report is present
    WORKSPACE_ID = 'fe8f95d8-3df5-4bb9-8057-fbde79234a6d'
    
    # Report Id for which Embed token needs to be generated
    REPORT_ID = '7f9989e4-0183-47d2-94e1-1c99191aeca6'
    
    # Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
    TENANT_ID = '051bd2dd-ddc9-4d76-98af-b47d4277d0fc'
    
    # Client Id (Application Id) of the AAD app
    CLIENT_ID = 'db8efc0b-f0d8-4bca-a75d-3d340ed1ac44'
    
    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    CLIENT_SECRET = 'Whf8Q~NOIx2lluod1n3MmL3u8vf2M4xxk_MnMbnb'
    
    # Scope Base of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    SCOPE_BASE = ['https://analysis.windows.net/powerbi/api/.default']
    
    # URL used for initiating authorization request
    AUTHORITY_URL = 'https://login.microsoftonline.com/organizations'
    
    # Master user email address. Required only for MasterUser authentication mode.
    POWER_BI_USER = 'deployment@syntivis.eu'
    
    # Master user email password. Required only for MasterUser authentication mode.
    POWER_BI_PASS = 'qls6bsdf876r32!143reAJ#iB6lbCGgchVN19'