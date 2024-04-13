from concerto import *
from itertools import chain
from examples.openstack import *
from examples.cps import *

type_of_comp = {}

def cap1(input_string):
    if len(input_string) == 0:
        return input_string
    else:
        return input_string[0].upper() + input_string[1:]

def __make_port(typename, port, sep_port_bounded="!"):
    bounded = list(map(lambda place: f"{typename}{cap1(place.name())}", port.bound_places()))
    return f"{typename}{cap1(port.name())} {sep_port_bounded} ({', '.join(bounded)})" 

def flatmap(func, iterable):
    return list(chain.from_iterable(map(func, iterable)))

def gen_instances(instances, states):
    if len(instances) == 0:
        return "empty"
    else:
        maude_instances = list(map(lambda instance: gen_instance(instance, states[instance]), instances))
        id_instances = map(lambda x: x[0], maude_instances)
        name_instances = flatmap(lambda x: x[1], maude_instances)
        str_instances = flatmap(lambda x: x[2], maude_instances)
        return list(id_instances), list(name_instances), str_instances
    
def gen_connections(instances, node_name):
    lines = []
    connections = set()
    for inst in instances:
        inst = ComponentInstance("myinst", None)
        name = inst.id()
        for port in inst.all_connections().keys():
            if port.is_use_port():
                use_port_name = port.name() 
                use_type = inst.type().name()
                use_name = name
                for connected in inst.all_connections()[port]:
                    provider = connected[0]
                    provide_name = provider.id()
                    provide_type = provider.type().name()
                    provide_port_name = connected[1].name()
            if port.is_provide_port():
                provide_port_name = port.name() 
                provide_type = inst.type().name()
                provide_name = name
                for connected in inst.all_connections()[port]:
                    user = connected[0]
                    use_name = user.id()
                    use_type = user.type().name()
                    use_port_name = connected[1].name()
            connections.add((f"{use_name}, {use_type}{use_port_name.capitalize()}, {provide_name}, {provide_type}{provide_port_name.capitalize()}"))
    name_connections = f"connections{node_name.capitalize()}"
    lines.append(f"op {name_connections} : => Connections .")
    lines.append(f"eq {name_connections} = {' '.join(connections)} . ")
    return name_connections, lines

def gen_instance(instance: ComponentInstance, curr):
    name = f"instance{instance.id().capitalize()}"
    id = instance.id() 
    type = instance.type().name() 
    idInstance = f"op {id} : -> IdentInstance ."
    decInstance =  f"op {name} : -> Instance ."
    defInstance =  f"eq {name} = < id:{id},type:{type},queueBehavior: nil, marking:m({type}{curr.capitalize()}, empty, empty) > ."
    lines = [idInstance, decInstance, defInstance]
    return id, name, lines        
        
        
def gen_maude(programs, instances=[], states={}):
    conf_names = list(map(lambda program: f"confwatever", programs))
    maude = "ops " + ' '.join(conf_names) + " : ->  LocalConfiguration ."
    adds = flatmap(lambda program: filter(lambda instr: instr.isAdd(), program.instructions()), programs) # Get all add from all programs using flatmap
    types = set()
    for add in adds:
        type_of_comp[add.component()] = add.type()
        types.add(add.type())
    for instance in instances:
        types.add(instance.type())
    maude += "\nop test : -> Net ."
    maude += "\n" + '\n'.join(map(lambda type: gen_maude_from_type(type), types))
    
    id_exist_instances, name_exist_instances, str_exist_instances = gen_instances(instances, states)
    maude += "\n" + '\n'.join(str_exist_instances)
    
    maude += "\n" + "ops " + ' '.join(id_exist_instances) + " : -> IdentInstance ."
    
    # TODO : dans conf, les ids doivent etre etendu pour inclure ceux des instances deja là
    # TODO la ca va pas. On a autant de node que de program. Donc il faut que je recupere, pour chaque program, les instances deja la
    # Autrement dit, instances c'est pas une list, mais un dict["nodename", instances]
    connections_name, connections_maude = gen_connections(instances, "") 
    maude += "\n"
    # TODO for all connection, add to conf. Connections must be generated then
    
    maude += "\n" + '\n'.join(map(lambda program: gen_maude_program(program), programs))
    maude += "\n" + f"eq test = {' ; '.join(conf_names)} ."
    
    lines = maude.split('\n')
    indented_lines = ['\t' + line for line in lines]
    indented_maude = '\n'.join(indented_lines)
    res = f"""mod Concerto-PREDS is 
\tprotecting OPERATIONAL-SEMANTICS . 
\tincluding SATISFACTION .

{indented_maude}
endm 
    """
    
    return res

