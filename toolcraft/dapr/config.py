"""
https://docs.dapr.io/developing-applications/sdks/python/python-client/

https://docs.dapr.io/developing-applications/building-blocks/configuration/howto-manage-configuration/

from dapr.clients import DaprClient

with DaprClient() as d:
    # Get Configuration
    configuration = d.get_configuration(store_name='configurationstore', keys=['orderId'], config_metadata={})

Check dapr-grpc examples here
https://github.com/dapr/python-sdk/tree/master/examples

"""
