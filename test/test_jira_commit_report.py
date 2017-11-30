# -*- coding: utf-8 -*-
import unittest

import jira_commits_report as jcr

class ReportCreationTest(unittest.TestCase):
    def testSanitize(self):
        field = "Use ""this"""

        self.assertEqual("Use """"this""""", jcr.sanitize(field))


if __name__ == '__main__':
    unittest.main()
