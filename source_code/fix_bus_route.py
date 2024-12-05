########################################################
## Section 2.8: Fix bus route in the transfer file
class FixBusRoute:
    def __init__(self,):
        self.word3 = '$+LINEROUTEITEM'  # Start
        self.word4 = '$+TIMEPROFILE'  # end
    def fix_routes(self, nodes_removal_list, chains, file_read, file_write):
        with open(file_write, "w") as fw, open(file_read, "r") as fp:
            lines = fp.readlines()
            inside_block = False
            new_lines = []

            for i, line in enumerate(lines):
                line = line.strip()
                if self.word3 in line:
                    inside_block = True
                elif self.word4 in line:
                    inside_block = False
                new_lines.append(line)

                if inside_block and i < len(lines) - 1:
                    next_line = lines[i + 1].strip()
                    if any(node in line for node in nodes_removal_list):
                        continue

                    for chain in chains:
                        first, second, *middle, last = chain
                        if (
                            str(first) in line
                            and str(second) in line
                            and str(first) in next_line
                            and str(last) in next_line
                        ):
                            new_lines.append(next_line)
                            for mid in middle:
                                new_lines.append(next_line.replace(str(last), str(mid)))
                            i += 1

            fw.write("\n".join(new_lines))