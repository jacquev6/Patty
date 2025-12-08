# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>
# Copyright 2025 Elise Lincker <elise.lincker@lecnam.net>

# This module's sole purpose is to allow unpickling the model. It's been pickled in an environment
# where there was a 'models_bert_torch' top-level module with the 'SingleBert' class, but I've
# refactored all that in 'patty.classification'.

from patty.classification.models import SingleBert

__all__ = ["SingleBert"]
