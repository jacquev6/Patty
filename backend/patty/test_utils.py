import os
import unittest


costs_money = unittest.skipUnless("PATTY_TESTS_SPEND_MONEY" in os.environ, "Costs money")
