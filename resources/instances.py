from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import Table


def get_resources_usage(resources, meta, tenant_id=None):
    instances = Table('instances', meta, autoload=True)
    if tenant_id:
        resources_usage = select(
            columns=[
                instances.c.tenant_id,
                func.count(instances.c.id),
                func.ifnull(func.sum(instances.c.volume_size), 0),
            ],
            whereclause=and_(instances.c.deleted == 0,
                             instances.c.tenant_id == tenant_id),
            group_by=[instances.c.tenant_id])
    else:
        resources_usage = select(
            columns=[
                instances.c.tenant_id,
                func.count(instances.c.id),
                func.ifnull(func.sum(instances.c.volume_size), 0),
            ],
            whereclause=and_(instances.c.deleted == 0),
            group_by=[instances.c.tenant_id])
    for (tenant_id, instances, volumes) in resources_usage.execute():
        if tenant_id not in resources:
            resources[tenant_id] = {}
            resources[tenant_id]['tenant_id'] = tenant_id
        resources[tenant_id]['instances'] = int(instances)
        resources[tenant_id]['volumes'] = int(volumes)
    return resources
