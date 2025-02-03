########################################################
## Section 2.8: Fix bus route in the transfer file
from itertools import filterfalse
from turtle import TurtleGraphicsError


class FixBusRoute:
    def __init__(self,):
        self.word3 = '$+LINEROUTEITEM'  # Start
        self.word4 = '$+TIMEPROFILE'  # end
    def adjust_routes(self, error_route_list, error_modification,processed_error_mod_transfer_file,route_added_transfer_file_temp):
        ## delete error routes related lines in error_modification.tra and add new nodes/stops in route_added_transfer_file_temp.tra
        shortened_error_route_list = [' '.join(s.split()[:2]) for s in error_route_list]
        shortened_error_route_list = list(set(shortened_error_route_list))
        # delete error routes related lines in error_modification.tra
        with open(error_modification, "r") as fp:
            mod_lines = fp.readlines()
        with (open(processed_error_mod_transfer_file, "w") as fw):
            for line in mod_lines:
                if any(route in line for route in shortened_error_route_list):
                    pass
                else:
                    fw.write(line)


## Change routeAddedTransferTemp.tra
        # create index from error_modification for adding/deleting lines in routeAddedTransferTemp.tra
        # '* Table: Line route items (Element deleted)
        elements_delete =[]
        elements_to_find = [
            '* Table: Line route items (Element deleted)\n',
            '* \n',
            '$<LINEROUTEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;NODENO;STOPPOINTNO;TRAVERSAL\n',
        ]
        collect_items = False
        for line in mod_lines:
            if collect_items:
                elements_delete.append(line)
            elif line in elements_to_find:
                if not collect_items:
                    elements_to_find.remove(line)
                if not elements_to_find:
                    collect_items = True
            elif line == '\n' and collect_items:
                collect_items = False
        elements_delete = [item.rstrip('\n') for item in elements_delete]
        try:
            elements_delete = elements_delete[:elements_delete.index('')]
        except:
            pass

        # '* Table: Line route items (Element inserted)
        elements_insert =[]
        elements_to_find = [
            '* Table: Line route items (Element inserted)\n',
            '* \n',
            '$>LINEROUTEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;>NODENO;>STOPPOINTNO;>TRAVERSAL;NODENO;STOPPOINTNO;TRAVERSAL;ISROUTEPOINT;POSTLENGTH;ADDVAL;IBUSLENGTH\n',
        ]
        collect_items = False
        start_table = False
        for line in mod_lines:
            if '* Table: Line route items (Element inserted)' in line:
                start_table = True
            elif '$>LINEROUTEITEM:' in line:
                collect_items = True
            elif collect_items and start_table:
                elements_insert.append(line)
            elif line == '\n' and collect_items:
                collect_items = False
        elements_insert = [item.rstrip('\n') for item in elements_insert]
        try:
            elements_insert = elements_insert[:elements_insert.index('')]
        except:
            pass

        # '* Table: Line route items (Element changed)
        elements_changed = []
        elements_to_find = [
            '* Table: Line route items (Element changed)\n',
            '* \n',
            '$*LINEROUTEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;NODENO;STOPPOINTNO;TRAVERSAL;POSTLENGTH\n',
        ]
        collect_items = False
        for line in mod_lines:
            if collect_items:
                elements_changed.append(line)
            elif line in elements_to_find:
                elements_to_find.remove(line)
                if not elements_to_find:
                    collect_items = True
            elif line == '\n' and collect_items:
                collect_items = False
        elements_changed = [item.rstrip('\n') for item in elements_changed]
        try:
            elements_changed = elements_changed[:elements_changed.index('')]
        except:
            pass


        # '* Table: Time profile items (Element inserted)
        # Add time profile items added in ErrorMod
        time_profile = []
        table_start = False
        collect_items = False
        for line in mod_lines:
            if '* Table: Time profile items (Element inserted)' in line:
                table_start = True
            elif table_start and 'TIMEPROFILEITEM:' in line:
                collect_items = True
            elif table_start and collect_items:
                time_profile.append(line)
            elif line == '\n' and collect_items:
                collect_items = False
                table_start = False

        time_profile = [item.rstrip('\n') for item in time_profile]
        try:
            time_profile = time_profile[:elements_changed.index('')]
            time_profile = [item for item in time_profile if item != '']
        except:
            pass

        # add new nodes/stops in route_added_transfer_file_temp.tra
        with open(route_added_transfer_file_temp, "r") as fp:
            transfer_lines = fp.readlines()
        filtered_transfer_lines = [line for line in transfer_lines if
                                   not any(delete_str in line for delete_str in elements_delete)]
        # Write the filtered lines back to the file or use as needed
        with open(route_added_transfer_file_temp, "w") as fw:
            fw.writelines(filtered_transfer_lines)

        with open(route_added_transfer_file_temp, "r") as fp:
            transfer_lines = fp.readlines()

        start_insert = False
        insert_next = False
        with open(route_added_transfer_file_temp, "w") as fw:
            for line in transfer_lines:
                fw.writelines(line)
                for i in range(len(elements_insert)-1):
                    parts = elements_insert[0].split(';')
                    element_short = ';'.join(parts[:5])
                    if element_short in line and not start_insert and not insert_next:
                        start_insert = True
                        if elements_insert[0].split(';')[1] == elements_insert[0+1].split(';')[1] and ((elements_insert[0].split(';')[6] == elements_insert[0+1].split(';')[3] and elements_insert[0].split(';')[6] != '') or (elements_insert[0].split(';')[7] == elements_insert[0+1].split(';')[4] and elements_insert[0].split(';')[7] != '')):
                            insert_next = True
                        else:
                            insert_next = False
                            parts_ordered = parts[:3] + parts[6:]
                            fw.writelines(';'.join(parts_ordered) + '\n')
                        elements_insert = elements_insert[1:]
                    elif not element_short in line and start_insert:
                        if insert_next:
                            parts_ordered = parts[:5] + parts[8:]
                            fw.writelines(';'.join(parts_ordered) + '\n')
                            if elements_insert[0].split(';')[1] == elements_insert[0+1].split(';')[1] and ((elements_insert[0].split(';')[6] == elements_insert[0+1].split(';')[3] and elements_insert[0].split(';')[6] != '') or (elements_insert[0].split(';')[7] == elements_insert[0+1].split(';')[4] and elements_insert[0].split(';')[7] != '')):
                                insert_next = True
                                elements_insert = elements_insert[1:]
                            else:
                                insert_next = False
                                start_insert = False
                                parts_ordered = parts[:3] + parts[6:]
                                fw.writelines(';'.join(parts_ordered) + '\n')
                                elements_insert = elements_insert[1:]
                                break
                        else:
                            parts_ordered = parts[:3] + parts[6:]
                            fw.writelines(';'.join(parts_ordered) + '\n')
                if len(elements_insert)==1:
                    parts = elements_insert[0].split(';')
                    parts_ordered = parts[:5] + parts[8:]
                    fw.writelines(';'.join(parts_ordered) + '\n')
                    parts_ordered = parts[:3] + parts[6:]
                    fw.writelines(';'.join(parts_ordered) + '\n')
                    elements_insert =[]

        # elements changed
        with open(route_added_transfer_file_temp, "r") as fp:
            transfer_lines = fp.readlines()
        with open(route_added_transfer_file_temp, "w") as fw:
            for line in transfer_lines:
                for element in elements_changed:
                    part_element = element.split(';')
                    if (';'.join(part_element[:5])+';') in line:
                        part_line = line.split(';')
                        part_line[:6] = part_element[:6]
                        part_line[7] = part_element[6]
                        line = ';'.join(part_line)
                fw.writelines(line)

        # timeprofiles
        with open(route_added_transfer_file_temp, "r") as fp:
            transfer_lines = fp.readlines()

        elements = [] # route items elements for indexing the stops along the routes
        elements_to_find = [
            '* Table: Line route items (inserted)\n',
            '* \n',
            '$+LINEROUTEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;NODENO;STOPPOINTNO;TRAVERSAL;ISROUTEPOINT;POSTLENGTH;ADDVAL;IBUSLENGTH\n',
        ]
        collect_items = False
        for line in transfer_lines:
            if collect_items:
                elements.append(line)
            elif line in elements_to_find:
                elements_to_find.remove(line)
                if not elements_to_find:
                    collect_items = True
            elif line == '\n' and collect_items:
                collect_items = False
        elements = [item.rstrip('\n') for item in elements]
        try:
            elements = elements[:elements.index('')]
        except:
            pass
        stops = []
        for i in range(len(elements)):
            parts = elements[i].split(';')
            if parts[4] != '':
                element_short = parts[1] + parts[4]
                stops.append(element_short)
        stops = [stop for stop in stops if stop[4:] != '']

        timeprofile = []
        elements_to_find = [
            '* Table: Time profile items (inserted)\n',
            '* \n',
            '$+TIMEPROFILEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;TIMEPROFILENAME;NODENO;STOPPOINTNO;TRAVERSAL;ALIGHT;BOARD;PRERUNTIME;STOPTIME;NUMFAREPOINTS;NUMFAREPOINTSBOARD;NUMFAREPOINTSTHROUGH;NUMFAREPOINTSALIGHT;ADDVAL;JOURNEYTIMESSTRINGAM;JOURNEYTIMESSTRINGIP;JOURNEYTIMESSTRINGPM;JT_AM;JT_IP;JT_PM;TCUR_BUS\n',
        ]
        collect_items = False
        for line in transfer_lines:
            if collect_items:
                timeprofile.append(line)
            elif line in elements_to_find:
                elements_to_find.remove(line)
                if not elements_to_find:
                    collect_items = True
            elif line == '\n' and collect_items:
                collect_items = False
        timeprofile = [item.rstrip('\n') for item in timeprofile]
        try:
            timeprofile = timeprofile[:timeprofile.index('')]
        except:
            pass
        timeprofile.extend(time_profile)
        #timeprofile = timeprofile[:-1]
        # Extract the characters between the 5th and 6th semicolons

        def extract_stops(string):
            p = string.split(';')
            return p[1] + p[5] if len(p) > 5 else None
        timeprofile_map = {extract_stops(tp): tp for tp in timeprofile}
        # Reorder timeprofile based on the sequence of stops
        reordered_timeprofile = [timeprofile_map[stop] for stop in stops if stop in timeprofile_map]

        change_start = False
        change_firstline = False

        with open(route_added_transfer_file_temp, "w") as fw:
            for line in transfer_lines:
                if 'Table: Time profile items (inserted)' in line:
                    change_start = True
                    fw.writelines(line)
                elif change_start and 'TIMEPROFILEITEM:' in line and not change_firstline:
                    change_firstline = True
                    fw.writelines(line)
                elif change_start and not change_firstline:
                    fw.writelines(line)
                elif change_start and change_firstline:
                    for i in reordered_timeprofile:
                        fw.writelines(i + '\n')
                    change_start = False
                elif not change_start and change_firstline and line == '\n':
                        change_firstline = False
                        fw.writelines(line)
                elif change_start == False and change_firstline == False:
                    fw.writelines(line)


        with open(route_added_transfer_file_temp, "r") as fp:
            routelines = fp.readlines()
        node_list = []
        start_table = False
        start_record = False
        for line in routelines:
            if 'Table: Line route items (inserted)' in line:
                start_table = True
            elif start_table and '$+LINEROUTEITEM:' in line:
                start_record = True
            elif start_record and line != '\n':
                parts = line.split(';')
                node_list.append((parts[3], parts[1]))
            elif line == '\n' and start_record:
                start_record = False
                start_table = False
        node_list = [node for node in node_list if node[0] != '']
        node_pair_list = []
        turn_pair_list = []
        for i in range(len(node_list)-1):
            node_pair_list.append([node_list[i][0], node_list[i+1][0],node_list[i][1], node_list[i+1][1]])
        for i in range(len(node_list)-2):
            turn_pair_list.append([node_list[i][0], node_list[i+1][0], node_list[i+2][0],node_list[i][1], node_list[i+1][1], node_list[i+2][1]])
        return timeprofile, node_pair_list, turn_pair_list

    def fix_routes(self, nodes_delete_list, search_chains, file_read):
        for i in range(len(search_chains)):
            first, *middle, last = search_chains[i][0]
            first = int(first)
            last = int(last)
            middle = [int(m) for m in middle]
            # 1st 2nd and last nodes
            route = search_chains[i][1]  # route
            with open(file_read, "r") as fp:
                lines = fp.readlines()
            start_add = False
            pause_read = False
            end_add = False
            with open(file_read, "w") as fw:
                start_idx = end_idx = 0
                for line in lines:
                    if route in line and str(first) in line:
                        start_add = True
                        fw.write(line)
                    elif route in line and str(last) in line:
                        end_add = True
                        fw.write(line)
                    elif start_add and not end_add and not pause_read:
                        try:
                            for mid in middle:
                                parts = line.split(';')
                                parts[7] = '0.000km'
                                parts[3] = str(mid)
                                parts[4] = ''
                                new_line = ';'.join(parts)
                                fw.write(new_line)
                        except:
                            pass
                        pause_read = True
                    elif end_add:
                        fw.write(line)
                    elif not start_add:
                        fw.write(line)

        #fix u-turn(s)
        with open(file_read, "r") as fp:
            transfer_lines = fp.readlines()
        start_table = False
        start_record = False
        end_table = False
        nodes = []
        new_lines = []
        for line in transfer_lines:
            if not start_table and 'Table: Line route items (inserted)' in line:
                start_table = True
            elif start_table and '$+LINEROUTEITEM:' in line:
                start_record = True
            elif start_record and line != '\n':
                parts = line.split(';')
                nodes.append([parts[1],parts[3]])
                new_lines.append(line)
            elif line == '\n' and start_record:
                start_record = False
                start_table = False
        delete_list = []

        for i in range(len(nodes)-1):
            for n in range(i,len(nodes)-1):
                if nodes[i] == nodes [n] and i !=n and nodes[i][1] != '':
                    #for j in range(i,n):
                        #nodes.pop(j)
                    for m in list(range(i,n)):
                        delete_list.append(m)
        seen = set()
        delete_idx = []
        for item in delete_list:
            if item not in seen:
                seen.add(item)
                delete_idx.append(item)
        delete_list = delete_idx

        updated_lines = []
        for i in range(len(new_lines)):
            if not i in delete_list:
                updated_lines.append(new_lines[i])

        with open(file_read, "w") as fw:
            start_table = False
            start_record = False
            end_record = False
            for line in transfer_lines:
                if not start_table and not start_record and not 'Table: Line route items (inserted)' in line:
                    fw.write(line)
                elif start_table and '$+LINEROUTEITEM' in line:
                    start_record = True
                    fw.write(line)
                elif start_record and line != '\n':
                    if not end_record:
                        for i in range(len(updated_lines)):
                            fw.write(updated_lines[i])
                    end_record = True
                elif line == '\n' and start_record:
                    start_record = False
                    start_table = False
                    fw.write(line)
                elif not start_table and 'Table: Line route items (inserted)' in line:
                    start_table = True
                    fw.write(line)
                elif start_table and not '$+LINEROUTEITEM' in line:
                    fw.write(line)


    def fix_profile(self,route_added_transfer_file_temp, timeprofile):
        # timeprofiles
        seen = set()
        timeprofile = [x for x in timeprofile if not (x in seen or seen.add(x))]
        with open(route_added_transfer_file_temp, "r") as fp:
            transfer_lines = fp.readlines()

        elements = []
        elements_to_find = [
            '* Table: Line route items (inserted)\n',
            '* \n',
            '$+LINEROUTEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;NODENO;STOPPOINTNO;TRAVERSAL;ISROUTEPOINT;POSTLENGTH;ADDVAL;IBUSLENGTH\n',
        ]
        collect_items = False
        for line in transfer_lines:
            if collect_items:
                elements.append(line)
            elif line in elements_to_find:
                elements_to_find.remove(line)
                if not elements_to_find:
                    collect_items = True
            elif line == '\n' and collect_items:
                collect_items = False
        elements = [item.rstrip('\n') for item in elements]
        try:
            elements = elements[:elements.index('')]
        except:
            pass
        stops = []
        for i in range(len(elements)):
            parts = elements[i].split(';')
            element_short = [parts[1],parts[4]]
            stops.append(element_short)
        stops = [element for element in stops if element[1] != '']

        # timeprofile = timeprofile[:-1]
        # Extract the characters between the 5th and 6th semicolons
        def extract_5th_to_6th(string):
            p = string.split(';')
            return p[5] if len(p) > 5 else None
        seen = set()
        for x in timeprofile:
            if x in seen:
                timeprofile.remove(x)
            else:
                seen.add(x)

        reordered_timeprofile = []
        for i in range(len(stops)):
            for line in timeprofile:
                if stops[i][0] in line and stops[i][1] == line.split(';')[5]:
                    reordered_timeprofile.append(line)
        change_start = False
        change_firstline = False
        change_stop = False
        loop_finish = False
        with open(route_added_transfer_file_temp, "w") as fw:
            for line in transfer_lines:
                if 'Table: Time profile items (inserted)' in line:
                    change_start = True
                    fw.writelines(line)
                elif change_start and not change_firstline and not '$+TIMEPROFILEITEM:' in line:
                    fw.writelines(line)
                elif change_start and '$+TIMEPROFILEITEM:' in line and not change_firstline:
                    change_firstline = True
                    fw.writelines(line)
                elif change_start and change_firstline:
                    if not loop_finish:
                        for i in reordered_timeprofile:
                            fw.writelines(i + '\n')
                    loop_finish = True
                    if line == '\n':
                        change_start = False
                        change_firstline = False
                        fw.writelines(line)
                elif change_start == False and change_firstline == False:
                    fw.writelines(line)

