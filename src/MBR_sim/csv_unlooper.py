import csv



def unloop(file, new_file):
    with open(file, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        new_csvfile = open(new_file, "w")
        csvwriter = csv.writer(new_csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        for row in csvreader:
            if ("".join(row))[0] == "#":
                csvwriter.writerow(row)
                continue
            else:
                # get last column element, if it is > 1 then set a repeat
                last_elem = row[-1]
                if last_elem != "" and int(last_elem) > 1:
                    rep = int(last_elem)
                    for i in range(rep):
                        csvwriter.writerow(row)
                else:
                    csvwriter.writerow(row)
                    continue

    
    new_csvfile.close()
    return 0



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Unloops csv\'s to repeat each operation k times')
    parser.add_argument("-f", "--file", help="the path to the csv file to be unrolled", type=str, default="workloads/csv/bert-large.csv")
    args = parser.parse_args()

    file = args.file
    new_file = file[0:file.index(".csv")] + "_unlooped.csv"
    unlooped = unloop(file, new_file)
        