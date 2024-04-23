from __future__ import annotations

from abc import ABC
from itertools import chain
from typing import Dict, Set, Tuple, Iterable, Any, Union


class Place:

    def __init__(self, name: str, t: ComponentType):
        self._name: str = name
        self._type: ComponentType = t
        self._bound_ports: Dict[str, Port] = {}

    def name(self) -> str:
        return self._name

    def type(self) -> ComponentType:
        return self._type

    def add_bound_port(self, p: Port) -> None:
        assert p.type() == self._type
        assert p.name() not in self._bound_ports
        self._bound_ports[p.name()] = p

    def bound_ports(self) -> Iterable[Port]:
        return self._bound_ports.values()

    def bound_use_ports(self) -> Iterable[Port]:
        return (p for p in self._bound_ports.values() if p.is_use_port())

    def bound_provide_ports(self) -> Iterable[Port]:
        return (p for p in self._bound_ports.values() if p.is_provide_port())

    def __str__(self):
        return self._name


class Port:

    def __init__(self, name: str, t: ComponentType, provide_port: bool, bound_places: Iterable[Place]):
        self._name: str = name
        self._type: ComponentType = t
        self._provide_port: bool = provide_port
        self._bound_places: Set[Place] = set(bound_places)
        for p in bound_places:
            p.add_bound_port(self)

    def name(self) -> str:
        return self._name

    def type(self) -> ComponentType:
        return self._type

    def is_provide_port(self) -> bool:
        return self._provide_port

    def is_use_port(self) -> bool:
        return not self._provide_port

    def is_active(self, active_places: Set[Place]):
        return any(pl in self._bound_places for pl in active_places)

    def bound_places(self) -> Iterable[Place]:
        return self._bound_places

    def is_bound_to(self, p: Place) -> bool:
        assert p in self._type.places()
        return p in self._bound_places

    def __eq__(self, other):
        if isinstance(other, Port):
            return other.name() == self._name
            # and other.is_provide_port() == self._provide_port and other.bound_places() == self._bound_places
        return False

    def __hash__(self):
        return hash(self._type) + hash(self._name) + hash(self._provide_port)


class Transition:

    def __init__(self, src: Place, dst: Place, dock: int = 0, cost: int = 1):
        assert src.type() == dst.type()
        self._src = src
        self._dst = dst
        self._dock = dock
        self._cost = cost

    def source(self) -> Place:
        return self._src

    def cost(self) -> int:
        return self._cost

    def destination(self) -> Tuple[Place, int]:
        return self._dst, self._dock

    def activating_ports(self) -> Iterable[Port]:
        t = self._src.type()
        return (p for p in t.ports() if p.is_bound_to(self._dst) and not p.is_bound_to(self._src))

    def deactivating_ports(self) -> Iterable[Port]:
        t = self._src.type()
        # a port that satsifies the condition could remain active after firing the transition, if there are other
        # active places bound to that port
        return (p for p in t.ports() if p.is_bound_to(self._src) and not p.is_bound_to(self._dst))


class Behavior:

    def __init__(self, name: str, t: ComponentType):
        self._name: str = name
        self._type: ComponentType = t
        self._transitions: Dict[str, Transition] = {}

    def name(self) -> str:
        return self._name

    def type(self) -> ComponentType:
        return self._type

    def add_transition(self, name: str, src: Place, dst: Place, dock: int = 0, cost: int = 1):
        assert name not in self._transitions
        assert src in self._type.places()
        assert dst in self._type.places()
        assert not self._introduces_cycle(src, dst)
        self._transitions[name] = Transition(src, dst, dock, cost)

    def transitions(self) -> Iterable[Transition]:
        return self._transitions.values()

    def transitions_as_dict(self) -> Dict[str, Transition]:
        return self._transitions

    def get_transition(self, name: str) -> Transition:
        if name in self._transitions.keys:
            return self._transitions[name]
        else:
            return None

    def transitions_from(self, src: Place) -> Iterable[Transition]:
        assert src in self._type.places()
        return (tr for tr in self._transitions.values() if tr.source() == src)

    def transitions_to(self, dst: Place, dock: int = 0) -> Iterable[Transition]:
        assert dst in self._type.places()
        return (tr for tr in self._transitions.values() if tr.destination() == (dst, dock))

    def has_transitions_from(self, active_places: Set[Place]) -> bool:
        return any(tr.source() in active_places for tr in self._transitions.values())

    def is_final_place(self, p: Place) -> bool:
        return not any(tr.source() == p for tr in self._transitions.values())

    def _introduces_cycle(self, new_tr_src: Place, new_tr_dst: Place):
        reached: Set[Place] = {new_tr_dst}
        while reached:
            p = reached.pop()
            if p == new_tr_src:
                return True
            for t in self._transitions.values():
                if t.source() == p:
                    reached.add(t.destination()[0])
        return False


