from concerto import *

ids_of_bhv = set()
type_of_comp = {} # For a component name, store its concrete type

def flatmap(func, iterable):
    return list(chain.from_iterable(map(func, iterable)))

def get_connections(instance: ComponentInstance):
    #  a set of (id: str, useport: str, provider: str, provideport: str)
    connections = set()
    for port in instance.all_connections().keys():
        if port.is_provide_port():
            provider = instance.id()
            provide_port = instance.type().name() + port.name().capitalize()
            for connection in instance.all_connections()[port]:
                user = connection[0].id()
                use_port = connection[0].type().name() + connection[1].name().capitalize()
                connections.add((user, use_port, provider, provide_port))
        if port.is_use_port():
            user = instance.id()
            use_port = instance.type().name() + port.name().capitalize()
            for connection in instance.all_connections()[port]:
                provider = connection[0].id()
                provide_port = connection[0].type().name() + connection[1].name().capitalize()
                connections.add((user, use_port, provider, provide_port))
    return connections

def get_all_ids(instances, program):
    ids = set(map(lambda instance: instance.id(), instances))
    add_instructions = list(filter(lambda instr: instr.isAdd(), program.instructions()))
    return ids.union(set(map(lambda add: add.component(), add_instructions)))

def get_instance_names(instances):
    if len(instances) == 0:
        return "empty" 
    names = set(map(lambda instance: f"inst{instance.id().capitalize()}", instances))
    return ', '.join(names)

def make_connections_name(node_name):
    return f"connections{node_name.capitalize()}"

def make_maude_instruction(instruction: Instruction):
    if instruction.isAdd():
        add = instruction
        return f"add({add.component()},{add.type().name()})"
    if instruction.isCon():
        connect = instruction
        type_pro = type_of_comp[connect.provider()].name()
        type_use = type_of_comp[connect.user()].name()
        return f"con({connect.user()},{type_use}{connect.using_port().capitalize()},{connect.provider()},{type_pro}{connect.providing_port().capitalize()})" 
    if instruction.isDel():
        delete = instruction
        return f"del({delete.component()})"
    if instruction.isDiscon():
        disconnect = instruction
        type_pro = type_of_comp[disconnect.provider()].name()
        type_use = type_of_comp[disconnect.user()].name()
        return f"dcon({disconnect.user()},{type_use}{disconnect.using_port().capitalize()},{disconnect.provider()},{type_pro}{disconnect.providing_port().capitalize()})" 
    if instruction.isPushB():
        pushb = instruction
        type_comp = type_of_comp[pushb.component()]
        ids_of_bhv.add(pushb.id())
        return f"pushB({pushb.component()}, {type_comp.name()}{pushb.behavior().capitalize()}, {pushb.id()})" 
    if instruction.isWait():
        wait = instruction
        return f"wait({wait.component()}, {wait.behavior()})"
    
def make_port(typename, port, sep_port_bounded="!"):
    bounded = list(map(lambda place: f"{typename}{place.name().capitalize()}", port.bound_places()))
    return f"{typename}{port.name().capitalize()} {sep_port_bounded} ({', '.join(bounded)})"     
    
def make_conf_program(program):    
    plan = ' '.join(map(lambda instr: make_maude_instruction(instr), program.instructions()))
    return plan

