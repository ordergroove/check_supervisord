#!/usr/bin/env python2.7
"""Supervisord status checker"""

import sys
import argparse
import subprocess


class NagiosPlugin(object):
    """Nagios Plugin base class"""

    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self, warning, critical, *args, **kwargs):
        self.warning = warning
        self.critical = critical

    def run_check(self):
        raise NotImplementedError

    def ok_state(self, msg):
        print "OK - {}".format(msg)
        sys.exit(self.OK)

    def warning_state(self, msg):
        print "WARNING - {}".format(msg)
        sys.exit(self.WARNING)

    def critical_state(self, msg):
        print "CRITICAL - {}".format(msg)
        sys.exit(self.CRITICAL)

    def unknown_state(self, msg):
        print "UNKNOWN - {}".format(msg)
        sys.exit(self.UNKNOWN)


class SupervisordServiceCheck(NagiosPlugin):
    CHECK_CMD = ['service', 'supervisord', 'status']

    def __init__(self):
        super(SupervisordServiceCheck, self).__init__(None, None)

    def run_check(self):
        try:
            subprocess.check_output(self.CHECK_CMD)
        except subprocess.CalledProcessError:
            self.critical_state("Supervisord service not running")


class SupervisordProcessCheck(NagiosPlugin):
    CHECK_CMD = ['supervisorctl', 'status']

    supervisor_states = {
        NagiosPlugin.OK: ['STOPPED', 'RUNNING'],
        NagiosPlugin.WARNING: ['STOPPING', 'STARTING'],
        NagiosPlugin.CRITICAL: ['EXITED', 'BACKOFF', 'FATAL', 'UNKNOWN']
    }

    def __init__(self, process_names=None, warning=supervisor_states[NagiosPlugin.WARNING],
                 critical=supervisor_states[NagiosPlugin.CRITICAL]):
        super(SupervisordProcessCheck, self).__init__(warning, critical)
        self.process_names = process_names
        self._process_status = {}

    def run_check(self):
        try:
            status_output = subprocess.check_output(self.CHECK_CMD)
            is_warning, is_critical = False, False
            for line in status_output.strip().split('\n'):
                process_name, proc_status = line.split()[0], line.split()[1]
                if not self.process_names or (self.process_names and process_name in self.process_names):
                    self._process_status[process_name] = proc_status
                    is_critical |= proc_status in self.critical
                    is_warning |= proc_status in self.warning
            if is_critical:
                self.critical_state(self._get_msg())
            if is_warning:
                self.warning_state(self._get_msg())
        except subprocess.CalledProcessError:
            self.unknown_state('Unable to get process status')

    def _get_msg(self):
        msg = ''
        for proc_name, proc_status in self._process_status.items():
            if proc_status not in self.supervisor_states[NagiosPlugin.OK]:
                msg += '{} is {}\n\t'.format(proc_name, proc_status)
        return msg


def main():
    parser = argparse.ArgumentParser(description='Supervisord server and process status checker')
    parser.add_argument('-p', '--process-names', dest='proc_names', nargs='+', default=None,
                        help="Space separated names of processes as they appear in supervisorctl status")

    args = parser.parse_args()

    ssc = SupervisordServiceCheck()
    ssc.run_check()
    spc = SupervisordProcessCheck(args.proc_names)
    spc.run_check()
    spc.ok_state("Service and all processes running")


if __name__ == '__main__':
    main()