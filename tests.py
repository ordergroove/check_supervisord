import unittest
import mock
import subprocess

from check_supervisord import SupervisordServiceCheck, SupervisordProcessCheck


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
        mock_check_output.side_effect = subprocess.CalledProcessError
        self.assertRaises(subprocess.CalledProcessError, self.ssc.run_check)


class TestSupervisordProcessCheck(unittest.TestCase):

    def setUp(self):
        self.spc = SupervisordProcessCheck()

        # Mock the NagiosPlugin methods and how they would behave - i.e. SystemExit is raised
        self.spc.ok_state = mock.Mock()
        self.spc.warning_state = mock.Mock(side_effect=SystemExit)
        self.spc.critical_state = mock.Mock(side_effect=SystemExit)
        self.spc.unknown_state = mock.Mock(side_effect=SystemExit)

if __name__ == '__main__':
    unittest.main()