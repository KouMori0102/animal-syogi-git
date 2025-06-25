# Animal Shogi - Python implementation
# Author: [あなたの名前]
# This game simulates a 3x4 board Shogi-like game for 2 players or AI.

import random


class AnimalSyogi:
    def __init__(self):
        # 初期盤面設定
        self.board = [
            ["G2", "L2", "E2"],  # プレイヤー2の駒
            ["  ", "C2", "  "],  # プレイヤー2のヒヨコ
            ["  ", "C1", "  "],  # プレイヤー1のヒヨコ
            ["E1", "L1", "G1"],  # プレイヤー1の駒
        ]
        self.turn = 1  # 現在のターン (1または2)
        self.captured_pieces = {1: [], 2: []}  # 各プレイヤーの持ち駒
        self.history = []  # 盤面履歴（千日手判定用）
        self.is_ai = {1: False, 2: False}  # プレイヤー1と2のAIモードを管理

    def display_board(self):
        """現在の盤面と持ち駒を表示"""
        print("\n   A    B    C")
        for i, row in enumerate(self.board, start=1):
            print(i, " | ".join(row))
            if i < 4:
                print("  ---+----+---")
        print(f"プレイヤー1の持ち駒: {self.captured_pieces[1]}")
        print(f"プレイヤー2の持ち駒: {self.captured_pieces[2]}")
        print()

    def get_piece_direction(self, piece, player):
        """駒ごとの移動可能な方向を取得"""
        base_directions = {
            "L": [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)],
            "E": [(1, 1), (-1, -1), (1, -1), (-1, 1)],
            "G": [(0, 1), (1, 0), (0, -1), (-1, 0)],
            "C": [(0, 1)],
            "N": [(0, 1), (1, 1), (-1, 1), (-1, 0), (1, 0), (0, -1)],
        }
        piece_type = piece[0]  # 駒の種類を取得 (L, E, G, C, N)
        directions = base_directions[piece_type]
        if player == 1:
            # プレイヤー1は方向を反転
            directions = [(-dx, -dy) for dx, dy in directions]
        return directions

    def is_valid_move(self, start, end, player):
        """駒の移動が有効かを判定"""
        # 入力座標をインデックスに変換
        start_x, start_y = ord(start[0]) - ord("A"), int(start[1]) - 1
        end_x, end_y = ord(end[0]) - ord("A"), int(end[1]) - 1

        # 移動先が盤面内かを確認
        if not (0 <= start_x < 3 and 0 <= start_y < 4 and 0 <= end_x < 3 and 0 <= end_y < 4):
            return False

        piece = self.board[start_y][start_x]

        # 開始位置に自分の駒があるか確認
        if piece == "  " or not piece.endswith(str(player)):
            return False

        # 移動方向を取得し、指定方向が正しいか確認
        direction = (end_x - start_x, end_y - start_y)
        valid_directions = self.get_piece_direction(piece, player)
        if direction not in valid_directions:
            return False

        # 移動先が空白または相手の駒の場合のみ有効
        target_piece = self.board[end_y][end_x]
        if target_piece == "  " or target_piece.endswith(str(3 - player)):
            return True

        return False

    def is_valid_placement(self, position, piece, player):
        """持ち駒を配置できるかを判定"""
        x, y = ord(position[0]) - ord("A"), int(position[1]) - 1

        # 配置先が盤面内で空白か確認
        if not (0 <= x < 3 and 0 <= y < 4) or self.board[y][x] != "  ":
            return False

        return True

    def move_piece(self, start, end, player):
        """駒を移動し、必要なら駒を捕獲や進化を実行"""
        # 入力座標をインデックスに変換
        start_x, start_y = ord(start[0]) - ord("A"), int(start[1]) - 1
        end_x, end_y = ord(end[0]) - ord("A"), int(end[1]) - 1

        # 駒を移動
        piece = self.board[start_y][start_x]
        target_piece = self.board[end_y][end_x]
        self.board[start_y][start_x] = "  "
        self.board[end_y][end_x] = piece

        # 相手の駒を捕獲
        if target_piece != "  ":
            captured_piece = target_piece[0] + str(player)
            # ニワトリは捕獲されるとヒヨコに戻る
            if captured_piece.startswith("N"):
                captured_piece = "C" + str(player)
            self.captured_pieces[player].append(captured_piece)

        # ヒヨコが相手のエリアに到達したら進化
        if piece.startswith("C"):
            if (player == 1 and end_y == 3) or (player == 2 and end_y == 0):
                self.board[end_y][end_x] = "N" + str(player)  # ヒヨコがにわとりに進化
                print(f"プレイヤー{player}のヒヨコがにわとりに進化しました！")

    def place_piece(self, position, piece, player):
        """持ち駒を盤面に配置"""
        x, y = ord(position[0]) - ord("A"), int(position[1]) - 1
        self.board[y][x] = piece
        self.captured_pieces[player].remove(piece)

    def get_possible_moves(self, player):
        """指定プレイヤーの全可能な移動を取得"""
        moves = []
        for y in range(4):
            for x in range(3):
                start = chr(x + ord("A")) + str(y + 1)
                piece = self.board[y][x]
                if piece.endswith(str(player)):
                    for dx, dy in self.get_piece_direction(piece, player):
                        end_x, end_y = x + dx, y + dy
                        if 0 <= end_x < 3 and 0 <= end_y < 4:
                            end = chr(end_x + ord("A")) + str(end_y + 1)
                            if self.is_valid_move(start, end, player):
                                moves.append((start, end))
        return moves

    def ai_turn(self, player):
        """AIによる移動または配置を実行"""
        moves = self.get_possible_moves(player)
        if self.captured_pieces[player]:
            placements = [
                (chr(x + ord("A")) + str(y + 1), piece)
                for y in range(4)
                for x in range(3)
                for piece in self.captured_pieces[player]
                if self.is_valid_placement(chr(x + ord("A")) + str(y + 1), piece, player)
            ]
        else:
            placements = []

        if moves and (not placements or random.random() > 0.5):
            start, end = random.choice(moves)
            print(f"AIが{start}から{end}へ移動しました。")
            self.move_piece(start, end, player)
        elif placements:
            position, piece = random.choice(placements)
            print(f"AIが持ち駒{piece}を{position}に配置しました。")
            self.place_piece(position, piece, player)

    def is_lion_safe(self, lion_position, opponent):
        # 指定されたライオンの位置が相手に取られないかを判定
        lion_x, lion_y = ord(
            lion_position[0]) - ord("A"), int(lion_position[1]) - 1

        # 相手の全駒の移動可能範囲を計算
        for y in range(4):
            for x in range(3):
                piece = self.board[y][x]
                if piece.endswith(str(opponent)):  # 相手の駒であるかを確認
                    directions = self.get_piece_direction(piece, opponent)
                    for dx, dy in directions:
                        end_x, end_y = x + dx, y + dy
                        if 0 <= end_x < 3 and 0 <= end_y < 4:  # 盤面内であるか確認
                            if end_x == lion_x and end_y == lion_y:
                                return False  # 相手の駒で取れる位置なら安全ではない
        return True

    def check_win(self):
        """勝利条件の判定"""
        # ライオンが盤面から消えた場合
        lions = [
            piece for row in self.board for piece in row if piece.startswith("L")]
        if "L2" not in lions:
            print("プレイヤー1の勝利！")
            return True
        elif "L1" not in lions:
            print("プレイヤー2の勝利！")
            return True

        # トライ（ライオンが相手陣地に到達しており、次ターンに取られない）
        for x in range(3):
            if self.board[0][x] == "L1" and "L1" not in self.captured_pieces[2]:
                lion_position = chr(x + ord("A")) + "1"
                if self.is_lion_safe(lion_position, 2):
                    print("プレイヤー1のトライ勝利！")
                    return True
            if self.board[3][x] == "L2" and "L2" not in self.captured_pieces[1]:
                lion_position = chr(x + ord("A")) + "4"
                if self.is_lion_safe(lion_position, 1):
                    print("プレイヤー2のトライ勝利！")
                    return True

        return False

    def is_repetition(self):
        """千日手の判定"""
        board_state = tuple(tuple(row) for row in self.board)
        self.history.append(board_state)
        if self.history.count(board_state) >= 3:
            print("千日手です！引き分けになります。")
            return True
        return False

    def setup_players(self):
        """プレイヤーのモードを設定"""
        print("プレイヤーのモードを選択してください:")
        for player in [1, 2]:
            while True:
                choice = input(
                    f"プレイヤー{player}はAIにしますか？ (y/n): ").strip().lower()
                if choice == "y":
                    self.is_ai[player] = True
                    print(f"プレイヤー{player}はAIモードに設定されました。")
                    break
                elif choice == "n":
                    self.is_ai[player] = False
                    print(f"プレイヤー{player}は手動モードに設定されました。")
                    break
                else:
                    print("無効な入力です。'y'または'n'を入力してください。")

    def play(self):
        """ゲームの進行"""
        self.setup_players()  # プレイヤー設定
        while True:
            self.display_board()  # 盤面を表示
            if self.is_repetition():  # 千日手判定
                break
            print(f"プレイヤー{self.turn}のターンです")
            if self.is_ai[self.turn]:
                self.ai_turn(self.turn)  # AIの行動
            else:
                # 手動プレイヤーの操作
                try:
                    action = input("駒を動かす場合は'M'、配置は'P': ").strip().upper()
                except EOFError:
                    print("入力エラー。")
                    return
                if action == "M":
                    start = input("動かしたい駒の位置（例: A1）: ")
                    end = input("移動先の位置（例: A2）: ")
                    if self.is_valid_move(start, end, self.turn):
                        self.move_piece(start, end, self.turn)
                    else:
                        print("不正な動きです。もう一度入力してください。")
                        continue
                elif action == "P":
                    piece = input(
                        f"配置する駒を選んでください {self.captured_pieces[self.turn]}: ").strip().upper()
                    position = input("配置する位置（例: A1）: ")
                    if piece in self.captured_pieces[self.turn] and self.is_valid_placement(position, piece, self.turn):
                        self.place_piece(position, piece, self.turn)
                    else:
                        print("不正な配置です。もう一度入力してください。")
                        continue
                else:
                    print("不正な入力です。もう一度入力してください。")
                    continue
            if self.check_win():  # 勝利条件判定
                break
            self.turn = 3 - self.turn  # ターンを切り替え


# ゲーム開始
game = AnimalSyogi()
game.play()