def gen_maude_type(type: ComponentType):
    ops, eqs = set(), set()
    ops.add(f"op {type.name()} : -> ComponentType .")
    use_ports = "empty"
    provide_ports = "empty"
    
    if type.places() is not []:
        dict_place_station = {f"{type.name()}{place.name().capitalize()}": f"st{type.name()}{place.name().capitalize()}" for place in type.places()}
        places = list(map(lambda place: f"{type.name()}{place.name().capitalize()}", type.places()))
        stations = list(map(lambda place: f"st{type.name()}{place.name().capitalize()}", type.places()))
        st_places = list(map(lambda stp: f"{stp[1]} ; {stp[0]}" , zip(places, stations)))
        init = f"{type.name()}{type.initial_place().name().capitalize()}"
        ops.add("ops " + ' '.join(places) + " : -> Place .")
        ops.add("ops " + ' '.join(stations) + " : -> Station .")
        ops.add(f"op {init} : -> InitialPlace .")
    
    if type.provide_ports():
        ops.add("ops " + ' '.join(map(lambda port: f"{type.name()}{port.name().capitalize()}", type.provide_ports())) + " : -> ProvidePort .")
        provide_ports = ', '.join(map(lambda port: make_port(type.name(), port, "?"), type.provide_ports()))
        
    if type.use_ports():
        ops.add("ops " + ' '.join(map(lambda port: f"{type.name()}{port.name().capitalize()}", type.use_ports())) + " : -> UsePort .")
        use_ports = ', '.join(map(lambda port: make_port(type.name(), port, "!"), type.use_ports()))

    behavior_transitions = {}
    transitions = {}
    for behavior in type.behaviors():
        behavior_name = f"{type.name()}{behavior.name().capitalize()}"
        behavior_transitions[behavior_name] = []
        for transition in behavior.transitions_as_dict().keys():
            act_transition = behavior.transitions_as_dict()[transition]
            source = f"{type.name()}{act_transition.source().name().capitalize()}"
            dest = dict_place_station[f"{type.name()}{act_transition.destination()[0].name().capitalize()}"]
            transition_name = f"{type.name()}{transition.capitalize()}"
            transitions[transition_name] = f"t({source}, {dest})"
            behavior_transitions[behavior_name].append(transition_name)
    ops.add(f"ops {' '.join(transitions.keys())} : -> Transition .")
    for tr in transitions.keys():
        eqs.add(f"eq {tr} = {transitions[tr]} .")
    ops.add(f"ops {' '.join(behavior_transitions.keys())} : -> Behavior .")
    eq_behaviors_tmp = {}
    for behavior in behavior_transitions.keys():
        eq_behaviors_tmp[behavior] = f"{','.join(behavior_transitions[behavior])}"
    for bhv in eq_behaviors_tmp.keys():
        eqs.add(f"eq {bhv} = b({eq_behaviors_tmp[bhv]}) .")
    transition_names = ', '.join(transitions.keys())
    behavior_names = ', '.join(eq_behaviors_tmp.keys())
    eqs.add(f"eq {type.name()} = {{ places: {','.join(places)}, initial: {init}, stationPlaces: {', '.join(st_places)}, transitions: ({transition_names}), behaviors: ({behavior_names}), groupUses: {use_ports}, groupProvides: {provide_ports} }} .")    
    return ops, eqs

def gen_maude_instance(instance: ComponentInstance, active: str):
    ops, eqs = set(), set()
    instance_name = f"inst{instance.id().capitalize()}"
    instance_id = instance.id()
    instance_type = instance.type().name()
    ops.add(f"op {instance_name} : -> Instance .")
    eqs.add(f"eq {instance_name} = < id: {instance_id}, type: {instance_type}, queueBehavior: nil, marking: m({instance_type}{active.capitalize()}, empty, empty) > .")
    return ops, eqs

def gen_maude_connections(name_of_connections_set, connections):
    ops, eqs = set(), set()
    ops.add(f"op {name_of_connections_set} : -> Connections ." )
    if len(connections) == 0:
        str_connections = ["empty"]
    else:
        str_connections = list(map(lambda tuple: f"{(tuple[0], tuple[1], tuple[2], tuple[3])}", connections))
    eqs.add(f"eq {name_of_connections_set} = " + ', '.join(str_connections) +" ." )
    return ops, eqs

def fill_type_of_comp_from_adds(add_instructions: list[Add]):
    for add in add_instructions:
        comp = add.component()
        type = add.type()
        type_of_comp[comp] = type

def fill_type_of_comp(instances: list[ComponentInstance]):
    for instance in instances:
        comp = instance.id()
        type = instance.type()
        type_of_comp[comp] = type

