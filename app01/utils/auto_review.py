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

# use PooledDB to connect mysql DB
# pool = PooledDB(MySQLdb,3,host=db_host, user=db_user, passwd=db_password, db=database, ssl={'ssl': {'ca': CA_file}})

# db = pool.connection()

# cursor = db.cursor()


class Leverage_Reivew(object):

    def __init__(self, case_number):
        self.case_number = case_number
        self.sql_cert = "select (select case_number from cert_records where id=cert_id) as cert_id, component_id,(select description from hardware_components where id=component_id) as component,description, result_64bits,(select case_number from cert_records where cert_records.id = leverage_comp_64bits) as component_cert,testplan_desc.name from testplan_desc where cert_id=(select id from cert_records where case_number = %s) and bits64 = 0 and required_64bits = 1 and (result_64bits is not NULL or leverage_comp_64bits is not NULL)"
        self.sql_test_id = "select (select case_number from cert_records where id=cert_id) as cert_id,component_id,(select description from hardware_components where id=component_id) as component,description,(select test_type from cert_tests where id=result_64bits) as class, testplan_desc.bits64 as confirmed, (select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version, (select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform from testplan_desc join cert_records where cert_records.id=testplan_desc.cert_id and cert_id = (select distinct cert_tests.cert_id from cert_tests join testplan_desc where testplan_desc.result_64bits=cert_tests.id and testplan_desc.result_64bits = %s) and testplan_desc.result_64bits = %s"
        self.sql_component_id = "select (select case_number from cert_records where id=testplan_desc.cert_id) as cert_id,testplan_desc.component_id,(select description from hardware_components where hardware_components.id=testplan_desc.component_id) as component,testplan_desc.description,(select test_type from cert_tests where id=testplan_desc.result_64bits) as class, (select name from hive_versions where hive_versions.id=cert_records.version_pns_id) as version, (select name from hive_platforms where hive_platforms.id = cert_records.platform_pns_id) as platform from testplan_desc join cert_records where cert_records.id=testplan_desc.cert_id and testplan_desc.cert_id = (select id from cert_records where case_number=%s) and cert_records.cert_status regexp 'Certified'"
        self.db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=database,
                                  ssl={'ssl': {'ca': CA_file}})
        self.cursor = self.db.cursor()

    def search_unconfirmed_testplan(self, cert_id):
        param = (cert_id,)
        number = self.cursor.execute(self.sql_cert, param)
        result = self.cursor.fetchall()
        return result

    def search_leverage_by_testid(self, test_id):
        param = (test_id, test_id)
        number = self.cursor.execute(self.sql_test_id, param)
        result = self.cursor.fetchall()
        return result

    def search_leverage_by_componentid(self, component_id):
        param = (component_id,)
        number = self.cursor.execute(self.sql_component_id, param)
        result = self.cursor.fetchall()
        return result

    def generate_lev_result(self):
        summary_list = []
        missing_com_id = []
        missing_test_id = []
        try:
            unconfirmed_testplan = self.search_unconfirmed_testplan(self.case_number)
            for each in unconfirmed_testplan:
                test_id = each[4]
                component_id = each[5]
                test_class = each[6]
                if test_id:
                    if each[3] != None:
                        original_device = "%s (%s)" % (each[2], each[3])
                    else:
                        original_device = each[2]
                    leverage_device = []
                    hardware_info = ""
                    leverage_cert_id = 0
                    confirmed = 1
                    rhel_version = "unknown"
                    platform = "unknown"
                    result_by_test_id = self.search_leverage_by_testid(test_id)
                    for each_device in result_by_test_id:
                        if each_device[3] != None:
                            hardware_info = [each_device[2], each_device[3], each_device[4]]
                        else:
                            hardware_info = [each_device[2], each_device[4]]
                        leverage_device.append(hardware_info)
                        leverage_cert_id = each_device[0]
                        rhel_version = each_device[6]
                        platform = each_device[7]
                        if int(each_device[5]) == 0:
                            confirmed = 0
                    if int(leverage_cert_id) != int(self.case_number) and confirmed == 0:
                        if test_id not in missing_test_id:
                            missing_test_id.append(test_id)
                    each_result = [test_id, original_device, test_class, leverage_device, rhel_version, platform]
                    if int(leverage_cert_id) != int(self.case_number):
                        summary_list.append(each_result)
                if component_id:
                    if each[3] != None:
                        original_device = "%s (%s)" % (each[2], each[3])
                    else:
                        original_device = each[2]
                    leverage_device = []
                    hardware_info = ""
                    leverage_cert_id = 0
                    rhel_version = "unknown"
                    platform = "unknown"
                    result_by_component_id = self.search_leverage_by_componentid(component_id)
                    for each_device in result_by_component_id:
                        if each_device[3] != None:
                            hardware_info = [each_device[2], each_device[3], each_device[4]]
                        else:
                            hardware_info = [each_device[2], each_device[4]]
                        leverage_device.append(hardware_info)
                        leverage_cert_id = each_device[0]
                        rhel_version = each_device[5]
                        platform = each_device[6]
                    each_result = [component_id, original_device, test_class, leverage_device, rhel_version, platform]
                    if leverage_cert_id:
                        summary_list.append(each_result)
                    else:
                        if component_id not in missing_com_id:
                            missing_com_id.append(component_id)
        except Exception, e:
            traceback.print_exc()
        finally:
            self.cursor.close()
            self.db.close()

        return (summary_list, missing_test_id, missing_com_id)


class Result_Reivew(object):


    '''
    [
        rpm_file1: [
                        (
                        test_id: xxxx,
                        run: xxxx,
                        test_type: xxxx,
                        status: xxxx,
                        is_fv: xxxx,
                        subtest:[
                                name: xxxx,
                                status: xxxx,
                                ],
                        device: xxxx,
                        pci_id: xxxx,
                        driver: xxxx,
                        ),

                        (
                        test_id: xxxx,
                        run: xxxx,
                        test_type: xxxx,
                        status: xxxx,
                        is_fv: xxxx,
                        subtest:[
                                name: xxxx
                                status: xxxx
                                ],
                        device: xxxx,
                        pci_id: xxxx,
                        driver: xxxx,
                        ),
                    ],

        rpm_file2: [
                        (
                        test_id: xxxx,
                        run: xxxx,
                        test_type: xxxx,
                        status: xxxx,
                        is_fv: xxxx,
                        subtest:[
                                name: xxxx,
                                status: xxxx,
                                ],
                        device: xxxx,
                        pci_id: xxxx,
                        driver: xxxx,
                        ),

                        (
                        test_id: xxxx,
                        run: xxxx,
                        test_type: xxxx,
                        status: xxxx,
                        is_fv: xxxx,
                        subtest:[
                                name: xxxx
                                status: xxxx
                                ],
                        device: xxxx,
                        pci_id: xxxx,
                        driver: xxxx,
                        ),
                    ],
    ]
    '''
    pass

