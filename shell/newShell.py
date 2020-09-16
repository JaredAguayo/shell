#! /usr/bin/env python3

import os, sys, re

    
def execute_command(command):
    for directory in re.split(':',os.environ['PATH']):
        program = "%s/%s" % (directory, command[0])
        print(program)
        try:
            os.execve(program, command,os.environ)
        except FileNotFoundError:
            pass
        except ValueError:
            pass
    os.write(2, ("Command %s not found\n" % command[0]).encode())

def output_redir(command):
    command = command.split()

    rc = os.fork()

    if rc < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(1)
        os.open(command[-1],os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)

        command = command[0:command.index(">")]
        execute_command(command)

        os.write(2, ("Command %s not found\n" % command[0]).encode())
        sys.exit(1)

def pipe(command):
    command = command.split()
    i = command.index('|')
    pipe1 = command[0:i]
    pipe2 = command[i+1:len(command)]

    r,w = os.pipe()

    for f in (r,w):
        os.set_inheritable(f,True)
    pipeChild = os.fork()

    if pipeChild < 0:
        os.write(2,"Fork failed".encode())
        sys.exit(1)

    if pipeChild == 0:
        os.close(1)
        os.dup(w)
        os.set_inheritable(1,True)
        for f in (r,w):
            os.close(f)
            
        command = pipe1

    else:
        os.close(0)
        os.dup(r)
        os.set_inheritable(0,True)
        for f in (r,w):
            os.close(f)

        command = pipe2
        
    execute_command(command)

while(1):
    current_dir = os.getcwd()
    
    command = input('$ ')

    if command == '':
        continue
    
    elif command == 'exit':
        sys.exit(1)
        
    elif command == 'help':
        os.write(1,("help was selected\n").encode())

    elif 'echo' in command:
        command = command.split(' ')
        os.write(1,(command[1] + "\n").encode())
        
    elif command == 'ls':
        dirs = os.listdir(current_dir)
        print('File List')
        print('----------------')
        for file in dirs:
            print(file)
        print('----------------')
    
    elif 'cd' in command:
        if '..' in command:
            change = '..'
        else:
            change = command.split('cd')[1].strip()
        try:
            print(current_dir)
            os.chdir(change)
            current_dir = os.getcwd()
            print(current_dir)
            
        except FileNotFoundError:
            os.write(2,("cd: no such file or directory\n").encode())

    elif command == 'pwd':
        os.write(1,(current_dir + "\n").encode())

    elif '>' in command:
        output_redir(command)

    elif '|' in command:
        pipe(command)
        

    elif '&' in command:
        background = True
        print(background)

    else:
        command = command.split()
        os.write(2,("%s: command not found\n" % command[0]).encode())
