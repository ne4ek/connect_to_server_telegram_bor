import paramiko

def connect_to_server(host_name:str, user_name:str, password: str): 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host_name, username=user_name, password=password)
    except Exception as e:
        raise e
    return ssh


def exit_from_server(ssh: paramiko.SSHClient, channel: paramiko.Channel):
    channel.close()
    ssh.close()


def test():   
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname="212.113.101.20", username="root", password="p75LGqPzMVVe")
    stdin, stdout, stderr = ssh.exec_command("ls")
    print(stdout.read().decode())    
    ssh.close()
   
   
if __name__ == "__main__":
    test()