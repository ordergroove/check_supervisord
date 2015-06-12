import unittest
import mock
import subprocess

from check_supervisord import SupervisordServiceCheck, SupervisordProcessCheck, NagiosPlugin


@mock.patch('check_supervisord.sys')
class TestNagiosPlugin(unittest.TestCase):

    def setUp(self):
        self.plugin_inst = NagiosPlugin(None, None)
        self.msg = "test"

    def test_run_check(self, mock_sys):
        with self.assertRaises(NotImplementedError):
            self.plugin_inst.run_check()

    def test_ok_state(self, mock_sys):
        self.plugin_inst.ok_state(self.msg)
        mock_sys.exit.assert_called_once_with(0)
        mock_sys.stdout.write.called_once_with("OK - {}".format(self.msg))

    def test_warning_state(self, mock_sys):
        self.plugin_inst.warning_state(self.msg)
        mock_sys.exit.assert_called_once_with(1)
        mock_sys.stdout.write.called_once_with("WARNING - {}".format(self.msg))

    def test_critical_state(self, mock_sys):
        self.plugin_inst.critical_state(self.msg)
        mock_sys.exit.assert_called_once_with(2)
        mock_sys.stdout.write.called_once_with("CRITICAL - {}".format(self.msg))

    def test_unknown_state(self, mock_sys):
        self.plugin_inst.unknown_state(self.msg)
        mock_sys.exit.assert_called_once_with(3)
        mock_sys.stdout.write.called_once_with("UNKNOWN - {}".format(self.msg))


class TestSupervisordServiceCheck(unittest.TestCase):

    def setUp(self):
        self.ssc = SupervisordServiceCheck()

        # Mock the NagiosPlugin methods and how they would behave - i.e. SystemExit is raised
        self.ssc.ok_state = mock.Mock()
        self.ssc.warning_state = mock.Mock(side_effect=SystemExit)
        self.ssc.critical_state = mock.Mock(side_effect=SystemExit)
        self.ssc.unknown_state = mock.Mock(side_effect=SystemExit)

    @mock.patch('check_supervisord.subprocess.check_output')
    def test_run_check(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(2, self.ssc.CHECK_CMD)
        with self.assertRaises(SystemExit):
            self.ssc.run_check()
        self.ssc.critical_state.assert_called_once_with('Supervisord service not running')


class TestSupervisordProcessCheck(unittest.TestCase):

    def setUp(self):
        self.spc = SupervisordProcessCheck()

        # Mock the NagiosPlugin methods and how they would behave - i.e. SystemExit is raised
        self.spc.ok_state = mock.Mock()
        self.spc.warning_state = mock.Mock(side_effect=SystemExit)
        self.spc.critical_state = mock.Mock(side_effect=SystemExit)
        self.spc.unknown_state = mock.Mock(side_effect=SystemExit)

    @mock.patch('check_supervisord.subprocess.check_output')
    def test_run_check_unknown_state(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(2, self.spc.CHECK_CMD)
        with self.assertRaises(SystemExit):
            self.spc.run_check()
        self.spc.unknown_state.assert_called_once_with('Unable to get process status')

    @mock.patch('check_supervisord.subprocess.check_output')
    def test_run_check_critical_state(self, mock_check_output):
        mock_check_output.return_value = 'proc1  FATAL  test\nproc2  BACKOFF  test2\nproc3  RUNNING\n'
        with self.assertRaises(SystemExit):
            self.spc.run_check()

        expected_msg="proc1 is FATAL\n\tproc2 is BACKOFF\n\t"
        self.spc.critical_state.assert_called_once_with(expected_msg)

        self.spc.critical_state.reset_mock()
        mock_check_output.return_value = 'proc1  RUNNING\nproc2  FATAL  test2\nproc3  UNKNOWN  test\n'
        with self.assertRaises(SystemExit):
            self.spc.run_check()

        expected_msg="proc3 is UNKNOWN\n\tproc2 is FATAL\n\t"
        self.spc.critical_state.assert_called_once_with(expected_msg)

        self.spc.critical_state.reset_mock()
        mock_check_output.return_value = 'proc1  EXITED  test\nproc3  RUNNING\nproc2  STOPPING  test2\n'
        with self.assertRaises(SystemExit):
            self.spc.run_check()

        expected_msg="proc1 is EXITED\n\tproc2 is STOPPING\n\t"
        self.spc.critical_state.assert_called_once_with(expected_msg)

    @mock.patch('check_supervisord.subprocess.check_output')
    def test_run_check_warning(self, mock_check_output):
        mock_check_output.return_value = 'proc1  STARTING  test\nproc2  STOPPING  test2\nproc3  RUNNING\n'
        with self.assertRaises(SystemExit):
            self.spc.run_check()

        expected_msg="proc1 is STARTING\n\tproc2 is STOPPING\n\t"
        self.spc.warning_state.assert_called_once_with(expected_msg)

        self.spc.warning_state.reset_mock()
        mock_check_output.return_value = 'proc1  RUNNING\nproc2  STARTING  test2\nproc3  RUNNING'
        with self.assertRaises(SystemExit):
            self.spc.run_check()

        expected_msg="proc2 is STARTING\n\t"
        self.spc.warning_state.assert_called_once_with(expected_msg)


if __name__ == '__main__':
    unittest.main()