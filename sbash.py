#!/usr/bin/env python

import argparse
import os
import vars

parser = argparse.ArgumentParser(description='Generate srun command')
parser.add_argument('--n-gpus', type=int, required=True)
parser.add_argument('--n-cpus', type=int, default=None)
parser.add_argument('--account', type=str, default="overcap", choices=vars.accounts)
parser.add_argument('--node', type=str, default=None)
parser.add_argument('--gpu-types', type=str, nargs='+', default=["rtx_6000", "2080_ti", "a40"], choices=vars.gpu_types)
parser.add_argument('--blacklist', type=str, nargs='+', default=None)
args = parser.parse_args()

# num GPUs
command = [f"srun --gres=gpu:{args.n_gpus} --account={args.account}"]
# GPU types
if args.gpu_types is not None:
    args.gpu_types = "|".join(args.gpu_types)
    command.append(f"--constraint=\'{args.gpu_types}\'")
# num CPUs
if args.n_cpus is None:
    args.n_cpus = args.n_gpus * 7
command.append(f"-c {args.n_cpus}")
# partition
partition = "long" if args.account == "kira-lab" else "overcap"
command.append(f"-p {partition}")
# blacklist
blacklist = vars.blacklist
if args.blacklist is not None:
    blacklist.extend(args.blacklist)
blacklist = ",".join(blacklist)
command.append(f"-x {blacklist}")
# node
if args.node is not None:
    command.append(f"-w {args.node}")

command.append("--pty bash -i")
command = " ".join(command)
print(command)
os.system(command)
