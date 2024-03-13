from concerto import *
from examples.openstack import *

def __make_port(typename, port, sep_port_bounded="!"):
    bounded = list(map(lambda place: f"{typename}_{place.name()}", port.bound_places()))
    return f"{typename}_{port.name()} {sep_port_bounded} ({', '.join(bounded)})" 

def gen_maude(components, programs):
    res = '\n'.join(map(lambda component: gen_maude_from_component(component), components))
    res += "\n" + '\n'.join(map(lambda program: gen_maude_program(program), programs))
    return res 

def gen_maude_program(program):
    plan = ' . '.join(map(lambda instr: __make_instruction(instr), program.instructions()))
    return f"<(empty, empty), {plan} . [], empty, nil, nil, empty >"

def gen_maude_from_component(compInstance: ComponentInstance):
    return gen_maude_from_type(compInstance.type())

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
        initPlace = f"op {init} : -> InitPlace."
        
    if type.provide_ports():
        proPort = "ops " + ' '.join(map(lambda port: f"{name}_{port.name()}", type.provide_ports())) + " : -> ProPort ."
        provide_ports = ', '.join(map(lambda port: __make_port(name, port, "!"), type.provide_ports()))
        
    if type.use_ports():
        usePort = "ops " + ' '.join(map(lambda port: f"{name}_{port.name()}", type.use_ports())) + " : -> UsePort ."
        use_ports = ', '.join(map(lambda port: __make_port(name, port, "?"), type.use_ports()))
        
    all_transitions = []
    all_behaviors = []
    for behavior in type.behaviors():
        curr_bhv = []
        for transition in behavior.transitions():
            source = f"{name}_{transition.source().name()}"
            dest = dict_place_station[f"{name}_{transition.destination()[0].name()}"]
            all_transitions.append(f"t({source}, {dest})")
            curr_bhv.append(f"t({source}, {dest})")
        all_behaviors.append(f"b({', '.join(curr_bhv)})")
    
    transitions = ', '.join(all_transitions)
    behaviors = ', '.join(all_behaviors)
    
    comp = f"eq {name} = < ({' '.join(places)}), {init}, {', '.join(st_places)}, ({transitions}), ({behaviors}), {provide_ports}, {use_ports} > ."
    
    content = [componentType, place, station, initPlace, proPort, usePort, comp]
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
    return f"add({add.component()},{add.type()})"

def __make_del(delete: Delete):
    return f"del({delete.component()})" 

def __make_con(connect: Connect):    
    # TODO con(_) : Connection -> Instruction .
    # (_,_,_,_) : IdentC UsePort IdentC ProPort -> Connection 
    return f"con()" 
    
def __make_dcon(disconnect: Disconnect):
    # TODO dcon(_) : Connection -> Instruction .
    # (_,_,_,_) : IdentC UsePort IdentC ProPort -> Connection 
    return f"dcon()" 

def __make_pushb(pushb: PushB):
    # TODO pushB(_,_,_) : IdentC Behavior IdentB -> Instruction .
    return f"pushB()" 

def __make_wait(wait: Wait):
    # transitions_from_behavior[wait.behavior()] = 
    # return f"wait({wait.component()},{})"
    return "wait()" # TODO
    
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
    return t

def smallprogram():
    program = Program([
        Add("idc1", "cc22"),
        Connect("idc1", "us1", "idc3", "pr1"),
        PushB("idc1", "deploy")
    ])
    return program


if __name__ == "__main__":
   small = ComponentInstance("small", smalltype())
#    mariadb = ComponentInstance("mariadb", mariadb_worker_type())
#    maude = gen_maude_from_component(small)
   maude = gen_maude([small], [smallprogram()])
   print(maude)