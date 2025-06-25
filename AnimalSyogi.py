# 動物将棋のテキストベース実装
class AnimalSyogi:
    def __init__(self):
        # 初期盤面設定
        # L: ライオン, E: ゾウ, G: キリン, C: ヒヨコ, N: ニワトリ
        # 数字1: プレイヤー1, 数字2: プレイヤー2
        self.board = [
            ["G2", "L2", "E2"],
            ["  ", "C2", "  "],
            ["  ", "C1", "  "],
            ["E1", "L1", "G1"],
        ]
        self.turn = 1  # 現在のプレイヤー (1 または 2)
        self.captured_pieces = {1: [], 2: []}  # 各プレイヤーの持ち駒
        self.history = []  # 盤面履歴（千日手判定用）

    def display_board(self):
        """盤面と持ち駒を表示"""
        print("\n   A    B    C")
        for i, row in enumerate(self.board, start=1):
            print(i, " | ".join(row))
            if i < 4:
                print("  ---+----+---")
        print(f"プレイヤー1の持ち駒: {self.captured_pieces[1]}")
        print(f"プレイヤー2の持ち駒: {self.captured_pieces[2]}")
        print()

    def get_piece_direction(self, piece, player):
        """各駒の移動方向を返す
        - L (ライオン): 全方向
        - E (ゾウ): 斜め方向
        - G (キリン): 縦横方向
        - C (ヒヨコ): 前方向のみ
        - N (ニワトリ): 斜め後ろ方向以外
        """
        base_directions = {
            "L": [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)],
            "E": [(1, 1), (-1, -1), (1, -1), (-1, 1)],
            "G": [(0, 1), (1, 0), (0, -1), (-1, 0)],
            "C": [(0, 1)],
            "N": [(0, 1), (1, 1), (-1, 1), (-1, 0), (1, 0), (0, -1)],
        }

        # 駒の種類を取得
        piece_type = piece[0]

        # プレイヤーによる進行方向の調整
        directions = base_directions[piece_type]
        if player == 1:
            # プレイヤー2の場合は方向を反転させる
            directions = [(-dx, -dy) for dx, dy in directions]

        return directions

    def is_valid_move(self, start, end, player):
        """駒の移動が有効かを判定"""
        start_x, start_y = ord(start[0]) - ord("A"), int(start[1]) - 1
        end_x, end_y = ord(end[0]) - ord("A"), int(end[1]) - 1

        # 入力座標が盤面内かどうかをチェック
        if not (0 <= start_x < 3 and 0 <= start_y < 4 and 0 <= end_x < 3 and 0 <= end_y < 4):
            print("範囲外の座標です。")
            return False

        piece = self.board[start_y][start_x]

        # 開始位置に自分の駒がない場合、無効
        if piece == "  " or not piece.endswith(str(player)):
            print(f"無効な開始位置です: {start}")
            return False

        # 移動方向を計算
        direction = (end_x - start_x, end_y - start_y)

        # 指定方向が駒の移動可能な方向かを確認
        valid_directions = self.get_piece_direction(piece, player)
        if direction not in valid_directions:
            print(f"無効な移動方向: {direction}")
            return False

        # 移動先が空マスまたは相手の駒がある場合のみ有効
        target_piece = self.board[end_y][end_x]
        if target_piece == "  ":
            return True  # 空のマスは有効
        elif target_piece.endswith(str(3 - player)):  # 相手の駒がある場合
            return True

        # それ以外の場合（自分の駒がある場合など）
        print(f"移動先が無効です: {end} ({target_piece})")
        return False

    def move_piece(self, start, end, player):
        """駒を移動し、必要なら駒を捕獲"""
        start_x, start_y = ord(start[0]) - ord("A"), int(start[1]) - 1
        end_x, end_y = ord(end[0]) - ord("A"), int(end[1]) - 1
        piece = self.board[start_y][start_x]
        target_piece = self.board[end_y][end_x]

        # 開始位置を空にし、移動先に駒を置く
        self.board[start_y][start_x] = "  "
        self.board[end_y][end_x] = piece

        # 移動先に相手の駒がある場合は捕獲
        if target_piece != "  ":
            captured_piece = target_piece[0] + str(player)
            # ニワトリを捕獲した場合、ヒヨコに戻す
            if captured_piece.startswith("N"):
                captured_piece = "C" + str(player)
            self.captured_pieces[player].append(captured_piece)

        # ヒヨコが相手のエリアに到達したら進化
        if piece.startswith("C"):
            if (player == 1 and end_y == 0) or (player == 2 and end_y == 3):
                self.board[end_y][end_x] = "N" + str(player)  # ヒヨコがにわとりに進化
                print(f"プレイヤー{player}のヒヨコがにわとりに進化しました！")

    def place_piece(self, pos, piece, player):
        """持ち駒を盤面に配置"""
        x, y = ord(pos[0]) - ord("A"), int(pos[1]) - 1
        if self.board[y][x] == "  ":
            self.board[y][x] = piece
            self.captured_pieces[player].remove(piece)
            return True
        return False

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
        """勝利条件をチェック (ライオン捕獲やトライの判定)"""
        # ライオンが盤面にいない場合
        lions = [
            piece for row in self.board for piece in row if piece.startswith("L")]
        if "L2" not in lions:
            print("プレイヤー1の勝利！")
            return True
        elif "L1" not in lions:
            print("プレイヤー2の勝利！")
            return True

        # トライ (ライオンが相手エリアに到達)
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

    def is_repetition(self):
        """千日手の判定 (同じ盤面が3回出現した場合)"""
        board_state = tuple(tuple(row) for row in self.board)
        self.history.append(board_state)
        if self.history.count(board_state) >= 3:
            print("千日手です！引き分けになります。")
            return True
        return False

    def play(self):
        """ゲームの進行"""
        while True:
            self.display_board()  # 盤面を表示

            # 千日手判定
            if self.is_repetition():
                break

            print(f"プレイヤー{self.turn}のターンです")
            action = input("コマを動かす場合は'M'、持ち駒を置く場合は'P'を入力: ").strip().upper()

            if action == "M":
                # 駒を動かす処理
                start = input("動かしたいコマの位置（例: A1）: ")
                end = input("移動先の位置（例: A2）: ")
                if self.is_valid_move(start, end, self.turn):
                    self.move_piece(start, end, self.turn)
                else:
                    print("不正な動きです。もう一度入力してください。")
                    continue
            elif action == "P":
                # 持ち駒を配置する処理
                piece = input("置きたい持ち駒（例: C1）: ")
                pos = input("置く位置（例: A2）: ")
                if piece in self.captured_pieces[self.turn] and self.place_piece(pos, piece, self.turn):
                    pass
                else:
                    print("不正な配置です。もう一度入力してください。")
                    continue
            else:
                print("不正な入力です。もう一度入力してください。")
                continue

            # 勝利条件の判定
            if self.check_win():
                break

            # ターンを切り替え
            self.turn = 3 - self.turn


# ゲーム開始
game = AnimalSyogi()
game.play()
