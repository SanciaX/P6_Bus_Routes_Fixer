########################################################
## Section 2.8: Fix bus route in the transfer file
class FixBusRoute:
    def __init__(self,):
        self.word3 = '$+LINEROUTEITEM'  # Start
        self.word4 = '$+TIMEPROFILE'  # end
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
            for mid in middle:
                parts = line.split(';')
                parts[3] = str(mid)
                new_line = ';'.join(parts)
                fw.write(new_line)

            # Write lines from the end index
            for i in range(end_idx, len(lines)):
                fw.write(lines[i])

