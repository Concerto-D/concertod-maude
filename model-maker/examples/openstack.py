from concerto import ComponentType

def mariadb_master_type() -> ComponentType:
    t = ComponentType("mariadb")
    pl_initiated = t.add_place("initiated")
    pl_configured = t.add_place("configured")
    pl_bootstrapped = t.add_place("bootstrapped")
    pl_restarted = t.add_place("restarted")
    pl_registered = t.add_place("registered")
    pl_deployed = t.add_place("deployed")
    pl_interrupted = t.add_place("interrupted")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("configure0", pl_initiated, pl_configured, cost=3)
    bhv_deploy.add_transition("configure1", pl_initiated, pl_configured, cost=5)
    bhv_deploy.add_transition("bootstrap", pl_configured, pl_bootstrapped, cost=26)
    bhv_deploy.add_transition("start", pl_bootstrapped, pl_restarted, cost=13)
    bhv_deploy.add_transition("register", pl_restarted, pl_registered, cost=3)
    bhv_deploy.add_transition("deploy", pl_registered, pl_deployed, cost=13)
    bhv_interrupt = t.add_behavior("interrupt")
    bhv_interrupt.add_transition("interrupt", pl_deployed, pl_interrupted, cost=1)
    bhv_pause = t.add_behavior("pause")
    bhv_pause.add_transition("pause", pl_interrupted, pl_bootstrapped, cost=1)
    bhv_stop = t.add_behavior("update")
    bhv_stop.add_transition("update", pl_interrupted, pl_configured, cost=2)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_interrupted, pl_initiated, cost=5)
    t.add_use_port("haproxy_service", {pl_bootstrapped, pl_restarted})
    t.add_use_port("common_service", {pl_restarted, pl_registered, pl_deployed, pl_interrupted})
    t.add_provide_port("service", {pl_deployed})
    return t

def mariadb_master_type() -> ComponentType:
    t = ComponentType("mariadb_master")
    pl_initiated = t.add_place("initiated")
    pl_configured = t.add_place("configured")
    pl_bootstrapped = t.add_place("bootstrapped")
    pl_restarted = t.add_place("restarted")
    pl_registered = t.add_place("registered")
    pl_deployed = t.add_place("deployed")
    pl_interrupted = t.add_place("interrupted")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("configure0", pl_initiated, pl_configured, cost=3)
    bhv_deploy.add_transition("configure1", pl_initiated, pl_configured, cost=5)
    bhv_deploy.add_transition("bootstrap", pl_configured, pl_bootstrapped, cost=26)
    bhv_deploy.add_transition("start", pl_bootstrapped, pl_restarted, cost=13)
    bhv_deploy.add_transition("register", pl_restarted, pl_registered, cost=3)
    bhv_deploy.add_transition("deploy", pl_registered, pl_deployed, cost=13)
    bhv_interrupt = t.add_behavior("interrupt")
    bhv_interrupt.add_transition("interrupt", pl_deployed, pl_interrupted, cost=1)
    bhv_pause = t.add_behavior("pause")
    bhv_pause.add_transition("pause", pl_interrupted, pl_bootstrapped, cost=1)
    bhv_stop = t.add_behavior("update")
    bhv_stop.add_transition("update", pl_interrupted, pl_configured, cost=2)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_interrupted, pl_initiated, cost=5)
    t.add_use_port("haproxy_service", {pl_bootstrapped, pl_restarted})
    t.add_use_port("common_service", {pl_restarted, pl_registered, pl_deployed, pl_interrupted})
    t.add_provide_port("service", {pl_deployed})
    return t

def mariadb_worker_type() -> ComponentType:
    t = ComponentType("mariadb_worker")
    pl_initiated = t.add_place("initiated")
    pl_configured = t.add_place("configured")
    pl_bootstrapped = t.add_place("bootstrapped")
    pl_restarted = t.add_place("restarted")
    pl_registered = t.add_place("registered")
    pl_deployed = t.add_place("deployed")
    pl_interrupted = t.add_place("interrupted")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("configure0", pl_initiated, pl_configured, cost=3)
    bhv_deploy.add_transition("configure1", pl_initiated, pl_configured, cost=5)
    bhv_deploy.add_transition("bootstrap", pl_configured, pl_bootstrapped, cost=26)
    bhv_deploy.add_transition("start", pl_bootstrapped, pl_restarted, cost=13)
    bhv_deploy.add_transition("register", pl_restarted, pl_registered, cost=3)
    bhv_deploy.add_transition("deploy", pl_registered, pl_deployed, cost=13)
    bhv_interrupt = t.add_behavior("interrupt")
    bhv_interrupt.add_transition("interrupt", pl_deployed, pl_interrupted, cost=1)
    bhv_pause = t.add_behavior("pause")
    bhv_pause.add_transition("pause", pl_interrupted, pl_bootstrapped, cost=1)
    bhv_stop = t.add_behavior("update")
    bhv_stop.add_transition("update", pl_interrupted, pl_configured, cost=2)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_interrupted, pl_initiated, cost=5)
    t.add_use_port("haproxy_service", {pl_bootstrapped, pl_restarted})
    t.add_use_port("common_service", {pl_restarted, pl_registered, pl_deployed, pl_interrupted})
    t.add_use_port("master_service", {pl_bootstrapped, pl_restarted, pl_registered, pl_deployed, pl_interrupted})
    t.add_provide_port("service", {pl_deployed})
    return t