class ComponentType:

    def __init__(self, name: str):
        self._name: str = name
        self._behaviors: Dict[name, Behavior] = {}
        self._provide_ports: Dict[str, Port] = {}
        self._use_ports: Dict[str, Port] = {}
        self._places: Dict[str, Place] = {}
        self._running_place: Place = None
        self._initial_place: Place = None

    def name(self):
        return self._name

    def initial_place(self) -> Place:
        return self._initial_place

    def running_place(self) -> Place:
        return self._running_place

    def set_initial_place(self, place: Place):
        assert place in self.places()
        self._initial_place = place

    def set_running_place(self, place: Place):
        assert place in self.places()
        self._running_place = place

    def get_cost(self, name: str, default: int = 0) -> int:
        for bhv in self.behaviors():
            tr = bhv.get_transition(name)
            if tr is not None:
                return tr.cost()
        return default

    def add_behavior(self, name: str) -> Behavior:
        assert name not in self._behaviors
        b = Behavior(name, self)
        self._behaviors[name] = b
        return b

    def add_place(self, name: str) -> Place:
        assert name not in self._places
        p = Place(name, self)
        self._places[name] = p
        return p

    def get_place(self, name: str) -> Place:
        assert name in self._places
        return self._places[name]

    def add_provide_port(self, name: str, bound_places: Iterable[Place]) -> Port:
        assert name not in self._use_ports and name not in self._provide_ports
        assert all(p in self._places.values() for p in bound_places)
        p = Port(name, self, True, bound_places)
        self._provide_ports[name] = p
        return p

    def add_use_port(self, name: str, bound_places: Iterable[Place]) -> Port:
        assert name not in self._provide_ports and name not in self._use_ports
        assert all(p in self._places.values() for p in bound_places)
        p = Port(name, self, False, bound_places)
        self._use_ports[name] = p
        return p

    def provide_ports(self) -> Iterable[Port]:
        res = []
        for name in self._provide_ports:
            res.append(self._provide_ports[name])
        return res

    def use_ports(self) -> Iterable[Port]:
        res = []
        for name in self._use_ports:
            res.append(self._use_ports[name])
        return res

    def ports(self) -> Iterable[Port]:
        return chain(self._provide_ports.values(), self._use_ports.values())

    def get_provide_port(self, name: str) -> Port:
        assert name in self._provide_ports
        return self._provide_ports[name]

    def get_use_port(self, name: str) -> Port:
        assert name in self._use_ports
        return self._use_ports[name]

    def get_port(self, name: str) -> Port:
        if name in self._provide_ports:
            return self._provide_ports[name]
        if name in self._use_ports:
            return self._use_ports[name]
        assert False

    def get_behavior(self, name: str) -> Behavior:
        assert name in self._behaviors
        return self._behaviors[name]

    def behaviors(self) -> Iterable[Behavior]:
        return self._behaviors.values()

    def places(self) -> Iterable[Place]:
        return self._places.values()

    def __eq__(self, other):
        if isinstance(other, ComponentType):
            return self._name == other.name()
        return False

    def __hash__(self):
        return hash(self._name)


class CInstance(ABC):

    def id(self) -> str:
        pass

    def type(self) -> ComponentType:
        pass

    def connections(self, port: Port) -> Iterable[Tuple[Any, Any]]:
        pass

    def isDecentralized(self) -> bool:
        return False

    def neighbors(self) -> Set[str]:
        pass

    def external_port_connection(self, comp: Union[CInstance, str], port: Union[Port, str]) -> str:
        pass


