#!/usr/bin/env python3

'''
OPS445 Assignment 2 - summer 2026
Program: assignment2.py
Author: "Kiera Solomon"

The python code in this file is original work written by
"Kiera Solomon". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.

I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Memory Visualiser - Displays memory usage of the system
and processes.

Date: July 24 2026

'''

import argparse
import os, sys


def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."

    parser = argparse.ArgumentParser(
        description="Memory Visualiser -- See Memory Usage Report with bar charts",
        epilog="Copyright 2023"
    )

    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )

    parser.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="Display memory values in human readable format."
    )

    parser.add_argument(
        "program",
        type=str,
        nargs='?',
        help="Show memory use of specified program."
    )

    args = parser.parse_args()

    return args



def percent_to_graph(percent: float, length: int = 20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"

    hashes = int(percent * length)

    spaces = length - hashes

    return "[" + "#" * hashes + " " * spaces + "]"



def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"

    with open("/proc/meminfo", "r") as file:

        for line in file:

            if line.startswith("MemTotal"):

                return int(line.split()[1])

    return 0



def get_avail_mem() -> int:
    "return total memory that is currently available"

    with open("/proc/meminfo", "r") as file:

        for line in file:

            if line.startswith("MemAvailable"):

                return int(line.split()[1])


    mem_free = 0
    swap_free = 0


    with open("/proc/meminfo", "r") as file:

        for line in file:

            if line.startswith("MemFree"):

                mem_free = int(line.split()[1])

            if line.startswith("SwapFree"):

                swap_free = int(line.split()[1])


    return mem_free + swap_free



def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"

    output = os.popen("pidof " + app_name).read()

    if output == "":

        return []

    return output.split()



def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the Resident memory used"

    total_rss = 0


    try:

        with open("/proc/" + proc_id + "/smaps", "r") as file:

            for line in file:

                if line.startswith("Rss:"):

                    total_rss += int(line.split()[1])


    except FileNotFoundError:

        return 0


    return total_rss



def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:

    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']

    suf_count = 0

    result = kibibytes


    while result > 1024 and suf_count < len(suffixes):

        result /= 1024

        suf_count += 1


    return f'{result:.{decimal_places}f} {suffixes[suf_count]}'




if __name__ == "__main__":

    args = parse_command_args()


    total_memory = get_sys_mem()

    available_memory = get_avail_mem()

    used_memory = total_memory - available_memory


    if not args.program:


        percent = used_memory / total_memory


        if args.human_readable:

            memory = (
                bytes_to_human_r(used_memory)
                + "/"
                + bytes_to_human_r(total_memory)
            )

        else:

            memory = str(used_memory) + "/" + str(total_memory)


        print(
            f"Memory         {percent_to_graph(percent,args.length)} "
            f"{percent*100:.0f}% {memory}"
        )


    else:


        pids = pids_of_prog(args.program)

        program_total = 0


        for pid in pids:

            memory = rss_mem_of_pid(pid)

            program_total += memory

            percent = memory / total_memory


            if args.human_readable:

                output = (
                    bytes_to_human_r(memory)
                    + "/"
                    + bytes_to_human_r(total_memory)
                )

            else:

                output = str(memory) + "/" + str(total_memory)


            print(
                f"{pid:<15}{percent_to_graph(percent,args.length)} "
                f"{percent*100:.0f}% {output}"
            )


        percent = program_total / total_memory


        if args.human_readable:

            output = (
                bytes_to_human_r(program_total)
                + "/"
                + bytes_to_human_r(total_memory)
            )

        else:

            output = str(program_total) + "/" + str(total_memory)


        print(
            f"{args.program:<15}{percent_to_graph(percent,args.length)} "
            f"{percent*100:.0f}% {output}"
        )