def keystone_type() -> ComponentType:
    t = ComponentType("keystone")
    pl_initiated = t.add_place("initiated")
    pl_pulled = t.add_place("pulled")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("pull", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("deploy", pl_pulled, pl_deployed)
    bhv_stop = t.add_behavior("stop")
    bhv_stop.add_transition("stop", pl_deployed, pl_pulled)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("turnoff", pl_deployed, pl_initiated)
    t.add_use_port("mariadb_service", {pl_pulled, pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def nova_type() -> ComponentType:
    t = ComponentType("nova")
    pl_initiated = t.add_place("initiated")
    pl_pulled = t.add_place("pulled")
    pl_ready = t.add_place("ready")
    pl_restarted = t.add_place("restarted")
    pl_deployed = t.add_place("deployed")
    pl_interrupted = t.add_place("interrupted")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("pull0", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("pull1", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("pull2", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("ready0", pl_pulled, pl_ready)
    bhv_deploy.add_transition("ready1", pl_pulled, pl_ready)
    bhv_deploy.add_transition("start", pl_ready, pl_restarted)
    bhv_deploy.add_transition("deploy", pl_restarted, pl_deployed)
    bhv_deploy.add_transition("cell_setup", pl_pulled, pl_deployed)
    bhv_interrupt = t.add_behavior("interrupt")
    bhv_interrupt.add_transition("interrupt", pl_deployed, pl_interrupted)
    bhv_pause = t.add_behavior("pause")
    bhv_pause.add_transition("pause", pl_interrupted, pl_ready)
    bhv_stop = t.add_behavior("update")
    bhv_stop.add_transition("unpull", pl_interrupted, pl_pulled)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_interrupted, pl_initiated)
    t.add_use_port("mariadb_service", {pl_pulled, pl_ready, pl_restarted, pl_deployed})
    t.add_use_port("keystone_service", {pl_ready, pl_restarted, pl_deployed, pl_interrupted})
    t.add_provide_port("service", {pl_deployed})
    return t

def neutron_type() -> ComponentType:
    t = ComponentType("neutron")
    pl_initiated = t.add_place("initiated")
    pl_pulled = t.add_place("pulled")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("pull0", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("pull1", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("pull2", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("deploy", pl_pulled, pl_deployed)
    bhv_stop = t.add_behavior("stop")
    bhv_stop.add_transition("stop", pl_deployed, pl_pulled)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("turnoff", pl_deployed, pl_initiated)
    t.add_use_port("mariadb_service", {pl_pulled, pl_deployed})
    t.add_use_port("keystone_service", {pl_pulled, pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def glance_type() -> ComponentType:
    t = ComponentType("glance")
    pl_initiated = t.add_place("initiated")
    pl_pulled = t.add_place("pulled")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("pull0", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("pull1", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("pull2", pl_initiated, pl_pulled)
    bhv_deploy.add_transition("deploy", pl_pulled, pl_deployed)
    bhv_stop = t.add_behavior("stop")
    bhv_stop.add_transition("stop", pl_deployed, pl_pulled)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("turnoff", pl_deployed, pl_initiated)
    t.add_use_port("mariadb_service", {pl_pulled, pl_deployed})
    t.add_use_port("keystone_service", {pl_pulled, pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def facts_type() -> ComponentType:
    t = ComponentType("facts")
    pl_initiated = t.add_place("initiated")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy", pl_initiated, pl_deployed)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_deployed, pl_initiated)
    t.add_provide_port("service", {pl_deployed})
    return t

def haproxy_type() -> ComponentType:
    t = ComponentType("haproxy")
    pl_initiated = t.add_place("initiated")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy", pl_initiated, pl_deployed)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_deployed, pl_initiated)
    t.add_use_port("facts_service", {pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def memcached_type() -> ComponentType:
    t = ComponentType("memcached")
    pl_initiated = t.add_place("initiated")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy", pl_initiated, pl_deployed)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_deployed, pl_initiated)
    t.add_use_port("facts_service", {pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def ovswitch_type() -> ComponentType:
    t = ComponentType("ovswitch")
    pl_initiated = t.add_place("initiated")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy", pl_initiated, pl_deployed)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_deployed, pl_initiated)
    t.add_use_port("facts_service", {pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def rabbitmq_type() -> ComponentType:
    t = ComponentType("rabbitmq")
    pl_initiated = t.add_place("initiated")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy", pl_initiated, pl_deployed)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_deployed, pl_initiated)
    t.add_use_port("facts_service", {pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t

def common_type() -> ComponentType:
    t = ComponentType("common")
    pl_initiated = t.add_place("initiated")
    pl_configured = t.add_place("configured")
    pl_deployed = t.add_place("deployed")
    t.set_initial_place(pl_initiated)
    t.set_running_place(pl_deployed)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("configure", pl_initiated, pl_configured)
    bhv_deploy.add_transition("deploy", pl_configured, pl_deployed)
    bhv_stop = t.add_behavior("stop")
    bhv_stop.add_transition("stop", pl_deployed, pl_configured)
    bhv_uninstall = t.add_behavior("uninstall")
    bhv_uninstall.add_transition("uninstall", pl_deployed, pl_initiated)
    t.add_use_port("facts_service", {pl_configured, pl_deployed})
    t.add_provide_port("service", {pl_deployed})
    return t