class ComponentInstance(CInstance):

    def __init__(self, identifier: str, t: ComponentType):
        self._id: str = identifier
        self._type: ComponentType = t
        self._connections: Dict[Port, Set[Tuple[ComponentInstance, Port]]] = {p: set() for p in self._type.ports()}
        # For a given port name `pname` from an external component, self._ext_connections[pname] = port, with port a port of self
        self._external_port_connections: Dict[(str, str), Port] = {}

    def id(self) -> str:
        return self._id

    def type(self) -> ComponentType:
        return self._type

    def connections(self, p: Port) -> Iterable[Tuple[ComponentInstance, Port]]:
        assert p in self._connections
        return self._connections[p]
    
    def all_connections(self):
        return self._connections

    def is_connected(self, p: Port) -> bool:
        assert p in self._type.ports()
        return len(self._connections[p]) > 0

    def connect_provide_port(self, provide_port: Port, user: ComponentInstance, use_port: Port) -> None:
        assert provide_port in self._type.provide_ports()
        assert use_port in user._type.use_ports()
        self._connections[provide_port].add((user, use_port))
        self._external_port_connections[(user.id(), use_port.name())] = provide_port

    def connect_use_port(self, use_port: Port, provider: ComponentInstance, provide_port: Port) -> None:
        assert use_port in self._type.use_ports()
        assert provide_port in provider._type.provide_ports()
        # a use port should only be connected to one provider
        assert not self._connections[use_port]
        self._connections[use_port].add((provider, provide_port))
        self._external_port_connections[(provider.id(), provide_port.name())] = use_port

    def neighbors(self) -> Set[str]:
        res = set()
        for connections in self._connections.values():
            res = res | set(map(lambda t: t[0].id(), connections))
        return res

    def external_port_connection(self, comp: Union[CInstance, str], port: Union[Port, str]) -> str:
        ext_portname = port.name() if isinstance(port, Port) else port
        ext_compname = comp.id() if isinstance(comp, CInstance) else comp
        if (ext_compname, ext_portname) in self._external_port_connections.keys():
            return self._external_port_connections[(ext_compname, ext_portname)].name()
        # else:
        return None

    def __eq__(self, other):
        if not isinstance(other, ComponentInstance):
            return False
        else:
            return self.id() == other.id() and self.type() == other.type()

    def __hash__(self):
        return hash(self._id) + hash(self._type)


class IAssembly(ABC):

    def add_instance(self, instance_id: str, t: ComponentType) -> CInstance:
        pass

    def get_instance(self, identifier: str) -> CInstance:
        pass

    def instances(self) -> Iterable[CInstance]:
        pass

    def connect_instances_id(self, provider_id: str, provide_port_name: str, user_id: str, use_port_name: str):
        pass


class Assembly(IAssembly):

    def __init__(self):
        self._instances: Dict[str, ComponentInstance] = {}

    def add_instance(self, instance_id: str, t: ComponentType) -> ComponentInstance:
        assert instance_id not in self._instances
        c = ComponentInstance(instance_id, t)
        self._instances[instance_id] = c
        return c

    def connect_instances(self,
                          provider: ComponentInstance,
                          provide_port: Port,
                          user: ComponentInstance,
                          use_port: Port) -> None:
        assert provider in self._instances.values()
        assert provide_port.is_provide_port()
        assert user in self._instances.values()
        assert use_port.is_use_port()
        provider.connect_provide_port(provide_port, user, use_port)
        user.connect_use_port(use_port, provider, provide_port)

    def connect_instances_id(self,
                             provider_id: str,
                             provide_port_name: str,
                             user_id: str,
                             use_port_name: str) -> None:
        provider = self.get_instance(provider_id)
        user = self.get_instance(user_id)
        provide_port = provider.type().get_provide_port(provide_port_name)
        use_port = user.type().get_use_port(use_port_name)
        self.connect_instances(provider, provide_port, user, use_port)

    def get_instance(self, identifier: str) -> CInstance:
        assert identifier in self._instances
        return self._instances[identifier]

    def instances(self) -> Iterable[CInstance]:
        return self._instances.values()
    

class Instruction(ABC):

    def isWait(self):
        return False

    def isPushB(self):
        return False

    def isAdd(self):
        return False

    def isDel(self):
        return False

    def isCon(self):
        return False

    def isDiscon(self):
        return False


class Add(Instruction):

    def __init__(self, component: str, component_type: ComponentType):
        self._comp = component
        self._ctype = component_type

    def isAdd(self):
        return True

    def component(self):
        return self._comp

    def type(self):
        return self._ctype

    def triplet(self) -> (str, str, str):
        return 'add', self._comp, self._ctype.name()

    def __str__(self):
        return f"add({self._comp}, {self._ctype.name()})"

    def __eq__(self, other):
        if isinstance(other, Add):
            return other.component() == self.component() and other.type() == self.type()
        return False

    def __hash__(self):
        return hash('add') + hash(self._comp) + hash(self._ctype)


