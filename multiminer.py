from __future__ import (absolute_import, division, print_function, unicode_literals, with_statement)
from libtmux.pane import Pane
from libtmux.server import Server
from libtmux.session import Session
from libtmux.window import Window

import fire
import yaml

SESSION_NAME='multiminer'

class MultiMiner(object):
    """ multi miner class 
    
    use session name suffix as the identifier for runner plan

    Command List
        start [planname]        run the corresponding plan, or the default if planname not given
        stop                    stop the miner tmux session

    TMUX commands you might use
        C-b d          detach the current session
        C-b left       go to the next pane on the left
        C-b right      (or one of these other directions)
        C-b up
        C-b down
    """
    
    def __init__(self):

        self.server = Server()
        self.miner_session = None
        self.miner_layout = ''

        # get the miner session if exists.
        # we don't use exact match
        # the session name is like 'multiminer-zen'
        if self.server.has_session(SESSION_NAME, exact=False):
            for sess in self.server.list_sessions():
                if sess['session_name'].startswith(SESSION_NAME):
                    self.miner_session = sess
                    self.miner_layout = sess['session_name'][len(SESSION_NAME)+1:]
                    break

    def _miner_exist(func):
        def _decorator(self, *args, **kwargs):
            if self.miner_session is None:
                print("NO MINER SESSION RUNNING")
                return
            return func(self, *args, **kwargs)
        return _decorator

    @_miner_exist
    def miners(self):
        pass
        
    @_miner_exist
    def stop(self):
        try:
            self.server.kill_session(SESSION_NAME)
            print("MINER STOPPED")
        except:
            # LibTmuxException
            pass

    def start(self, target="default"):
        # load config file
        with open("./config.yaml", 'r') as stream:
            try:
                config = yaml.load(stream)

                # kill all miner sessions
                if self.server.has_session(SESSION_NAME, exact=False):
                    self.server.kill_session(target_session=SESSION_NAME)
                    print("Killing the running miners ...")
                
                # run new session
                self.miner_session = self.server.new_session(
                    session_name=SESSION_NAME + '-' + target,
                    kill_session=True,
                    )

                self._build_layout(target, config)

            except yaml.YAMLError as e:
                print(e)
            except:
                pass
        pass

    def _build_layout(self, target, config):
        
        runner_config = config['runners'][target]

        # we use only one window, the default window
        default_window = self.miner_session.attached_window

        p = None 
        for miner_conf in runner_config:
            device_config = miner_conf['devices']
            if device_config is None or len(device_config) == 0:
                # skip if no or 0 device configed
                continue

            if p is None:
                p = default_window.attached_pane
            else:
                # split the current window for more panes
                p = default_window.split_window(
                    target=p.id,
                    attach=True,
                    start_directory= None,
                    vertical=False
                )
            
            default_window.select_layout('even-horizontal') # default layout
            default_window.server._update_panes()

            wallet_config = config['wallets'][miner_conf['wallet']]
            miner_config = config['miners'][miner_conf['miner']]

            # build cmd
            cmd = self._build_miner_cmd(miner_conf['miner'], wallet_config, miner_config, device_config)
            print(cmd)
            p.send_keys(cmd, suppress_history=True)

        self.server.attach_session(SESSION_NAME)
            
    
    def _build_miner_cmd(self, miner_name, wallet, miner, device):
        cmd = ''
        if miner_name == 'zm':
            # zm --server servername.com --port 1234 --user username -- dev 0 1 2 --time --color
            # TODO: support temperature adaptation
            protocol = ''
            if miner['ssl'] is True:
                protocol = 'ssl://'
            cmd = '%s --server %s%s --port %d --user %s --pass %s --dev %s --time --color' % (miner['location'], protocol, wallet['server'], wallet['port'], wallet['address'], wallet['pass'], " ".join(map(str, device)))
        if miner_name == 'bminer':
            protocol = 'stratum'
            if miner['ssl'] is True:
                protocol = 'stratum+ssl'
            # ./bminer -uri $SCHEME://$USERNAME@$POOL -api 127.0.0.1:1880
            cmd = '%s -uri %s://%s:%s@%s:%s -devices ' % (miner['location'], protocol, wallet['address'], wallet['pass'], wallet['server'], wallet['port'], ",".join(map(str, device)))
        if miner_name == 'ethminer':
            cmd = ''

        return cmd

    
def main():
    fire.Fire(MultiMiner)

if __name__ == '__main__':
    main()


