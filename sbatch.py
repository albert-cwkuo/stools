#!/usr/bin/env python

import argparse
import tempfile
import subprocess
from pathlib import Path
import shutil

import vars


parser = argparse.ArgumentParser(description='Generate srun command')
parser.add_argument('--n-gpus', type=int, required=True)
parser.add_argument('--n-cpus', type=int, default=None)
parser.add_argument('--account', type=str, default="overcap", choices=vars.accounts)
parser.add_argument('--node', type=str, default=None)
parser.add_argument('--gpu-types', type=str, nargs='+', default=["rtx_6000", "2080_ti", "a40"], choices=vars.gpu_types)
parser.add_argument('--blacklist', type=str, nargs='+', default=None)
parser.add_argument('--env', type=str, default=None)
parser.add_argument('--logdir', type=str, default="run/")
parser.add_argument('--command', type=str, required=True)
args = parser.parse_args()

f = tempfile.NamedTemporaryFile(mode='w+t')
args.logdir = Path(args.logdir)/Path(f.name).name
shutil.rmtree(args.logdir, ignore_errors=True)
args.logdir.mkdir(parents=True, exist_ok=True)

f.write("#!/bin/bash\n")
f.write(f"#SBATCH\n")

# output log
f.write(f"#SBATCH -o {str(args.logdir/'log')}\n")

# num GPUs
f.write(f"#SBATCH --gres=gpu:{args.n_gpus}\n")

# account
f.write(f"#SBATCH --account {args.account}\n")

# GPU types
args.gpu_types = "|".join(args.gpu_types)
f.write(f"#SBATCH --constraint {args.gpu_types}\n")

# num CPUs
if args.n_cpus is None:
    args.n_cpus = args.n_gpus * 7
f.write(f"#SBATCH -c {args.n_cpus}\n")

# partition
partition = "long" if args.account == "kira-lab" else "overcap"
f.write(f"#SBATCH -p {partition}\n")

# blacklist
blacklist = vars.blacklist
if args.blacklist is not None:
    blacklist.extend(args.blacklist)
blacklist = ",".join(blacklist)
f.write(f"#SBATCH -x {blacklist}\n")

# node
if args.node is not None:
    f.write(f"#SBATCH -w {args.node}\n")

f.write("hostname\n")

# conda env
if args.env is not None:
    f.write(f"source activate {args.env}\n")

# running command
f.write(f"{args.command}\n")

f.seek(0)
print(f.read())
shutil.copyfile(f.name, args.logdir/"sbatch")
print(f"Job name: {Path(f.name).name}")
subprocess.run(["sbatch", f.name])
f.close()