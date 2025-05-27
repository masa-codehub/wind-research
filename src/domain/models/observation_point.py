from dataclasses import dataclass

@dataclass(frozen=True)
class ObservationPointValue:
    """
    観測地点を表す値オブジェクト。
    都道府県番号と地点番号の組み合わせで一意。
    不変・等価性・自己検証を持つ。
    """
    prefecture_no: str
    block_no: str

    def __post_init__(self):
        if not self.prefecture_no or not self.block_no:
            raise ValueError("都道府県番号と地点番号は必須です。")
