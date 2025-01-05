from azure.mgmt.subscription import SubscriptionClient
from azure.core.exceptions import HttpResponseError
from base import Base

class Subscription(Base):
    def __init__(self, subscription_id):
        super().__init__(subscription_id)
        self._set_clients()
    
    def _set_clients(self):
        self._subscription_client = SubscriptionClient(self.credential)
    
    def get_subscription_info(self):
        try:
            info = self._subscription_client.subscriptions.get(self.subscription_id)
            return {
                'id': info.subscription_id,
                'name': info.display_name,
                'tenant_id': info.tenant_id,
                'state': info.state,
                'policies': info.subscription_policies
            }
        except Exception as e:
            raise e