def gen_maude_program(program):
    add_instr = filter(lambda instr: instr.isAdd(), program.instructions())
    list_ids = list(map(lambda add: add.component(), add_instr))
    ids = ', '.join(list_ids)
    plan = ' '.join(map(lambda instr: __make_instruction(instr), program.instructions()))
    pushb_instr = filter(lambda instr: instr.isPushB(), program.instructions())
    IdentBehavior = "ops " + ' '.join(map(lambda instr: f"{instr.id()}", pushb_instr)) + " : -> IdentBehavior ."
    IdentInstance = "ops " + ' '.join(list_ids) + " : -> IdentInstance ."
    return IdentBehavior + '\n' + IdentInstance + '\n' + f"eq conf{cap1(program.id())} = <id:({ids}), instances:empty, connections:empty, program:{plan} , msgs:empty, receive:nil, send:nil, history:empty > ."

def gen_maude_from_type(type: ComponentType) -> str:
    name = type.name()
    place, InitialPlace, station, ProvidePort, usePort = "", "", "", "", ""
    provide_ports = "empty"
    use_ports = "empty"
    componentType = f"op {name} : -> ComponentType ."
    
    if type.places() is not []:
        dict_place_station = {f"{name}{cap1(place.name())}": f"st{cap1(name)}{cap1(place.name())}" for place in type.places()}
        places = list(map(lambda place: f"{name}{cap1(place.name())}", type.places()))
        stations = list(map(lambda place: f"st{cap1(name)}{cap1(place.name())}", type.places()))
        st_places = list(map(lambda stp: f"{stp[1]} ; {stp[0]}" , zip(places, stations)))
        init = f"{name}{cap1(type.initial_place().name())}"
        place = "ops " + ' '.join(places) + " : -> Place ."
        station = "ops " + ' '.join(stations) + " : -> Station ."
        InitialPlace = f"op {init} : -> InitialPlace ."
        
    if type.provide_ports():
        ProvidePort = "ops " + ' '.join(map(lambda port: f"{name}{cap1(port.name())}", type.provide_ports())) + " : -> ProvidePort ."
        provide_ports = ', '.join(map(lambda port: __make_port(name, port, "?"), type.provide_ports()))
        
    if type.use_ports():
        usePort = "ops " + ' '.join(map(lambda port: f"{name}{cap1(port.name())}", type.use_ports())) + " : -> UsePort ."
        use_ports = ', '.join(map(lambda port: __make_port(name, port, "!"), type.use_ports()))
        
    behavior_transitions = {}
    transitions = {}
    for behavior in type.behaviors():
        behavior_name = f"{name}{cap1(behavior.name())}"
        behavior_transitions[behavior_name] = []
        for transition in behavior.transitions_as_dict().keys():
            act_transition = behavior.transitions_as_dict()[transition]
            source = f"{name}{cap1(act_transition.source().name())}"
            dest = dict_place_station[f"{name}{cap1(act_transition.destination()[0].name())}"]
            transition_name = f"{name}{cap1(transition)}"
            transitions[transition_name] = f"t({source}, {dest})"
            behavior_transitions[behavior_name].append(transition_name)
    ops_transitions = f"ops {' '.join(transitions.keys())} : -> Transition ."
    eq_transitions = '\n'.join(map(lambda tr: f"eq {tr} = {transitions[tr]} .", transitions.keys()))
    ops_behaviors = f"ops {' '.join(behavior_transitions.keys())} : -> Behavior ."
    eq_behaviors_tmp = {}
    for behavior in behavior_transitions.keys():
        eq_behaviors_tmp[behavior] = f"{','.join(behavior_transitions[behavior])}"
    eq_behaviors = '\n'.join(map(lambda bhv: f"eq {bhv} = b({eq_behaviors_tmp[bhv]}) .", eq_behaviors_tmp.keys()))
    transition_names = ', '.join(transitions.keys())
    behavior_names = ', '.join(eq_behaviors_tmp.keys())
    comp = f"eq {name} = < places:{','.join(places)}, initial:{init}, stationPlaces:{', '.join(st_places)}, transitions:({transition_names}), behaviors:({behavior_names}), groupUses:{use_ports}, groupProvides:{provide_ports} > ."
    content = [componentType, place, station, InitialPlace, ProvidePort, usePort, ops_transitions, eq_transitions, ops_behaviors, eq_behaviors, comp]
    return '\n'.join(content)

