import paramiko

class SSHConnection(object):
 
    def __init__(self, host_dict):
        self.host = host_dict['host']
        self.port = host_dict['port']
        self.username = host_dict['username']
        self.pwd = host_dict['pwd']
        self.__k = None
 
    def connect(self):
        try:
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.pwd)
            self.__transport = transport
            print('------------认证成功!-----------')
            self.ssh = paramiko.SSHClient()
            self.ssh._transport = self.__transport
        except Exception:
            print(f'连接远程服务器(ip:{self.host})发生异常!请检查用户名和密码是否正确!')
 
    def close(self):
        self.__transport.close()
    
    def cmd(self, command, get_pty=False, sudo=False):
        """
        执行shell命令,返回字典
        get_pty用于执行多个指令，用';'连接
        sudo代表使用sudo命令
        """
        #ssh = paramiko.SSHClient()
        #ssh._transport = self.__transport
        # 多个命令
        if((get_pty==False)&(sudo==False)):
            stdin, stdout, stderr = self.ssh.exec_command(command)
        else:
            stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)
        # 使用sudo
        if(sudo==True):
            stdin.write(self.pwd + '\n')
        # 获取命令结果
        res = stdout.read().decode('utf-8')
        # 获取错误信息
        error = stderr.read().decode('utf-8')
        # 如果有错误信息，返回error
        # 否则返回res
        if error.strip():
            print('error:\n', error)
            return {'color':'red','res':error}
        else:
            print(res)
            return {'color': 'green', 'res':res}

    def upload(self, local_path, target_path):
        # 连接，上传
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # 将location.py 上传至服务器 /tmp/test.py
        sftp.put(local_path, target_path, confirm=True)
        # print(os.stat(local_path).st_mode)
        # 增加权限
        # sftp.chmod(target_path, os.stat(local_path).st_mode)
        sftp.chmod(target_path, 0o755)  # 注意这里的权限是八进制的，八进制需要使用0o作为前缀
 
    def download(self,target_path, local_path):
        # 连接，下载
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # 将location.py 下载至服务器 /tmp/test.py
        sftp.get(target_path, local_path)
 
    # 销毁
    def __del__(self):
        self.close()
 
