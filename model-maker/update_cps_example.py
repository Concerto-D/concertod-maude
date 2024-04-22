from examples.cps import *
from concerto import ComponentInstance
from concerto2maude import gen_maude

def _connect(provider, provide_port_name, user, use_port_name):
    provider.connect_provide_port(provider.type().get_provide_port(provide_port_name), user, user.type().get_use_port(use_port_name))
    user.connect_use_port(user.type().get_use_port(use_port_name), provider, provider.type().get_provide_port(provide_port_name))

def deploy_cps(n):
    inventory = {}
    inventory["node1"] = ({}, db_deploy())
    inventory["node2"] = ({}, sys_deploy(n))
    for i in range(1, n+1):
        inventory[f"node{2+i}"] = ({}, sensor_deploy(i))
    return gen_maude(inventory)

def update_cps(n):
    # -------------------------
    # Component definitions
    # -------------------------
    database = ComponentInstance("mydb0", database_type())
    system = ComponentInstance("mysys0", system_type())
    listeners, sensors = {}, {}
    for i in range(1, n+1):
        listeners[i] = ComponentInstance(f"listener{i}", listener_type())
        sensors[i] = ComponentInstance(f"sensor{i}", sensor_type())
    inventory = {}
    # -------------------------
    # Pre-update existing connections
    # -------------------------
    _connect(database, "service", system, "dbService")
    for i in range(1, n+1):
        _connect(system, "service", listeners[i], "sysService")
        _connect(listeners[i], "rcv", sensors[i], "rcvService")
        _connect(listeners[i], "config", sensors[i], "configService")
    # -------------------------
    # Node definitions
    # -------------------------
    inventory["node1"] = (
        {database: "deployed"}, 
        db_update_listeners())
    # -------------------------
    node2_components = {system: "deployed"}
    for i in range(1, n+1):
        node2_components[listeners[i]] = "running"
    inventory["node2"] = (node2_components, sys_update_listeners(n))
    # -------------------------
    for i in range(1, n+1):
        node2i_components = {sensors[i]: "running"}
        inventory[f"node{2+i}"] = (node2i_components, sensor_update_listeners(i))
        
    return gen_maude("listener-sensor-example", inventory)


if __name__ == "__main__":
    maude = update_cps(1)
    # maude = deploy_cps(1)
    print(maude)