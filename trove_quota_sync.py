#!/usr/bin/python

import argparse
import sys

from prettytable import PrettyTable

import db
from resources import backups as backups_resource
from resources import instances as instances_resource
from resources import quotas as quotas_resource


RESOURCES = ['instances', 'volumes', 'backups']


def update_quota_usages(meta, usage):

    if usage['in_sync']:
        print("[ERROR] already in sync")
        return

    for key in RESOURCES:
        quota_key = key + '#quota_usage'
        if usage[key] != usage[quota_key]:
            db.update_quota_usages_db(meta, usage['tenant_id'], key,
                                      usage[key])


def display(resources, all_resources=False):

    rows = ['tenant_id'] + RESOURCES + ['status']
    ptable = PrettyTable(rows)
    for tenant_id in resources:
        values = [tenant_id]
        in_sync = True
        for key in RESOURCES:
            quota_key = key + '#quota_usage'
            if resources[tenant_id][key] != resources[tenant_id][quota_key]:
                in_sync = False
                value = str(resources[tenant_id][quota_key]) + ' -> ' + str(
                    resources[tenant_id][key])
            else:
                value = str(resources[tenant_id][key])
            values.append(value)
        if not in_sync:
            values.append('\033[1m\033[91mMismatch\033[0m')
            ptable.add_row(values)
        elif all_resources:
            values.append('\033[1m\033[92mOK\033[0m')
            ptable.add_row(values)
    if ptable._rows:
        print('\n')
        print(ptable)


def analise_user_usage(resources):
    for tenant_id in resources:
        in_sync = True
        for key in RESOURCES:
            quota_key = key + '#quota_usage'
            if key not in resources[tenant_id]:
                resources[tenant_id][key] = 0
            if quota_key not in resources[tenant_id]:
                resources[tenant_id][quota_key] = 0
            if resources[tenant_id][key] != resources[tenant_id][quota_key]:
                in_sync = False
        resources[tenant_id]['in_sync'] = in_sync
    return resources


def sync_resources(meta, resources):
    for tenant_id in resources:
        if not resources[tenant_id]['in_sync']:
            update_quota_usages(meta, resources[tenant_id])


def parse_cmdline_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        action="store_true",
        help="show the state of all quota resources")
    parser.add_argument(
        "--sync",
        action="store_true",
        help=("automatically sync all resources, "
              "PLEASE USE IT WITH EXTREME CAUTION."))
    parser.add_argument(
        "--tenant_id", type=str, help="searches only project ID")
    parser.add_argument(
        "--config",
        default='/etc/trove/trove.conf',
        help='configuration file')
    return parser.parse_args()


def main():
    try:
        args = parse_cmdline_args()
    except Exception as e:
        sys.stdout.write("Wrong command line arguments (%s)" % e.strerror)

    db_url = db.get_db_url(args.config)
    session, meta, base = db.makeConnection(db_url)
    resources = {}
    # get instances usage
    instances_resource.get_resources_usage(resources, meta,
                                           tenant_id=args.tenant_id)
    # get backups usage
    backups_resource.get_resources_usage(resources, meta,
                                         tenant_id=args.tenant_id)
    # get quota usage
    quotas_resource.get_resources_usage(resources, meta,
                                        tenant_id=args.tenant_id)
    analise_user_usage(resources)
    display(resources, all_resources=args.all)
    if args.sync:
        sync_resources(meta, resources)


if __name__ == "__main__":
    main()
