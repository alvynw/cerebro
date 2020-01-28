import argparse
import json
import subprocess, shlex, os, yaml

def process_input(directory, filename):
    # def f(s, x, start=0):
    #     pos = s.find(x, start)
    #     if pos == -1:
    #         return start-1
    #     return f(s, x, pos+1)

    # split = f(input_filename, "/")
    directory = input_filename[:split]
    filename = input_filename[split+1:-3]
    cmd = "python Input_Data/gen_data.py {} {}".format(directory, filename)
    proc = subprocess.Popen(shlex.split(cmd))
    print "Finished processing input"
    return 


def execute_framework(decision, party_id, program_name):
    root_dir = os.getcwd()
    print "Executing {} framework for program {}".format(decision, program_name)
    proc = None
    if decision == "arithmetic":
        os.chdir("./crypto_backend/SCALE-MAMBA/")
        proc = subprocess.Popen(shlex.split("./Player {} {}".format(party_id, program_name)))
    elif decision == "boolean":
        os.chdir("./crypto_backend/emp-toolkit/emp-agmpc/")
        proc = subprocess.Popen(shlex.split("./bin/run_circuit {} 2000 {} {} {} ".format(party_id, program_name, program_name, program_name)))
    else:
        raise ValueError("Framework {} is not supported as a valid execution backend".format(decision))

    print proc.communicate()[0]
    print "Finished executing {} framework for program {}".format(decision, program_name)
    os.chdir(root_dir)

def process_output(decision, program_name):
    if decision == "boolean":
        proc = subprocess.Popen(shlex.split("python Output_Data/agmpc_output_parser.py {}".format(program_name + "/agmpc.txt.output")))
        print proc.communicate()[0]

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--config", default="config.yaml", type=str, help="Path to the configuration file")
    parser.add_argument("--plan", type=str, default="mpc_exec_plan", dest="plan_file", help="""Path to the file with the plan; default file is "./mpc_exec_plan" """)

    args = parser.parse_args()
    plan_file = args.plan_file

    config_file = open(args.config, 'r')
    config_data = yaml.load(config_file.read())
    config_file.close()
    config = yaml.dump(config_data)
    
    party_id = config["party_id"]
    program_dir = config["program_dir"]
    program_name = config["program_name"]
    input_dir = config["input_dir"]

    f = open(plan_file, 'r')
    plan_json = f.read()
    f.close()
    plan = json.loads(plan_json)

    decision = plan["decision"]
    
    process_input(input_dir, program_name)
    execute_framework(decision, party_id, program_name)
    process_output(decision, program_name)

if __name__ == "__main__":
    main()