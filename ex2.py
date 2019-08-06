import time
import pexpect
import re
class SshTimeoutException(Exception):
    print('Timeout')

class SshManager:
    def __init__(self,serv_address,user,password):
        self.tn = pexpect.spawn(f"ssh {user}@{serv_address}")
        time.sleep(1)
        self.prompt=r"/\$\s*$"
        expect_vals = [pexpect.TIMEOUT,
                        r"[Pp]assword",
                        r"\(yes/no\)\?",
                        self.prompt,
                        pexpect.EOF]

        connect_timeout = 60
        retried = False
        end_timeout = time.time() + connect_timeout
        #conditia este ca sa nu dureze mai mult de un minut.
        while True and time.time() < end_timeout:

            result = self.tn.expect(expect_vals,timeout=5)
            if result == 0:
                raise SshTimeoutException("TIMEOUT")
                #try..expect, iese de tot 
            if result == 1:
                self.tn.sendline(password)
                time.sleep(1)
                continue
            if result == 2:
                self.tn.sendline("yes")
                time.sleep(1)
                continue
            if result == 3:
                print('Connected')
                break
            if result == 4:
                #ne reconectam
                if retried:
                    print('BUG')
                    break
                else:
                   retried = True
                   self.tn = pexpect.spawn(f"ssh {user}@{serv_address}")


    def exec_command(self,cmd):
        
        self.tn.send(f"{cmd}\r\n")
        time.sleep(1)
        self.tn.expect(self.prompt,timeout=5)
        output = self.tn.before
        output = output.decode("utf-8") 
        lines = output.split("\r\n")
        lines = lines[1:-1]
        #if cmd in lines[0]:
            #lines=line
        #for line in lines:
        #   print(line)       
        output = "\n".join(lines)
        return output

    def list_directory(self):
        output = self.exec_command("ls -l")
        patt = r"(\w+\.?\w+)$"
        list_of_files = []
        for line in output.split("\n"):
            #import code; code.interact(local = locals())
            out = re.search(patt,line)
            if out:
                list_of_files.append(out.group())
        
        return list_of_files
ssh = SshManager("test.rebex.net","demo","password")
#print(ssh.exec_command("ls -l"))
print(ssh.list_directory())
