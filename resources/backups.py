from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import Table


def get_resources_usage(resources, meta, tenant_id=None):
    backups = Table('backups', meta, autoload=True)
    if tenant_id:
        resources_usage = select(
            columns=[
                backups.c.tenant_id,
                func.count(backups.c.id),
            ],
            whereclause=and_(backups.c.deleted == 0,
                             backups.c.tenant_id == tenant_id),
            group_by=[backups.c.tenant_id])
    else:
        resources_usage = select(
            columns=[
                backups.c.tenant_id,
                func.count(backups.c.id),
            ],
            whereclause=and_(backups.c.deleted == 0),
            group_by=[backups.c.tenant_id])
    for (tenant_id, backups) in resources_usage.execute():
        if tenant_id not in resources:
            resources[tenant_id] = {}
            resources[tenant_id]['tenant_id'] = tenant_id
        resources[tenant_id]['backups'] = int(backups)
    return resources
