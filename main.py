from dataclasses import dataclass


@dataclass(frozen=True)
class CropType:
    name: str
    grow_days: int


@dataclass(frozen=True)
class LivestockType:
    name: str
    product: str


@dataclass
class FieldPlot:
    crop: CropType | None = None
    planted_day: int | None = None

    def is_ready(self, current_day: int) -> bool:
        if self.crop is None or self.planted_day is None:
            return False
        return current_day - self.planted_day >= self.crop.grow_days


@dataclass
class Livestock:
    livestock_type: LivestockType
    hunger: int = 0

    def feed(self) -> str:
        self.hunger = 0
        return self.livestock_type.product

    def pass_day(self) -> None:
        self.hunger += 1


CROPS = [
    CropType("にんじん", 2),
    CropType("じゃがいも", 3),
    CropType("かぼちゃ", 4),
]
LIVESTOCK_TYPES = [
    LivestockType("ニワトリ", "たまご"),
    LivestockType("ウシ", "ミルク"),
]

GRID_WIDTH = 8
GRID_HEIGHT = 6
FIELD_POSITIONS = [(2, 1), (3, 1), (2, 2), (3, 2)]
BARN_POSITION = (6, 4)


class GameState:
    def __init__(self) -> None:
        self.day = 1
        self.day_limit = 10
        self.actions_per_day = 3
        self.player_pos = (0, 0)
        self.fields = {pos: FieldPlot() for pos in FIELD_POSITIONS}
        self.livestock = [
            Livestock(LIVESTOCK_TYPES[0]),
            Livestock(LIVESTOCK_TYPES[0]),
            Livestock(LIVESTOCK_TYPES[1]),
        ]
        self.inventory: dict[str, int] = {
            "たまご": 0,
            "ミルク": 0,
            "にんじん": 0,
            "じゃがいも": 0,
            "かぼちゃ": 0,
            "エサ": 6,
        }
        self.goal: dict[str, int] = {
            "にんじん": 5,
            "じゃがいも": 3,
            "たまご": 4,
            "ミルク": 2,
        }

    def goal_met(self) -> bool:
        return all(self.inventory.get(item, 0) >= amount for item, amount in self.goal.items())


def print_status(state: GameState) -> None:
    print("\n=== ステータス ===")
    print(f"日数: {state.day}/{state.day_limit}")
    print(f"現在地: {state.player_pos}")
    print("畑の状態:")
    for pos, plot in state.fields.items():
        if plot.crop is None:
            status = "空き"
        elif plot.is_ready(state.day):
            status = f"{plot.crop.name} (収穫OK)"
        else:
            remaining = plot.crop.grow_days - (state.day - plot.planted_day)
            status = f"{plot.crop.name} (あと{remaining}日)"
        print(f"  {pos}: {status}")
    print("家畜の状態:")
    for i, animal in enumerate(state.livestock, start=1):
        hunger_state = "元気" if animal.hunger == 0 else f"空腹 {animal.hunger}日目"
        print(f"  {i}. {animal.livestock_type.name}: {hunger_state}")
    print("所持品:")
    for item, amount in state.inventory.items():
        print(f"  {item}: {amount}")
    print("目標:")
    for item, amount in state.goal.items():
        print(f"  {item}: {amount}")
    print("=================\n")


def render_map(state: GameState) -> None:
    print("\n=== 農場マップ ===")
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
            pos = (x, y)
            if pos == state.player_pos:
                row.append("@")
            elif pos in state.fields:
                row.append("F")
            elif pos == BARN_POSITION:
                row.append("B")
            else:
                row.append(".")
        print(" ".join(row))
    print("凡例: @=主人公, F=畑, B=牧舎, .=道\n")


def prompt_choice(prompt: str, choices: list[str]) -> int:
    while True:
        print(prompt)
        for i, choice in enumerate(choices, start=1):
            print(f"  {i}. {choice}")
        selection = input("番号を入力: ").strip()
        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(choices):
                return index
        print("入力が正しくありません。もう一度お試しください。\n")


