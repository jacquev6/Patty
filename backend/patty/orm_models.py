from .adaptation import (
    OldAdaptation,
    OldBatch,
    OldExternalExercise,
    OldInput,
    OldStrategy,
    OldStrategySettings,
    OldStrategySettingsBranch,
    OldTextbook,
)
from .database_utils import OrmBase


__all__ = [
    "OldAdaptation",
    "OldBatch",
    "OldExternalExercise",
    "OldInput",
    "OldStrategy",
    "OldStrategySettings",
    "OldStrategySettingsBranch",
    "OldTextbook",
]


all_models: list[type[OrmBase]] = [
    OldAdaptation,
    OldBatch,
    OldExternalExercise,
    OldInput,
    OldStrategy,
    OldStrategySettings,
    OldStrategySettingsBranch,
    OldTextbook,
]
