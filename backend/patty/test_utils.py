import os
import unittest


costs_money = unittest.skipUnless("PATTY_TESTS_SPEND_MONEY" in os.environ, "Costs money")

skip_migrations = os.environ.get("PATTY_TESTS_SKIP_MIGRATIONS", "false") == "true"
