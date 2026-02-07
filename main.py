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


class GameState:
    def __init__(self) -> None:
        self.day = 1
        self.day_limit = 10
        self.actions_per_day = 2
        self.fields = [FieldPlot() for _ in range(4)]
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

    def print_status(self) -> None:
        print("\n=== ステータス ===")
        print(f"日数: {self.day}/{self.day_limit}")
        print("畑の状態:")
        for i, plot in enumerate(self.fields, start=1):
            if plot.crop is None:
                status = "空き"
            elif plot.is_ready(self.day):
                status = f"{plot.crop.name} (収穫OK)"
            else:
                remaining = plot.crop.grow_days - (self.day - plot.planted_day)
                status = f"{plot.crop.name} (あと{remaining}日)"
            print(f"  {i}. {status}")
        print("家畜の状態:")
        for i, animal in enumerate(self.livestock, start=1):
            hunger_state = "元気" if animal.hunger == 0 else f"空腹 {animal.hunger}日目"
            print(f"  {i}. {animal.livestock_type.name}: {hunger_state}")
        print("所持品:")
        for item, amount in self.inventory.items():
            print(f"  {item}: {amount}")
        print("目標:")
        for item, amount in self.goal.items():
            print(f"  {item}: {amount}")
        print("=================\n")


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


def plant_crop(state: GameState) -> None:
    empty_plots = [i for i, plot in enumerate(state.fields) if plot.crop is None]
    if not empty_plots:
        print("畑に空きがありません。収穫してから植えましょう。")
        return
    crop_index = prompt_choice("植える作物を選んでください:", [c.name for c in CROPS])
    plot_choices = [f"畑 {i + 1}" for i in empty_plots]
    plot_index = prompt_choice("植える場所を選んでください:", plot_choices)
    plot = state.fields[empty_plots[plot_index]]
    plot.crop = CROPS[crop_index]
    plot.planted_day = state.day
    print(f"{plot.crop.name}を植えました！")


def harvest(state: GameState) -> None:
    ready_plots = [i for i, plot in enumerate(state.fields) if plot.is_ready(state.day)]
    if not ready_plots:
        print("収穫できる作物がありません。")
        return
    plot_choices = [
        f"畑 {i + 1}: {state.fields[i].crop.name}" for i in ready_plots
    ]
    plot_index = prompt_choice("収穫する作物を選んでください:", plot_choices)
    plot = state.fields[ready_plots[plot_index]]
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
            print(f"残り行動回数: {actions_left}")
            choice = prompt_choice(
                "行動を選んでください:",
                [
                    "作物を植える",
                    "作物を収穫する",
                    "家畜にエサをあげる",
                    "ステータス確認",
                    "行動を終了する",
                ],
            )
            if choice == 0:
                plant_crop(state)
                actions_left -= 1
            elif choice == 1:
                harvest(state)
                actions_left -= 1
            elif choice == 2:
                feed_animals(state)
                actions_left -= 1
            elif choice == 3:
                state.print_status()
            elif choice == 4:
                actions_left = 0

            if state.goal_met():
                print("\n目標を達成しました！農場は大成功です！\n")
                return

        end_day(state)

    if state.goal_met():
        print("\n制限日数ギリギリで目標達成！素晴らしい成果です！\n")
    else:
        print("\n時間切れです。次はもっと計画的に挑戦しましょう。\n")
        state.print_status()


if __name__ == "__main__":
    main()
