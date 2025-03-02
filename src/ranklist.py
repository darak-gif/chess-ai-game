from dataclasses import dataclass
import os
import math


@dataclass
class User:
    username: str
    password: str
    score: int


class RankList:

    def __init__(self, file_path: list[str], k_factor: int) -> None:  #! can throw
        self.k_factor = k_factor
        self._data = {}
        self._was_changed = False
        self.file_path = os.path.join(*file_path)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as fd:
                pass
        else:
            self.load_data()

    def load_data(self) -> None:  #! can throw
        # The file format should be: "username,password,score" on each line.
        try:
            with open(self.file_path, "r") as fd:
                list_of_data = fd.readlines()
        except OSError as e:
            raise RuntimeError(f"Error reading file '{self.file_path}': {e}")
        try:
            self._data = {
                line.split(",")[0]: {
                    "password": line.split(",")[1].strip(),
                    "score": line.split(",")[2].strip(),
                }
                for line in list_of_data
                if line.strip()
            }
        except IndexError:
            raise ValueError("File contains invalid or malformed data.")

    def _from_dict_to_list(self) -> list[str]:
        list_data = [
            f"{key},{values['password']},{values['score']}"
            for key, values in self._data.items()
        ]
        list_data = [line + "\n" for line in list_data]
        return list_data

    def save_ranklist(self) -> None:  #!can throw
        if self._was_changed and self.file_path:
            self.sort_ranklist()
            try:
                with open(self.file_path, "w") as fd:
                    fd.writelines(self._from_dict_to_list())
            except OSError as e:
                raise RuntimeError(f"Error writing file '{self.file_path}': {e}")

    def is_already_has_account(self, user: User) -> bool:
        return (
            user.username in self._data
            and self._data[user.username]["password"] == user.password
        )

    def already_used_nickname(self,user: User) -> bool:
        return user.username in self._data


    def add_new_user(self, new_user: User) -> None:
        new_user.score = 1200
        self._data[new_user.username] = {
            "password": new_user.password,
            "score": str(new_user.score),
        }
        self._was_changed = True

    def change_points_of_user(self, user: User, points: int) -> None:
        if self.is_already_has_account(user):
            score = int(self._data[user.username]["score"]) + points
            self._data[user.username]["score"] = str(score)
            self._was_changed = True

    def sort_ranklist(self) -> None:
        # Sorts the ranking list in descending order based on user scores.
        self._data = {
            k: v
            for k, v in sorted(
                self._data.items(), key=lambda item: int(item[1]["score"]), reverse=True
            )
        }
        self._was_changed = True

    def get_rank_list(
        self,
    ) -> dict[
        str, dict[str, str]
    ]:  # or just to return data by function and to make the view in ranklistState
        if self._was_changed:
            self.sort_ranklist()
        return self._data

    def get_user_score(self, username: str) -> int:
        return int(self._data[username]["score"])

    def probability_first_to_win(
        self, score_player_1: int, score_player_2: int
    ) -> float:
        return 1.0 / (1 + math.pow(10, (score_player_2 - score_player_1) / 400))

    def calculate_elo(
        self, score_player_1: int, score_player_2: int, outcome: float = 0.0
    ) -> tuple[int, int]:
        # outcome:Actual result (1 = Player 1 wins, 0 = Player 2 wins, 0.5 = Draw)
        prob_P_1 = self.probability_first_to_win(score_player_1, score_player_2)
        prob__P_2 = 1 - prob_P_1
        new_points_p_1 = round(self.k_factor * (outcome - prob_P_1))
        new_points_p_2 = round(self.k_factor * ((1 - outcome) - prob__P_2))
        return new_points_p_1, new_points_p_2

    def update_elo(self, player_1: User, player_2: User, outcome: float = 0) -> None:
        # Updates the Elo ratings for two players based on the game outcome.
        # outcome:Actual result (1 = Player 1 wins, 0 = Player 2 wins, 0.5 = Draw)
        new_points = self.calculate_elo(player_1.score, player_2.score, outcome)
        self.change_points_of_user(player_1, new_points[0])
        if not player_2.username.startswith(
            "AI."
        ):  # can be AI, AI score must not be changed
            self.change_points_of_user(player_2, new_points[1])
        self.sort_ranklist()