class Delete(Instruction):

    def __init__(self, component: str):
        self._comp = component

    def isDel(self):
        return True

    def component(self):
        return self._comp

    def duet(self) -> (str, str, str):
        return 'del', self._comp

    def __str__(self):
        return f"del({self._comp})"

    def __eq__(self, other):
        if isinstance(other, Delete):
            return other.component() == self.component()
        return False

    def __hash__(self):
        return hash('delete') + hash(self._comp)


class Connect(Instruction):

    def __init__(self, provider: str, providing_port: str, user: str, using_port: str):
        self._provider = provider
        self._providing_port = providing_port
        self._user = user
        self._using_port = using_port

    def isCon(self):
        return True

    def provider(self):
        return self._provider

    def user(self):
        return self._user

    def providing_port(self):
        return self._providing_port

    def using_port(self):
        return self._using_port

    def quintet(self):
        return 'connect', self._provider, self._providing_port, self._user, self._using_port

    def __str__(self):
        return f"connect({self._provider}, {self._providing_port}, {self._user}, {self._using_port})"

    def __eq__(self, other):
        if isinstance(other, Connect):
            return other.provider() == self.provider() and other.providing_port() == self.providing_port() \
                   and other.user() == self.user() and other.using_port() == self.using_port()
        return False

    def __hash__(self):
        return hash('connect') + hash(self._provider) + hash(self._providing_port) \
               + hash(self._using_port) + hash(self._user)


class Disconnect(Instruction):

    def __init__(self, provider: str, providing_port: str, user: str, using_port: str):
        self._provider = provider
        self._providing_port = providing_port
        self._user = user
        self._using_port = using_port

    def isDiscon(self):
        return True

    def provider(self):
        return self._provider

    def user(self):
        return self._user

    def providing_port(self):
        return self._providing_port

    def using_port(self):
        return self._using_port

    def quintet(self):
        return 'disconnect', self._provider, self._providing_port, self._user, self._using_port

    def __str__(self):
        return f"disconnect({self._provider}, {self._providing_port}, {self._user}, {self._using_port})"

    def __eq__(self, other):
        if isinstance(other, Disconnect):
            return other.provider() == self.provider() and other.providing_port() == self.providing_port() \
                   and other.user() == self.user() and other.using_port() == self.using_port()
        return False

    def __hash__(self):
        return hash('disconnect') + hash(self._provider) + hash(self._providing_port) \
               + hash(self._using_port) + hash(self._user)


class Wait(Instruction):

    def __init__(self, component: str, behavior: str):
        self._component = component
        self._behavior = behavior

    def component(self) -> str:
        return self._component

    def behavior(self) -> str:
        return self._behavior

    def triplet(self) -> (str, str, str):
        return 'wait', self._component, self._behavior

    def isWait(self):
        return True

    def __str__(self):
        return f"wait({self._component}, {self._behavior})"

    def __eq__(self, other):
        if isinstance(other, Wait):
            return other.behavior() == self.behavior() and other.component() == self.component()
        return False

    def __hash__(self):
        return hash('wait') + hash(self._behavior) + hash(self._component)


class PushB(Instruction):

    def __init__(self, component: str, behavior: str, id: str):
        self._component = component
        self._behavior = behavior
        self._idbhv = id

    def component(self) -> str:
        return self._component

    def behavior(self) -> str:
        return self._behavior
    
    def id(self) -> str:
        return self._idbhv

    def triplet(self) -> (str, str, str, str):
        return 'pushB', self._component, self._behavior, self._idbhv

    def isPushB(self):
        return True

    def __str__(self):
        return f"pushB({self._component}, {self._behavior}, {self._idbhv})"

    def __eq__(self, other):
        if isinstance(other, PushB):
            return other.behavior() == self.behavior() and other.component() == self.component()
        return False

    def __hash__(self):
        return hash('pushb') + hash(self._behavior) + hash(self._component)


class Program:
    
    def __init__(self, instructions) -> None:
        self.__instructions = instructions
        
    def __str__(self):
        return f"[{' '.join(str(self.__instructions))}]"
        
    def instructions(self):
        return self.__instructions