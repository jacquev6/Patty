import typing

import openai.lib._parsing._completions
import pydantic

from ...any_json import JsonDict


CustomPydanticModel = typing.TypeVar("CustomPydanticModel", bound=pydantic.BaseModel)


def make_schema(model: type[CustomPydanticModel]) -> JsonDict:
    response_format_param = openai.lib._parsing._completions.type_to_response_format_param(model)
    assert isinstance(response_format_param, dict)
    assert response_format_param["type"] == "json_schema"
    return response_format_param["json_schema"]["schema"]


# def _is_ref_dict(schema: JsonType, *, refs: set[str] | None = None) -> str | None:
#     if isinstance(schema, dict) and len(schema) == 1 and "$ref" in schema:
#         ref = schema["$ref"]
#         assert isinstance(ref, str)
#         if refs is None or ref in refs:
#             return ref
#     return None


# def _gather_refs(schema: JsonType) -> typing.Iterable[str]:
#     if ref := _is_ref_dict(schema):
#         yield ref
#     elif isinstance(schema, dict):
#         for v in schema.values():
#             yield from _gather_refs(v)
#     elif isinstance(schema, list):
#         for item in schema:
#             yield from _gather_refs(item)


# def _replace_refs(schema: JsonType, repl: dict[str, str]) -> JsonType:
#     if ref := _is_ref_dict(schema, refs=set(repl.keys())):
#         return {"$ref": repl[ref]}
#     elif isinstance(schema, dict):
#         return {k: _replace_refs(v, repl) for k, v in schema.items()}
#     elif isinstance(schema, list):
#         return [_replace_refs(item, repl) for item in schema]
#     else:
#         return schema


# def _remove_refs(schema: JsonType, refs: set[str]) -> JsonType:
#     if isinstance(schema, dict):
#         return {k: _remove_refs(v, refs) for k, v in schema.items()}
#     elif isinstance(schema, list):
#         return [_remove_refs(item, refs) for item in schema if not _is_ref_dict(item, refs=refs)]
#     else:
#         return schema


# def make_non_recursive_schema(model: type[CustomPydanticModel], *, max_depth: int = 3) -> JsonDict:
#     schema = make_schema(model)

#     if "$defs" in schema:
#         original_defs: dict[str, JsonType] = schema["$defs"]
#         new_defs: dict[str, JsonType] = {}

#         dependency_graph = nx.DiGraph(
#             [(f"#/$defs/{orig}", dest) for orig, value in original_defs.items() for dest in set(_gather_refs(value))]
#         )
#         cyclic_defs = set()
#         for scc in nx.strongly_connected_components(dependency_graph):
#             if len(scc) > 1:
#                 cyclic_defs |= scc
#             elif len(scc) == 1:
#                 ref = next(iter(scc))
#                 if dependency_graph.has_edge(ref, ref):
#                     cyclic_defs.add(ref)

#         for key in original_defs.keys():
#             new_defs[key] = _replace_refs(original_defs[key], {k: f"{k}1" for k in cyclic_defs})
#             if f"#/$defs/{key}" in cyclic_defs:
#                 for depth in range(1, max_depth):
#                     new_defs[f"{key}{depth}"] = _replace_refs(
#                         original_defs[key], {k: f"{k}{depth+1}" for k in cyclic_defs}
#                     )
#                 new_defs[f"{key}{max_depth}"] = _remove_refs(original_defs[key], cyclic_defs)

#         used_defs = set()
#         refs_to_explore = set(_gather_refs([schema.get("properties", {}), schema.get("anyOf", [])]))
#         while refs_to_explore:
#             ref = refs_to_explore.pop()
#             assert ref.startswith("#/$defs/")
#             ref = ref[8:]
#             if ref not in used_defs:
#                 used_defs.add(ref)
#                 refs_to_explore.update(_gather_refs(new_defs[ref]))

#         schema["$defs"] = {k: v for (k, v) in new_defs.items() if k in used_defs}

#     return schema


# class MakeNonRecursiveSchemaTestCase(unittest.TestCase):
#     maxDiff = None

#     def test_non_recursive__without_defs(self) -> None:
#         class A(pydantic.BaseModel):
#             a: int
#             b: str

#         self.assertEqual(
#             make_non_recursive_schema(A),
#             {
#                 "additionalProperties": False,
#                 "properties": {"a": {"title": "A", "type": "integer"}, "b": {"title": "B", "type": "string"}},
#                 "required": ["a", "b"],
#                 "title": "A",
#                 "type": "object",
#             },
#         )

#     def test_non_recursive__with_defs(self) -> None:
#         class B(pydantic.BaseModel):
#             x: float

#         class A(pydantic.BaseModel):
#             a: int
#             b: B

#         self.assertEqual(
#             make_non_recursive_schema(A),
#             {
#                 "$defs": {
#                     "B": {
#                         "additionalProperties": False,
#                         "properties": {"x": {"title": "X", "type": "number"}},
#                         "required": ["x"],
#                         "title": "B",
#                         "type": "object",
#                     }
#                 },
#                 "additionalProperties": False,
#                 "properties": {"a": {"title": "A", "type": "integer"}, "b": {"$ref": "#/$defs/B"}},
#                 "required": ["a", "b"],
#                 "title": "A",
#                 "type": "object",
#             },
#         )

#     def test_auto_recursive__in_optional(self) -> None:
#         class A(pydantic.BaseModel):
#             t: A | None

