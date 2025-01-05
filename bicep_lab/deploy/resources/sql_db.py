from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient
from base import Base
from utils import context, log

class SqlDb(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._sql_client = MySQLManagementClient(self.credential, self.subscription_id)

    def find_sql_db_by_prefix(self, resource_group_name, env_name) -> str:
        prefix = context.get_sql_db_name_prefix(env_name)
        try:
            dbs = self._sql_client.servers.list_by_resource_group(resource_group_name)
            for db in dbs:
                if db.name.startswith(prefix):
                    return db.name
            return ''
        except Exception as e:
            log.error(f"An error occurred while checking the SQL DB: {e}")
            raise e
        
