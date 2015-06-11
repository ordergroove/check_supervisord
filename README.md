# check_supervisord

A Nagios NRPE plugin written in Python to monitor Supervisord server and processes controlled by it.

## Requirements
- Python 2.7
- Functioning NRPE setup
  - http://www.tecmint.com/how-to-add-linux-host-to-nagios-monitoring-server/ for instructions

## Installation
- Copy check_supervisord.py to /usr/local/nagios/libexec/
- ```chmod u+x /usr/local/nagios/libexec/check_supervisord.py```
- ```chown nagios:nagios /usr/local/nagios/libexec/check_supervisord.py```
- Add command to *nrpe.cfg*:
  - ```command[check_supervisord]=/usr/bin/sudo /usr/local/nagios/libexec/check_supervisord.py```
- Allow nagios user to run the check with sudo without requiring a password
  - Use ```visudo``` command to edit */etc/sudoers* and add following:
```
    Defaults:nagios !requiretty
    nagios    ALL=(ALL)   NOPASSWD:/usr/local/nagios/libexec/check_supervisord.py
```

## Command Line Parameters
- --process-names - [*optional*] - Space separated names of processes to check.  Names should be as they appear in supervisorctl status. If unspecified, all managed processes will be checked.

## Example Usage

As standalone:
```
[user@host ~]# sudo ./check_supervisord.py --process-names crashmail queue_consumers:cart_log_consumers
Redirecting to /bin/systemctl status  supervisord.service
CRITICAL - queue_consumers:cart_log_consumers is FATAL
```

As NRPE plugin:
```
[user@host libexec]# ./check_nrpe -H localhost -c check_supervisord
OK - Service and all processes running
```

### Sample services.cfg
```
define service{
    use                 generic-service
    hostgroup_name	    supervisord_hosts
    service_description Check Supervisord
    check_command	    check_nrpe!check_supervisord
}
```


License
=======
The MIT License (MIT)

Copyright (c) 2015 OrderGroove

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
