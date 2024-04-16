from concerto import ComponentType
from concerto import Program, Add, PushB, Connect, Wait

def system_type():
    t = ComponentType("system")
    pl_deployed = t.add_place("deployed")
    pl_configured = t.add_place("configured")
    pl_initiated = t.add_place("initiated")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_switch_on = t.add_behavior("deploy")
    bhv_switch_on.add_transition("deploy11", pl_initiated, pl_configured)
    bhv_switch_on.add_transition("deploy12", pl_initiated, pl_configured)
    bhv_switch_on.add_transition("deploy13", pl_initiated, pl_configured)
    bhv_switch_on.add_transition("deploy2", pl_configured, pl_deployed)
    bhv_interrupt = t.add_behavior("interrupt")
    bhv_interrupt.add_transition("interrupt1", pl_deployed, pl_configured)
    bhv_stop = t.add_behavior("stop")
    bhv_stop.add_transition("stop1", pl_deployed, pl_initiated)
    t.add_provide_port("service", {pl_deployed})
    t.add_use_port("dbService", {pl_configured, pl_deployed})
    return t


def listener_type():
    t = ComponentType("listener")
    pl_running = t.add_place("running")
    pl_configured = t.add_place("configured")
    pl_paused = t.add_place("paused")
    pl_off = t.add_place("off")
    t.set_initial_place(pl_off)
    t.set_running_place(pl_running)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy1", pl_off, pl_paused)
    bhv_deploy.add_transition("deploy2", pl_paused, pl_configured)
    bhv_deploy.add_transition("deploy3", pl_configured, pl_running)
    bhv_update = t.add_behavior("update")
    bhv_update.add_transition("update1", pl_running, pl_paused)
    bhv_destroy = t.add_behavior("destroy")
    bhv_destroy.add_transition("destroy1", pl_paused, pl_off)
    t.add_use_port("sysService", {pl_running, pl_configured})
    t.add_provide_port("rcv", {pl_running})
    t.add_provide_port("config", {pl_running, pl_configured})
    return t


def sensor_type():
    t = ComponentType("sensor")
    pl_running = t.add_place("running")
    pl_configured = t.add_place("configured")
    pl_installed = t.add_place("installed")
    pl_provisioned = t.add_place("provisioned")
    pl_off = t.add_place("off")
    t.set_initial_place(pl_off)
    t.set_running_place(pl_running)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy11", pl_off, pl_provisioned)
    bhv_deploy.add_transition("deploy12", pl_off, pl_provisioned)
    bhv_deploy.add_transition("deploy13", pl_off, pl_provisioned)
    bhv_deploy.add_transition("deploy2", pl_provisioned, pl_installed)
    bhv_deploy.add_transition("deploy3", pl_installed, pl_configured)
    bhv_deploy.add_transition("deploy4", pl_configured, pl_running)
    bhv_pause = t.add_behavior("pause")
    bhv_pause.add_transition("pause1", pl_running, pl_provisioned)
    bhv_stop = t.add_behavior("stop")
    bhv_stop.add_transition("stop1", pl_provisioned, pl_off)
    t.add_use_port("rcvService", {pl_running, pl_configured})
    t.add_use_port("configService", {pl_configured, pl_installed, pl_running})
    return t


def database_type():
    t = ComponentType("database")
    pl_initiated = t.add_place("initiated")
    pl_configured = t.add_place("configured")
    pl_bootstrapped = t.add_place("bootstrapped")
    pl_deployed = t.add_place("deployed")
    pl_registered = t.add_place("registered")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy11", pl_initiated, pl_configured)
    bhv_deploy.add_transition("deploy12", pl_initiated, pl_configured)
    bhv_deploy.add_transition("deploy2", pl_configured, pl_bootstrapped)
    bhv_deploy.add_transition("deploy3", pl_bootstrapped, pl_deployed)
    bhv_interrupt = t.add_behavior("interrupt")
    bhv_interrupt.add_transition("interrupt1", pl_deployed, pl_registered)
    bhv_pause = t.add_behavior("pause")
    bhv_pause.add_transition("pause1", pl_registered, pl_bootstrapped)
    bhv_update = t.add_behavior("update")
    bhv_update.add_transition("update", pl_registered, pl_configured)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall1", pl_registered, pl_initiated)
    t.add_provide_port("service", {pl_deployed})
    return t

    # --------------------------------

def db_deploy():
    return  Program([
        Add("mydb0", database_type()),
        Connect("mydb0", "service", "mysys0", "dbService"),
        PushB("mydb0", "deploy", "db1")
    ])
    
def sys_deploy(n):
    program = [
        Add("mysys0", system_type()),
        Connect("mydb0", "service", "mysys0", "dbService"),
    ]
    for i in range(1,n+1):
        program += [
            Add(f"listener{i}", listener_type()),
            Connect("mysys0", "service", f"listener{i}", "sysService"),
            Connect(f"listener{i}", "rcv", f"sensor{i}", "rcvService"),
            Connect(f"listener{i}", "config", f"sensor{i}", "configService")
        ]
    program += [PushB("mysys0", "deploy", "sys1")]
    program += [
        PushB(f"listener{i}", "deploy", f"{i}lst1")
        for i in range(1,n+1)
    ]
    return Program(program)

def sensor_deploy(i):
    return Program([
        Add(f"sensor{i}", sensor_type()),
        Connect(f"listener{i}", "rcv", f"sensor{i}", "rcvService"),
        Connect(f"listener{i}", "config", f"sensor{i}", "configService"),
        PushB(f"sensor{i}", "deploy", f"{i}sens1")
    ])
    
# --------------------------------

def db_update_listeners():
    return  Program([])
    
def sys_update_listeners(n):
    program = []
    for i in range(1,n+1): 
        program += [
            PushB(f"listener{i}", "update", f"{2+i*2}"),
            PushB(f"listener{i}", "deploy", f"{3+i*2}")
        ]
    return Program(program)

def sensor_update_listeners(i):
    progr = [
        PushB(f"sensor{i}", "pause", f"0"),
        Wait(f"listener{i}", f"{2+i*2}"),
        PushB(f"sensor{i}", "start", f"1")
    ]
    return Program(progr)
