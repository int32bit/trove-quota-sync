from sqlalchemy import select
from sqlalchemy import Table


def get_resources_usage(resources, meta, tenant_id=None):
    quota_usages = Table('quota_usages', meta, autoload=True)
    if tenant_id:
        resource_quota_usage = select(
            columns=[
                quota_usages.c.tenant_id, quota_usages.c.resource,
                quota_usages.c.in_use
            ],
            whereclause=quota_usages.c.tenant_id == tenant_id)
    else:
        resource_quota_usage = select(
            columns=[
                quota_usages.c.tenant_id, quota_usages.c.resource,
                quota_usages.c.in_use
            ])
    for (tenant_id, resource, in_use) in resource_quota_usage.execute():
        if tenant_id not in resources:
            resources[tenant_id] = {}
            resources[tenant_id]['tenant_id'] = tenant_id
        resources[tenant_id][resource + '#quota_usage'] = in_use
    return resources
