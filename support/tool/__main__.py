# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

from .main_command import main
from .dev import commands as dev_commands  # noqa: F401 to load commands
from .prod import commands as prod_commands  # noqa: F401


if __name__ == "__main__":
    main()
