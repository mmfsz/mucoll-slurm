#!/bin/bash

srun --ntasks=1 --cpus-per-task=16 --mem=32gb --time=08:00:00 --pty bash -c 'module load python && exec bash -i'
