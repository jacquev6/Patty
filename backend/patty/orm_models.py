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
from .new_orm_models import (
    AdaptableExercise,
    Adaptation,
    AdaptationBatch,
    AdaptationStrategy,
    AdaptationStrategySettings,
    BaseExercise,
    ClassificationBatch,
    ExerciseClass,
    ExternalExercise,
    Textbook,
)
from .database_utils import OrmBase


__all__ = [
    "AdaptableExercise",
    "Adaptation",
    "AdaptationBatch",
    "AdaptationStrategy",
    "AdaptationStrategySettings",
    "BaseExercise",
    "ClassificationBatch",
    "ExerciseClass",
    "ExternalExercise",
    "OldAdaptation",
    "OldBatch",
    "OldExternalExercise",
    "OldInput",
    "OldStrategy",
    "OldStrategySettings",
    "OldStrategySettingsBranch",
    "OldTextbook",
    "Textbook",
]


all_models: list[type[OrmBase]] = [
    AdaptableExercise,
    Adaptation,
    AdaptationBatch,
    AdaptationStrategy,
    AdaptationStrategySettings,
    BaseExercise,
    ClassificationBatch,
    ExerciseClass,
    ExternalExercise,
    OldAdaptation,
    OldBatch,
    OldExternalExercise,
    OldInput,
    OldStrategy,
    OldStrategySettings,
    OldStrategySettingsBranch,
    OldTextbook,
    Textbook,
]