def gen_maude(example_name, inventory):
    # inventory: str -> ({instance: states}, program)
    # For a node name, inventory stores: (i) the current instances and their state and (ii) a concerto-d program
    all_types = set()
    all_instances = set()
    connections = {}
    ops = set()
    eqs = set()
    eq_confs = {}
    id_instance_place = {}
    for node in inventory.keys():
        fill_type_of_comp(inventory[node][0])
        program = inventory[node][1]
        add_instructions = list(filter(lambda instr: instr.isAdd(), program.instructions()))
        fill_type_of_comp_from_adds(add_instructions)
    for node in inventory.keys():
        instances = inventory[node][0]
        program = inventory[node][1]
        add_instructions = list(filter(lambda instr: instr.isAdd(), program.instructions()))
        # Get types
        instantiated_types = set(map(lambda instance: instance.type(), instances))
        added_types = set(map(lambda add: add.type(), add_instructions))
        all_types = all_types.union(instantiated_types).union(added_types)
        # Instances
        for instance in inventory[node][0].keys():
            id_instance_place[instance.id()] = inventory[node][0][instance]
        all_instances = all_instances.union(instances)
        connections[make_connections_name(node)] = set(flatmap(lambda instance: get_connections(instance), instances)) # TODO somewhere consider it empty
        # Conf
        conf_name = f"conf{node.capitalize()}"
        conf_ids = get_all_ids(instances, program)
        for id in conf_ids:
            ops.add(f"op {id} : -> IdentInstance .")
        conf_instances = get_instance_names(instances)
        conf_connections = make_connections_name(node)
        conf_program = make_conf_program(program)
        eq_confs[conf_name] = f"eq {conf_name} = < ids: {', '.join(conf_ids)}, instances: {conf_instances}, connections: {conf_connections}, program: {conf_program}, msgs: [], receive: nil, send: nil, history: empty > ."
    for type in all_types:
        _ops, _eqs = gen_maude_type(type)
        ops = ops.union(_ops)
        eqs = eqs.union(_eqs)
    for instance in all_instances:
        _ops, _eqs = gen_maude_instance(instance, id_instance_place[instance.id()])
        ops = ops.union(_ops)
        eqs = eqs.union(_eqs)
    for connection in connections.keys():
        _ops, _eqs = gen_maude_connections(connection, connections[connection])
        ops = ops.union(_ops)
        eqs = eqs.union(_eqs)
    all_lines = list(ops) + list(eqs)
    ops_ident_bhv = f"ops {' '.join(ids_of_bhv)} : -> IdentBehavior . "
    all_lines = all_lines + [ops_ident_bhv]
    eq_confs_lines = []
    net_confs = []
    for eq_conf_name in eq_confs.keys():
        eq_conf_line = eq_confs[eq_conf_name]
        eq_confs_lines.append(f"op {eq_conf_name} : ->  LocalConfiguration .")
        eq_confs_lines.append(eq_conf_line)
        net_confs.append(eq_conf_name)
    net_op = "op globalSystem : -> Net ."
    net_eq = f"eq globalSystem = {', '.join(net_confs)} . "
    all_lines = all_lines + eq_confs_lines + [net_op, net_eq]
    indented_lines = ['\t' + line for line in all_lines]
    indented_maude = '\n'.join(indented_lines)
    maude = f"""fmod {example_name.upper()} is 
\tinc NET-D-CONFIGURATION .
\tinc CONSISTENCY-PORTS-FIRING-TRANSITION .
\tinc CONSISTENCY-PORTS-ENTERING-PLACE .
\tinc COLLECT-EXTERNAL-MESSAGES-FIRING .
\tinc COLLECT-EXTERNAL-MESSAGES-WAIT .
\tinc COLLECT-EXTERNAL-MESSAGES-DISCONNECT .
\tinc COLLECT-EXTERNAL-MESSAGES-ENTERING-PLACE .
\tinc UPDATE-COMMUNICATION-MESSAGES .

{indented_maude}
endfm 
    """
    return maude
