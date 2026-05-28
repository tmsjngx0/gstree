from dataclasses import asdict, dataclass


@dataclass(slots=True)
class RepoStatus:
    name: str
    path: str
    branch: str
    dirty: bool
    tracking: bool
    ahead: int
    behind: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
