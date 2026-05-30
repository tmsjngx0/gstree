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
    staged: int = 0
    modified: int = 0
    untracked: int = 0

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        if not any((self.staged, self.modified, self.untracked)):
            payload.pop("staged")
            payload.pop("modified")
            payload.pop("untracked")
        return payload
