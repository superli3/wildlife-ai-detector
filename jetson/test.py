from publisher import Connector

test = Connector()
print(test)
print(test.mqttc)
test.establish_connect()
test.publish_message('blah')