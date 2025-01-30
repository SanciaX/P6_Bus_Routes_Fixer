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
        for line in mod_lines:
            if collect_items:
                elements_insert.append(line)
            elif line in elements_to_find:
                elements_to_find.remove(line)
                if not elements_to_find:
                    collect_items = True
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
        #elements_to_find = [
            #'* Table: Time profile items (Element inserted)\n',
            #'* \n',
            #'$+TIMEPROFILEITEM:LINENAME;LINEROUTENAME;DIRECTIONCODE;TIMEPROFILENAME;NODENO;STOPPOINTNO;TRAVERSAL;ALIGHT;BOARD;PRERUNTIME;STOPTIME;NUMFAREPOINTS;NUMFAREPOINTSBOARD;NUMFAREPOINTSTHROUGH;NUMFAREPOINTSALIGHT;ADDVAL;JOURNEYTIMESSTRINGAM;JOURNEYTIMESSTRINGIP;JOURNEYTIMESSTRINGPM;JT_AM;JT_IP;JT_PM;TCUR_BUS\n',
        #]
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
                            elements_insert = elements_insert[1:]
                        else:
                            insert_next = False
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
                                elements_insert = elements_insert[1:]
                                break
                    if len(elements_insert) == 1:
                        parts = elements_insert[0].split(';')
                        parts_ordered = parts[:5] + parts[8:]
                        fw.writelines(';'.join(parts_ordered) + '\n')
                        parts_ordered = parts[:3] + parts[6:]
                        fw.writelines(';'.join(parts_ordered) + '\n')

        # elements changed
        with open(route_added_transfer_file_temp, "r") as fp:
            transfer_lines = fp.readlines()
        with open(route_added_transfer_file_temp, "w") as fw:
            for line in transfer_lines:
                for element in elements_changed:
                    part_element = element.split(';')
                    if ';'.join(part_element[:5]) in line:
                        part_line = line.split(';')
                        part_line[:6] = part_element[:6]
                        part_line[7] = part_element[6]
                        line = ';'.join(part_line)
                fw.writelines(line)

        # timeprofiles
        start_insert = False
        insert_next = False
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
            element_short = parts[4]
            stops.append(element_short)
        stops = [stop for stop in stops if stop != '']

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
        def extract_5th_to_6th(string):
            p = string.split(';')
            return p[5] if len(p) > 5 else None
        #def extract_4th(string):
            #p = string.split(';')
            #return p[4] if len(p) > 5 else None
        # Create a dictionary mapping the extracted characters to the corresponding strings
        timeprofile_map = {extract_5th_to_6th(tp): tp for tp in timeprofile}
        #routeitem_map = {extract_4th(tp): tp for tp in timeprofile}
        # Reorder timeprofile based on the sequence of stops
        reordered_timeprofile = [timeprofile_map[stop] for stop in stops if stop in timeprofile_map]

        change_start = False
        change_firstline = False
        change_stop = False

        with open(route_added_transfer_file_temp, "w") as fw:
            for line in transfer_lines:
                if 'Table: Time profile items (inserted)' in line:
                    change_start = True
                    fw.writelines(line)
                elif change_start and not change_firstline:
                    fw.writelines(line)
                elif change_start and '$+TIMEPROFILEITEM:' in line and not change_firstline:
                    change_firstline = True
                    fw.writelines(line)
                elif change_start and change_firstline:
                    for i in reordered_timeprofile:
                        fw.writelines(i + '\n')
                    if line == '\n':
                        change_start = False
                        change_firstline = False
                        fw.writelines(line)
                if change_start == False and change_firstline == False:
                    fw.writelines(line)
        return timeprofile

    def fix_routes(self, nodes_removal_list, chains, file_read):
        for chain in chains:
            line_start = []
            first, second, *middle, last = chain  # first being the route id
        with open(file_read, "r") as fp:
            lines = fp.readlines()
        with open(file_read, "w") as fw:
            start_idx = end_idx = -1
            # Identify the rows containing str1 and str2, and str1 and str3
            for idx, line in enumerate(lines):
                if str(first) in line and str(second) in line:
                    start_idx = idx
                elif str(first) in line and str(last) in line:
                    end_idx = idx
                    break
                #line = line.strip()
            # Write lines up to the start index
            for i in range(start_idx + 1):
                fw.write(lines[i])

            # Insert new rows based on the `middle` list
            try:
                for mid in middle:
                    parts = line.split(';')
                    parts[7] = '0.000km'
                    parts[3] = str(mid)
                    new_line = ';'.join(parts)
                    fw.write(new_line)
            except:
                pass

            # Write lines from the end index
            for i in range(end_idx, len(lines)):
                fw.write(lines[i])

    def fix_profile(self,route_added_transfer_file_temp, timeprofile):
        # timeprofiles
        seen = set()
        timeprofile = [x for x in timeprofile if not (x in seen or seen.add(x))]
        start_insert = False
        insert_next = False
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
            element_short = parts[4]
            stops.append(element_short)
        stops = [element for element in stops if element != '']

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

        timeprofile_map = {extract_5th_to_6th(tp): tp for tp in timeprofile}

        reordered_timeprofile = [timeprofile_map[stop] for stop in stops if stop in timeprofile_map]


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
