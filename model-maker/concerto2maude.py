import json

def parse(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data

def concerto2maude(content):
    # shorts = {}
    componentType = []
    componentTypeDefinition = []
    places = []
    init_places = []
    station_places = {}
    ports = {"use": [], "provide": []}
    for component in content["components"]:
        comp_place = []
        short = component["short"]
        # shorts[component["name"]] = short
        componentType.append(component["name"])    
        for place in component["places"]:
            place_name = f"{short}_{place}"
            comp_place.append(place_name)
            places.append(place_name)
            station_places[place_name] = place_name # TODO replace place, by its station... what is a station?
            
        for port in component["ports"]:
            ports[port["type"]].append(f"{short}_{port['name']}")
        comp_init_place = f"{short}_{component['start']}"
        init_places.append(comp_init_place)
        # A component type:
        # --- eq {comp_name} = < ({place_1}, .., {places_n}) , {place_init}, ( {station_1};{place_1} , ... ,  {station_n};{place_n} , (t({place_1}, {station_2}), ... , t({place_n}, {station_n'})), (b())  > .
        # eq c11 =  < (p1, p2, p3) , p1 , (s1 ; p1, s2 ; p2, s3 ; p3), (t(p1, s2), t(p2, s3) ), (b(t(p2, s3),t(p1, s2))) , us1 ! (p2), empty   > .
        comp_station_places= map(lambda pl: f"{pl};{station_places[pl]}", places) # TODO 
        cmp_t_def = f"eq {component['name']} = < ({', '.join(comp_place)}) , {comp_init_place}, {', '.join(comp_station_places)} >."
        componentTypeDefinition.append(cmp_t_def)
            
    print(f"ops {' '.join(places)} : -> IdentB.")
    print(f"ops {' '.join(init_places)} : -> InitPlace.")
    
    print(f"ops {' '.join(ports['use'])} : -> UsePort.")
    print(f"ops {' '.join(ports['provide'])} : -> ProPort.")
    joined_ct = f"ops {' '.join(componentType)} : -> ComponentType."
    print(joined_ct)
    joined_ctdef = '\n'.join(componentTypeDefinition)
    print(f"{joined_ctdef}")

        
def json2concerto(filename):
    return concerto2maude(parse(filename))

if __name__ == "__main__":
   #  json2concerto("cps.json")
   pass
