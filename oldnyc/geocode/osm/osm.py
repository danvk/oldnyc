from typing import Any, Literal, TypedDict, Union


class OsmElementBase(TypedDict):
    id: int
    tags: dict[str, Any]


class OsmNode(OsmElementBase):
    type: Literal["node"]
    lat: float
    lon: float


class OsmWay(OsmElementBase):
    type: Literal["way"]
    nodes: list[int]


class RelationMember(TypedDict):
    type: Union[Literal["way"], Literal["node"], Literal["relation"]]
    ref: int
    role: str


class OsmRelation(OsmElementBase):
    type: Literal["relation"]
    members: list[RelationMember]


OsmElement = Union[OsmNode, OsmWay, OsmRelation]
