from azure.identity import DefaultAzureCredential

class Base():
    def __init__(self, subscription_id):
        self._credential = DefaultAzureCredential()
        self._subscription_id = subscription_id

    def _set_clients(self):
        '''OVERWRITE THIS METHOD IN CHILD CLASSES'''
        pass

    @property
    def credential(self) -> DefaultAzureCredential:
        return self._credential
    
    @property
    def subscription_id(self) -> str:
        return self._subscription_id