def move_player(state: GameState) -> None:
    directions = {
        "W": (0, -1),
        "A": (-1, 0),
        "S": (0, 1),
        "D": (1, 0),
    }
    while True:
        move = input("移動 (W/A/S/D) を入力: ").strip().upper()
        if move in directions:
            dx, dy = directions[move]
            new_x = max(0, min(GRID_WIDTH - 1, state.player_pos[0] + dx))
            new_y = max(0, min(GRID_HEIGHT - 1, state.player_pos[1] + dy))
            state.player_pos = (new_x, new_y)
            print(f"現在地: {state.player_pos}")
            return
        print("入力が正しくありません。W/A/S/Dで入力してください。\n")


def plant_crop(state: GameState, plot: FieldPlot) -> None:
    crop_index = prompt_choice("植える作物を選んでください:", [c.name for c in CROPS])
    plot.crop = CROPS[crop_index]
    plot.planted_day = state.day
    print(f"{plot.crop.name}を植えました！")


def harvest(state: GameState, plot: FieldPlot) -> None:
    crop_name = plot.crop.name
    state.inventory[crop_name] = state.inventory.get(crop_name, 0) + 1
    plot.crop = None
    plot.planted_day = None
    print(f"{crop_name}を収穫しました！")


def feed_animals(state: GameState) -> None:
    if state.inventory.get("エサ", 0) <= 0:
        print("エサが足りません。")
        return
    fed = 0
    for animal in state.livestock:
        if state.inventory.get("エサ", 0) <= 0:
            break
        product = animal.feed()
        state.inventory[product] = state.inventory.get(product, 0) + 1
        state.inventory["エサ"] -= 1
        fed += 1
        print(f"{animal.livestock_type.name}にエサをあげました。{product}を獲得！")
    if fed == 0:
        print("エサをあげられる家畜がいませんでした。")


def interact(state: GameState) -> None:
    if state.player_pos in state.fields:
        plot = state.fields[state.player_pos]
        if plot.crop is None:
            plant_crop(state, plot)
        elif plot.is_ready(state.day):
            harvest(state, plot)
        else:
            remaining = plot.crop.grow_days - (state.day - plot.planted_day)
            print(f"{plot.crop.name}は成長中です。(あと{remaining}日)")
    elif state.player_pos == BARN_POSITION:
        feed_animals(state)
    else:
        print("ここでは特にできることがありません。")


def end_day(state: GameState) -> None:
    for animal in state.livestock:
        animal.pass_day()
    state.day += 1
    print("\n日が暮れました。翌日になりました。\n")


def main() -> None:
    print("農場経営シミュレーション: ほのかのチャレンジ")
    print("主人公の女の子『ほのか』が農場を育てます。")
    print("制限日数内に目標を達成しましょう！\n")

    state = GameState()

    while state.day <= state.day_limit:
        actions_left = state.actions_per_day
        while actions_left > 0:
            render_map(state)
            print(f"残り行動回数: {actions_left}")
            choice = prompt_choice(
                "行動を選んでください:",
                [
                    "移動する",
                    "その場で作業する",
                    "ステータス確認",
                    "行動を終了する",
                ],
            )
            if choice == 0:
                move_player(state)
                actions_left -= 1
            elif choice == 1:
                interact(state)
                actions_left -= 1
            elif choice == 2:
                print_status(state)
            elif choice == 3:
                actions_left = 0

            if state.goal_met():
                print("\n目標を達成しました！農場は大成功です！\n")
                return

        end_day(state)

    if state.goal_met():
        print("\n制限日数ギリギリで目標達成！素晴らしい成果です！\n")
    else:
        print("\n時間切れです。次はもっと計画的に挑戦しましょう。\n")
        print_status(state)


if __name__ == "__main__":
    main()
