# -*- coding: utf-8 -*-
import os, sys, MySQLdb, traceback
import ConfigParser
from DBUtils.PooledDB import PooledDB

cf = ConfigParser.ConfigParser()
cf.read("app01/utils/account.ini")
db_host = cf.get("db", "host")
db_user = cf.get("db", "user")
db_password = cf.get("db", "password")
database = cf.get("db", "database")
CA_file = cf.get("db", "CA_file")


# db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=database, ssl={'ssl':{'ca':CA_file}})

# pool = PooledDB(MySQLdb,3,host=db_host, user=db_user, passwd=db_password, db=database, ssl={'ssl': {'ca': CA_file}})

# db = pool.connection()

# cursor = db.cursor()

def use_cursor(sql, param):
    db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=database, ssl={'ssl': {'ca': CA_file}})
    cursor = db.cursor()
    number = cursor.execute(sql, param)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return number, result


def get_unique_values(string):
    if string == None:
        return None
    else:
        str_list = string.split(",")
        new_str_list = []
        for each in str_list:
            if each not in new_str_list:
                new_str_list.append(each)
        return new_str_list


def search_model(modelname):
    sql = "select bug_id, portal_id , case_number, (select description from vendors where id = vendor_id) as vendor,(select name from makes where id=make_id) as make, (select name from models where id=model_id) as model,(select name from hive_products where hive_products.id=cert_records.product_pns_id) as product,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version, (select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform, cert_status from cert_records where model_id in (select id from models where name regexp %s)"
    param = (modelname,)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_make(makename):
    sql = "select bug_id, portal_id , case_number, (select description from vendors where id = vendor_id) as vendor,(select name from makes where id=make_id) as make, (select name from models where id=model_id) as model, (select name from hive_products where hive_products.id=cert_records.product_pns_id) as product,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version,(select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform,cert_status from cert_records where make_id in (select id from makes where name regexp %s)"
    param = (makename,)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_component(device):
    sql = "select distinct cert_records.portal_id as cert,cert_records.case_number, (select description from vendors where id=cert_records.vendor_id) as vendor,(select name from makes where id=cert_records.make_id) as make,(select name from models where id=cert_records.model_id) as model,testplan_desc.description as testplan,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version,(select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform,cert_records.cert_status from cert_records join testplan_desc where testplan_desc.description regexp %s and cert_records.id=testplan_desc.cert_id and (required_64bits =1 or required_32bits =1) union select distinct cert_records.portal_id as cert,cert_records.case_number, (select description from vendors where id=cert_records.vendor_id) as vendor,(select name from makes where id=cert_records.make_id) as make, (select name from models where id=cert_records.model_id) as model,hardware_components.description as testplan,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version,(select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform,cert_records.cert_status from hardware_components join testplan_desc join cert_records where hardware_components.description regexp %s and testplan_desc.component_id=hardware_components.id and cert_records.id=testplan_desc.cert_id and (required_64bits =1 or required_32bits =1) order by cert"
    param = (device, device)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_product(productname):
    sql = "select cert_records.portal_id,cert_records.case_number,(select description from vendors where id=cert_records.vendor_id) as vendor,vendor_product.name as product_name,vendor_product_version as plugin_version,(select name from hive_products where hive_products.id=cert_records.product_pns_id) as product,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version,cert_records.cert_status as cert_status from cert_records join vendor_product where cert_records.vendor_product=vendor_product.id and (vendor_product.name regexp %s or cert_records.vendor_product_version regexp %s) and cert_status not regexp 'Withdrawn'"
    param = (productname, productname)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_kbase(keyword):
    sql = "select distinct bug_kbase_map.kbase_id as kbase, bug_kbase_map.kbase_type_id as kbase_type, kbase_summary_cache.title as subject,group_concat((select distinct case_number from cert_records where cert_records.id=bug_kbase_map.cert_id)) as certs from bug_kbase_map join kbase_summary_cache where kbase_summary_cache.kbase_id = bug_kbase_map.kbase_id and kbase_summary_cache.title regexp %s group by kbase"
    param = (keyword,)
    number, result = use_cursor(sql, param)
    result = [[x[0], x[1], x[2], get_unique_values(x[3])] for x in result]
    return (result, number)


def search_cert_created_by_account(sso_account):
    sql = "select bug_id, portal_id , case_number, owner_mail, owner_name, (select name from hive_products where hive_products.id=cert_records.product_pns_id) as product,cert_status from cert_records where (owner_mail regexp %s) or (owner_name regexp %s)"
    param = (sso_account, sso_account)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_cert_created_by_vendor(vendor):
    sql = "select bug_id, portal_id , case_number, (select description from vendors where id=vendor_id) as vendor, (select name from hive_products where hive_products.id=cert_records.product_pns_id) as product ,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version, (select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform, (select name from cert_type where id=cert_type) as cert_type, cert_status from cert_records where vendor_id in (select id from vendors where description regexp %s)"
    param = (vendor,)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_TAM_ack_certs(tam):
    sql = "select distinct cert_records.portal_id,cert_records.case_number, (select description from vendors where id=cert_records.vendor_id) as vendor,(select name from makes where id=cert_records.make_id) as make,(select name from models where id=cert_records.model_id) as model,(select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version,(select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform, (select name from cert_type where id=cert_type) as cert_type, vendors.ptams from cert_records join vendors where cert_records.vendor_id=vendors.id and cert_records.cert_status regexp 'Certified' and cert_records.tam_status regexp 'Requested' and vendors.ptams regexp %s"
    param = (tam,)
    number, result = use_cursor(sql, param)
    return (result, number)


def search_TAM_by_vendor(vendor):
    sql = "select description, ptams from vendors where type=0 and description regexp %s"
    param = (vendor,)
    number, result = use_cursor(sql, param)
    return (result, number)

def search_case_number(portal_id):
    sql = "select case_number, portal_id from cert_records where portal_id regexp %s"
    param = (portal_id,)
    number, result = use_cursor(sql, param)
    return (result, number)

# cursor.close()
# db.close()
