import libtmux
import fire
import sys
import subprocess
import yaml
from termcolor import colored, cprint

SESSION_PREFIX='multiminer-'

class MultiMiner(object):
    """ multi miner class """
    
    def __init__(self):
        self.server = libtmux.Server()
        self.miner_sessions = []
        self._update_miners()

    def _update_miners(self):
        try:
            sessions = self.server.list_sessions()
            for sess in sessions:
                if sess.get('session_name').startswith(SESSION_PREFIX):
                    self.miner_sessions.append(sess)
        except:
            pass

    def _miner_exist(func):
        def _decorator(self, *args, **kwargs):
            if len(self.miner_sessions) == 0:
                cprint("NO MINER RUNNING", 'red', attrs=['bold'], file=sys.stderr)
                return
            return func(self, *args, **kwargs)
        return _decorator

    @_miner_exist
    def miners(self):

        cprint("RUNNING MINERS: ", 'green', attrs=['bold'])
        for sess in self.miner_sessions:
            cprint('\t' + sess.get('session_name')[len(SESSION_PREFIX):], 'green')
        pass
        
    @_miner_exist
    def kill(self, target=None):

        if target:
            for sess in self.miner_sessions:
                if sess.get('session_name')[len(SESSION_PREFIX):] == target:
                    self.server.kill_session(sess.get('session_name'))
                    cprint(target + " KILLED", 'green', attrs=['bold'])
                    return
            cprint(target + " MINER NOT FOUND", 'red', attrs=['bold'])
        else:
            self.server.kill_server()
            cprint("ALL MINERS KILLED", 'red', attrs=['bold'])
    
    def run(self, target="default"):
        # load config file
        with open("./config.yaml", 'r') as stream:
            try:
                config = yaml.load(stream)
                if target not in config:
                    cprint("Run plan ("+target+") not configured", 'red', attrs=['bold'])
                    return
                
                cprint("STARTING MINERS:", 'green', attrs=['bold'])
                for miner_config in config[target]:

                    # run subprocess myself



            except yaml.YAMLError as e:
                print(e)
            except:
                pass
        pass

    # def _zm_config(self, config):
    #     return lambda
    
def main():
    fire.Fire(MultiMiner)

if __name__ == '__main__':
    main()