#         self.assertEqual(
#             make_non_recursive_schema(A),
#             {
#                 "$defs": {
#                     "A": {
#                         "additionalProperties": False,
#                         "properties": {"t": {"anyOf": [{"$ref": "#/$defs/A1"}, {"type": "null"}]}},
#                         "required": ["t"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A1": {
#                         "additionalProperties": False,
#                         "properties": {"t": {"anyOf": [{"$ref": "#/$defs/A2"}, {"type": "null"}]}},
#                         "required": ["t"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A2": {
#                         "additionalProperties": False,
#                         "properties": {"t": {"anyOf": [{"$ref": "#/$defs/A3"}, {"type": "null"}]}},
#                         "required": ["t"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A3": {
#                         "additionalProperties": False,
#                         "properties": {"t": {"anyOf": [{"type": "null"}]}},
#                         "required": ["t"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                 },
#                 "additionalProperties": False,
#                 "properties": {"t": {"anyOf": [{"$ref": "#/$defs/A"}, {"type": "null"}]}},
#                 "required": ["t"],
#                 "title": "A",
#                 "type": "object",
#             },
#         )

#     def test_non_recursive__in_auto_recursive(self) -> None:
#         class A(pydantic.BaseModel):
#             a: int

#         class B(pydantic.BaseModel):
#             t: B | None
#             a: A

#         self.assertEqual(
#             make_non_recursive_schema(B),
#             {
#                 "$defs": {
#                     "A": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"title": "A", "type": "integer"}},
#                         "required": ["a"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "B": {
#                         "additionalProperties": False,
#                         "properties": {
#                             "a": {"$ref": "#/$defs/A"},
#                             "t": {"anyOf": [{"$ref": "#/$defs/B1"}, {"type": "null"}]},
#                         },
#                         "required": ["t", "a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B1": {
#                         "additionalProperties": False,
#                         "properties": {
#                             "a": {"$ref": "#/$defs/A"},
#                             "t": {"anyOf": [{"$ref": "#/$defs/B2"}, {"type": "null"}]},
#                         },
#                         "required": ["t", "a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B2": {
#                         "additionalProperties": False,
#                         "properties": {
#                             "a": {"$ref": "#/$defs/A"},
#                             "t": {"anyOf": [{"$ref": "#/$defs/B3"}, {"type": "null"}]},
#                         },
#                         "required": ["t", "a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B3": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"$ref": "#/$defs/A"}, "t": {"anyOf": [{"type": "null"}]}},
#                         "required": ["t", "a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                 },
#                 "additionalProperties": False,
#                 "properties": {"a": {"$ref": "#/$defs/A"}, "t": {"anyOf": [{"$ref": "#/$defs/B"}, {"type": "null"}]}},
#                 "required": ["t", "a"],
#                 "title": "B",
#                 "type": "object",
#             },
#         )

#     def test_mutually_recursive(self) -> None:
#         class A(pydantic.BaseModel):
#             b: B | None

#         class B(pydantic.BaseModel):
#             a: A | None

#         self.assertEqual(
#             make_non_recursive_schema(A),
#             {
#                 "$defs": {
#                     "A1": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B2"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A3": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "B": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A1"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B2": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A3"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                 },
#                 "additionalProperties": False,
#                 "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B"}, {"type": "null"}]}},
#                 "required": ["b"],
#                 "title": "A",
#                 "type": "object",
#             },
#         )

#     def test_mutually_recursive__nested_in_object(self) -> None:
#         class A(pydantic.BaseModel):
#             b: B | None

#         class B(pydantic.BaseModel):
#             a: A | None

#         class C(pydantic.BaseModel):
#             a: A
#             b: B

#         self.assertEqual(
#             make_non_recursive_schema(C),
#             {
#                 "$defs": {
#                     "A": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B1"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A1": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B2"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A2": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B3"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A3": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "B": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A1"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B1": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A2"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B2": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A3"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B3": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                 },
#                 "additionalProperties": False,
#                 "properties": {"a": {"$ref": "#/$defs/A"}, "b": {"$ref": "#/$defs/B"}},
#                 "required": ["a", "b"],
#                 "title": "C",
#                 "type": "object",
#             },
#         )

#     def test_mutually_recursive__nested_in_union(self) -> None:
#         class A(pydantic.BaseModel):
#             b: B | None

#         class B(pydantic.BaseModel):
#             a: A | None

#         self.assertEqual(
#             make_non_recursive_schema(pydantic.RootModel[A | B]),
#             {
#                 "$defs": {
#                     "A": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B1"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A1": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B2"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A2": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"$ref": "#/$defs/B3"}, {"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "A3": {
#                         "additionalProperties": False,
#                         "properties": {"b": {"anyOf": [{"type": "null"}]}},
#                         "required": ["b"],
#                         "title": "A",
#                         "type": "object",
#                     },
#                     "B": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A1"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B1": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A2"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B2": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"$ref": "#/$defs/A3"}, {"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                     "B3": {
#                         "additionalProperties": False,
#                         "properties": {"a": {"anyOf": [{"type": "null"}]}},
#                         "required": ["a"],
#                         "title": "B",
#                         "type": "object",
#                     },
#                 },
#                 "anyOf": [{"$ref": "#/$defs/A"}, {"$ref": "#/$defs/B"}],
#                 "title": "RootModel[Union[MakeNonRecursiveSchemaTestCase.test_mutually_recursive__nested_in_union.<locals>.A, MakeNonRecursiveSchemaTestCase.test_mutually_recursive__nested_in_union.<locals>.B]]",
#             },
#         )


# def replace_const_with_enum(schema: JsonType) -> JsonType:
#     if isinstance(schema, dict):
#         if schema.get("type") == "string" and "const" in schema:
#             return {"type": "string", "enum": [schema["const"]]}
#         else:
#             return {k: replace_const_with_enum(v) for k, v in schema.items()}
#     elif isinstance(schema, list):
#         return [replace_const_with_enum(item) for item in schema]
#     else:
#         return schema