def __make_instruction(instruction: Instruction):
    if instruction.isAdd():
        return __make_add(instruction)
    if instruction.isCon():
        return __make_con(instruction)
    if instruction.isDel():
        return __make_del(instruction)
    if instruction.isDiscon():
        return __make_dcon(instruction)
    if instruction.isPushB():
        return __make_pushb(instruction)
    if instruction.isWait():
        return __make_wait(instruction)

def __make_add(add: Add):
    return f"add({add.component()},{add.type().name()})"

def __make_del(delete: Delete):
    return f"del({delete.component()})" 

def __make_con(connect: Connect):    
    type_pro = type_of_comp[connect.provider()].name()
    type_use = type_of_comp[connect.user()].name()
    return f"con({connect.user()},{type_use}{cap1(connect.using_port())},{connect.provider()},{type_pro}{cap1(connect.providing_port())})" 
    
def __make_dcon(disconnect: Disconnect):
    type_pro = type_of_comp[disconnect.provider()].name()
    type_use = type_of_comp[disconnect.user()].name()
    return f"dcon({disconnect.user()},{type_use}{cap1(disconnect.using_port())},{disconnect.provider()},{type_pro}{cap1(disconnect.providing_port())})" 

def __make_pushb(pushb: PushB):
    type_comp = type_of_comp[pushb.component()]
    return f"pushB({pushb.component()}, {type_comp.name()}{cap1(pushb.behavior())}, {pushb.id()})" 

def __make_wait(wait: Wait):
    return f"wait({wait.component()}, {wait.behavior()})"
    
def write_maude(filename, content):
    file = filename
    if not filename.endswith(".maude"):
        file = file + ".maude"
    with open(file, 'w') as file:
        file.write(content)
    
# ------------------- 
# Example: Basic
# ------------------- 
    
def smalltype(name="cc22"):
    t = ComponentType(name)
    p1 = t.add_place("p1")
    p2 = t.add_place("p2")
    p3 = t.add_place("p3")
    t.set_initial_place(p1)
    t.set_running_place(p3)
    bhv_deploy = t.add_behavior("deploy")
    bhv_deploy.add_transition("deploy1", p1, p2)
    bhv_deploy.add_transition("deploy2", p2, p3)
    t.add_use_port("us1", {p3})
    t.add_provide_port("pr1", {p3})
    return t

def smallprogram(nodename):
    name = nodename
    Type = smalltype()
    program = Program([
        Add("idc1", Type),
        Add("idc3", Type),
        Connect("idc1", "us1", "idc3", "pr1"),
        PushB("idc1", "deploy", f"{name}Idb2"),
        PushB("idc1", "deploy", f"{name}Idb3")
    ])
    return program


# ------------------- 
# Example: CPS
# ------------------- 

def cps(n):
    programs = cps_deploy_maude(n)
    maude = gen_maude(programs)
    write_maude("example_deploy_cps.maude", maude)
    programs = cps_deploy_update_maude(n)
    maude = gen_maude(programs)
    write_maude("example_deploy_update_cps.maude", maude)

# if __name__ == "__main__":
#     # cps(1)
#     inst = ComponentInstance("myinst", smalltype("x21"))
#     print(gen_maude([smallprogram("test")], [inst], {inst: "P1"}))
   
   
   
   