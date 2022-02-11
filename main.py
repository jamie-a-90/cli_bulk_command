import paramiko
import time
import os
import threading

username = input('Username: ')
passw = input('Password: ')
command = input('Command: ')
port = input('Port number: ')

command = '{}\n'.format(command)
node_list = list()
output_file = 'bulk_command_output.txt'
nodes = 'nodes.txt'

global_lock = threading.Lock()

with open(output_file, 'w') as f:
    f.write('')

def run_command(username, passw, command, port, node):
    twrssh = paramiko.SSHClient()
    twrssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    response = os.system('ping -n 1 ' + node)
    if response == 0:
        try:
            twrssh.connect(node, username=username, password=passw, port=int(port))
            session = twrssh.invoke_shell()
            session.send(command)
            time.sleep(10)
            buff = session.recv(65000)
            twrssh.close()
            output = buff.decode('ascii')

            while global_lock.locked():
                time.sleep(0.02)
                continue
            
            global_lock.acquire()
            with open(output_file, 'a') as f:
                f.write('\n\n\n=================== {} ====================\n\n\n'.format(node))
                f.write(str(output))
                f.write('\n\n')
            global_lock.release()

        except:
            return print('Error')
    else:
        while global_lock.locked():
            time.sleep(0.02)
            continue
            
        global_lock.acquire()
        with open(output_file, 'a') as f:
            f.write('\n\n\n=================== {} ====================\n\n\n'.format(node))
            f.write(node = ' is unreachable')
            f.write('\n\n')
        global_lock.release()

with open(nodes, 'r') as f:
    reader = f.readlines()
    for row in reader:
        node_list.append(row.strip('\n'))

for node in node_list:
    node_thread = threading.Thread(target=run_command, args=(username, passw, command, port,  node))
    node_thread.start()




