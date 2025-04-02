import os
import unittest


costs_money = unittest.skipUnless("PATTY_RUN_TESTS_COSTING_MONEY" in os.environ, "Costs money")
