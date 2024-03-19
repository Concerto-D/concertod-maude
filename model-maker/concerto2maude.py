from concerto import *
from itertools import chain
from examples.openstack import *
from examples.cps import *

type_of_comp = {}

def __make_port(typename, port, sep_port_bounded="!"):
    bounded = list(map(lambda place: f"{typename}_{place.name()}", port.bound_places()))
    return f"{typename}_{port.name()} {sep_port_bounded} ({', '.join(bounded)})" 

def flatmap(func, iterable):
    return list(chain.from_iterable(map(func, iterable)))

def gen_maude(programs):
    conf_names = list(map(lambda program: f"conf_{program.id()}", programs))
    maude = "ops " + ' '.join(conf_names) + " : ->  LocalConfiguration ."
    adds = flatmap(lambda program: filter(lambda instr: instr.isAdd(), program.instructions()), programs) # Get all add from all programs using flatmap
    types = set()
    for add in adds:
        type_of_comp[add.component()] = add.type()
        types.add(add.type())
    maude += "\nop test : -> Net ."
    maude += "\n" + '\n'.join(map(lambda type: gen_maude_from_type(type), types))
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
    plan = ' . '.join(map(lambda instr: __make_instruction(instr), program.instructions()))
    pushb_instr = filter(lambda instr: instr.isPushB(), program.instructions())
    identB = "ops " + ' '.join(map(lambda instr: f"{instr.id()}", pushb_instr)) + ": -> IdentB ."
    identC = "ops" + ' '.join(list_ids) + " -> IdentC ."
    return identB + '\n' + identC + '\n' + f"eq conf_{program.id()} = <({ids}), (empty, empty), {plan} . [], empty, nil, nil, empty > ."

def gen_maude_from_type(type: ComponentType) -> str:
    name = type.name()
    place, initPlace, station, proPort, usePort = "", "", "", "", ""
    provide_ports = "empty"
    use_ports = "empty"
    componentType = f"op {name} : -> ComponentType ."
    
    if type.places() is not []:
        dict_place_station = {f"{name}_{place.name()}": f"st_{name}_{place.name()}" for place in type.places()}
        places = list(map(lambda place: f"{name}_{place.name()}", type.places()))
        stations = list(map(lambda place: f"st_{name}_{place.name()}", type.places()))
        st_places = list(map(lambda stp: f"{stp[0]} ; {stp[1]}" , zip(places, stations)))
        init = f"{name}_{type.initial_place().name()}"
        place = "ops " + ' '.join(places) + " : -> Place ."
        station = "ops " + ' '.join(stations) + " : -> Station ."
        initPlace = f"op {init} : -> InitPlace ."
        
    if type.provide_ports():
        proPort = "ops " + ' '.join(map(lambda port: f"{name}_{port.name()}", type.provide_ports())) + " : -> ProPort ."
        provide_ports = ', '.join(map(lambda port: __make_port(name, port, "?"), type.provide_ports()))
        
    if type.use_ports():
        usePort = "ops " + ' '.join(map(lambda port: f"{name}_{port.name()}", type.use_ports())) + " : -> UsePort ."
        use_ports = ', '.join(map(lambda port: __make_port(name, port, "!"), type.use_ports()))
        
    behavior_transitions = {}
    transitions = {}
    for behavior in type.behaviors():
        behavior_name = f"{name}_{behavior.name()}"
        behavior_transitions[behavior_name] = []
        for transition in behavior.transitions_as_dict().keys():
            act_transition = behavior.transitions_as_dict()[transition]
            source = f"{name}_{act_transition.source().name()}"
            dest = dict_place_station[f"{name}_{act_transition.destination()[0].name()}"]
            transition_name = f"{name}_{transition}"
            transitions[transition_name] = f"t({source}, {dest})"
            behavior_transitions[behavior_name].append(transition_name)
    
    
    ops_transitions = f"ops {' '.join(transitions.keys())} : -> Transitionn ."
    eq_transitions = '\n'.join(map(lambda tr: f"eq {tr} = {transitions[tr]} .", transitions.keys()))
    ops_behaviors = f"ops {' '.join(behavior_transitions.keys())} : -> Behavior ."
    eq_behaviors_tmp = {}
    for behavior in behavior_transitions.keys():
        eq_behaviors_tmp[behavior] = f"{','.join(behavior_transitions[behavior])}"
    eq_behaviors = '\n'.join(map(lambda bhv: f"eq {bhv} = b({eq_behaviors_tmp[bhv]}) .", eq_behaviors_tmp.keys()))
        
    transition_names = ', '.join(transitions.keys())
    behavior_names = ', '.join(eq_behaviors_tmp.keys())

    comp = f"eq {name} = < ({','.join(places)}), {init}, {', '.join(st_places)}, ({transition_names}), ({behavior_names}), {use_ports}, {provide_ports} > ."
    
    content = [componentType, place, station, initPlace, proPort, usePort, ops_transitions, eq_transitions, ops_behaviors, eq_behaviors, comp]
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
    return f"con({connect.user()},{type_use}_{connect.using_port()},{connect.provider()},{type_pro}_{connect.providing_port()})" 
    
def __make_dcon(disconnect: Disconnect):
    type_pro = type_of_comp[disconnect.provider()].name()
    type_use = type_of_comp[disconnect.user()].name()
    return f"dcon({disconnect.user()},{type_use}_{disconnect.using_port()},{disconnect.provider()},{type_pro}_{disconnect.providing_port()})" 

def __make_pushb(pushb: PushB):
    type_comp = type_of_comp[pushb.component()]
    return f"pushB({pushb.component()}, {type_comp.name()}_{pushb.behavior()}, {pushb.id()})" 

def __make_wait(wait: Wait):
    return f"wait({wait.component()}, {wait.behavior()})"
    
def write_maude(filename, content):
    file = filename
    if not filename.endswith(".maude"):
        file = file + ".maude"
    with open(file, 'w') as file:
        file.write(content)
    
# ------------------- 
# Example
# ------------------- 
    
def smalltype():
    t = ComponentType("cc22")
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

def smallprogram(name):
    Type = smalltype()
    program = Program(name, [
        Add("idc1", Type),
        Add("idc3", Type),
        Connect("idc1", "us1", "idc3", "pr1"),
        PushB("idc1", "deploy", f"{name}_idb2"),
        PushB("idc1", "deploy", f"{name}_idb3")
    ])
    return program

# ------------------- 

if __name__ == "__main__":
    programs = deploy_maude(1)
    maude = gen_maude(programs)
    write_maude("example.maude", maude)
    # maude = gen_maude([smallprogram("n1"), smallprogram("n2")])
    # print(maude)
   