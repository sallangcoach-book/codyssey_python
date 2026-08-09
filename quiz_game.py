# quiz_game.py
# -----------------------------------------------------------
# 이 파일은 게임 전체 흐름(메뉴, 퀴즈 풀기, 추가, 목록, 점수, 저장/불러오기)을
# 관리하는 QuizGame 클래스를 담고 있음. 
#
# 보너스 기능도 이 파일에 함께 구현되어 있음.
#   - 랜덤 출제 (random 모듈)
#   - 풀 문제 수 선택
#   - 힌트 기능 (사용 시 점수 차감)
#   - 퀴즈 삭제 기능
#   - 점수 기록 히스토리 (날짜/시간, 문제 수, 점수)
# -----------------------------------------------------------

import json
import os
import random
from datetime import datetime

from quiz import Quiz

DATA_FILE_DEFAULT = "state.json"


def get_int_input(prompt, min_value=None, max_value=None):
    """
    사용자로부터 숫자를 입력받는 공용 함수
    다음 상황을 모두 처리한 뒤, 올바른 값이 입력될 때까지 계속 다시 물어보기
      1) 입력 앞뒤 공백 제거
      2) 빈 입력(그냥 Enter)
      3) 숫자로 변환할 수 없는 입력(예: "abc")
      4) 허용 범위(min_value ~ max_value)를 벗어난 숫자
    Ctrl+C, 입력 스트림 종료(EOFError)는 이 함수 밖(run 메서드)에서 한 번에 처리
    """
    while True:
        raw = input(prompt).strip()

        if raw == "":
            print("입력이 비어 있습니다. 숫자를 입력해 주세요.")
            continue

        try:
            value = int(raw)
        except ValueError:
            print(f"'{raw}'는 숫자가 아닙니다. 숫자로 다시 입력해 주세요.")
            continue

        if min_value is not None and value < min_value:
            print(f"{min_value} 이상의 숫자를 입력해 주세요.")
            continue
        if max_value is not None and value > max_value:
            print(f"{max_value} 이하의 숫자를 입력해 주세요.")
            continue

        return value


def get_text_input(prompt):
    """빈 문자열을 허용하지 않는 텍스트 입력 함수"""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print("빈 값은 입력할 수 없습니다. 다시 입력해 주세요.")
            continue
        return raw


class QuizGame:
    """퀴즈 게임 전체를 관리하는 클래스"""

    def __init__(self, data_file=DATA_FILE_DEFAULT):
        self.data_file = data_file
        self.quizzes = []          # Quiz 객체들을 담는 리스트
        self.best_score = 0        # 역대 최고 점수(정답 개수)
        self.history = []          # 점수 기록 히스토리 (보너스)
        self.load_data()

    # -----------------------------------------------------------
    # 기본 퀴즈 데이터
    # -----------------------------------------------------------
    def default_quizzes(self):
               """
               state.json 파일이 없을 때(처음 실행) 사용할 기본 퀴즈 데이터입니다.
               주제: Python · Git 기본 문법 (총 6문제)
               """
               return [
                   Quiz(
                       "파이썬에서 변수에 값을 저장(대입)할 때 사용하는 기호는 무엇일까요?",
                       ["=", "==", "+", ":"],
                       1,
                       hint="'같다'를 비교하는 기호(==)와 헷갈리지 않도록 주의하세요.",
                   ),
                   Quiz(
                       "문자열(글자)을 나타내는 파이썬 자료형은 무엇일까요?",
                       ["int", "str", "list", "bool"],
                       2,
                       hint="영어 단어 'string(문자열)'의 줄임말입니다.",
                   ),
                   Quiz(
                       "조건이 참(True)인 동안 계속 반복 실행하는 문법은 무엇일까요?",
                       ["for", "if", "while", "def"],
                       3,
                       hint="'~하는 동안'이라는 뜻을 가진 영어 단어입니다.",
                   ),
                   Quiz(
                       "클래스 안에서 '이 메서드를 호출한 객체 자기 자신'을 가리키는 이름은 무엇일까요?",
                       ["this", "self", "me", "obj"],
                       2,
                       hint="파이썬 메서드의 첫 번째 매개변수로 흔히 사용됩니다.",
                   ),
                   Quiz(
                       "Git에서 로컬 저장소의 커밋을 원격 저장소(GitHub)로 업로드하는 명령어는 무엇일까요?",
                       ["git pull", "git commit", "git push", "git clone"],
                       3,
                       hint="'밀어 올리다'라는 뜻의 영어 단어에서 온 이름입니다.",
                   ),
                   Quiz(
                       "Git에서 새 브랜치를 만들면서 동시에 그 브랜치로 이동하는 명령어는 무엇일까요?",
                       ["git branch", "git checkout -b", "git merge", "git status"],
                       2,
                       hint="-b 옵션은 '새로 만들라(branch)'는 뜻입니다.",
                   ),
               ]

    # -----------------------------------------------------------
    # 파일 저장 / 불러오기 (state.json)
    # -----------------------------------------------------------
    def load_data(self):
        """
        state.json 파일에서 퀴즈, 최고 점수, 기록 히스토리를 불러옴.
          - 파일이 없으면: 기본 퀴즈 데이터로 시작
          - 파일이 손상되었으면: 안내 메시지를 출력하고 기본 데이터로 복구
        """
        if not os.path.exists(self.data_file):
            print("[안내] 저장된 데이터 파일이 없어 기본 퀴즈로 시작합니다.")
            self.quizzes = self.default_quizzes()
            self.best_score = 0
            self.history = []
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            quizzes_data = data.get("quizzes", [])
            self.quizzes = [Quiz.from_dict(q) for q in quizzes_data]
            if not self.quizzes:
                self.quizzes = self.default_quizzes()

            self.best_score = data.get("best_score", 0)
            self.history = data.get("history", [])

        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            print("[안내] 데이터 파일이 손상되어 있어 기본 퀴즈로 초기화합니다.")
            self.quizzes = self.default_quizzes()
            self.best_score = 0
            self.history = []

    def save_data(self):
        """현재 퀴즈 목록, 최고 점수, 히스토리를 state.json 파일에 저장"""
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[오류] 데이터 저장에 실패했습니다: {e}")

    # -----------------------------------------------------------
    # 메뉴
    # -----------------------------------------------------------
    def show_menu(self):
        print("\n" + "=" * 40)
        print("   나만의 퀴즈 게임 : git-python")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록 보기")
        print("4. 점수 확인 (최고 점수 / 기록 히스토리)")
        print("5. 퀴즈 삭제")
        print("0. 종료")
        print("=" * 40)

    # -----------------------------------------------------------
    # 1) 퀴즈 풀기 (보너스: 랜덤 출제, 문제 수 선택, 힌트)
    # -----------------------------------------------------------
    def play_quiz(self):
        if not self.quizzes:
            print("\n[안내] 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        total_available = len(self.quizzes)
        print(f"\n현재 등록된 퀴즈는 총 {total_available}개입니다.")
        num_questions = get_int_input(
            f"몇 문제를 풀어볼까요? (1~{total_available}): ",
            min_value=1,
            max_value=total_available,
        )

        # 보너스: 랜덤 출제 - 원본 리스트는 건드리지 않도록 복사본을 섞습니다.
        quiz_pool = self.quizzes.copy()
        random.shuffle(quiz_pool)
        selected_quizzes = quiz_pool[:num_questions]
        # 슬라이싱 [시작번호:끝번호]  [:num_questions] 0번부터 num_questions개 까지 자르기. 

        correct_count = 0
        hint_used_count = 0

        for i, quiz in enumerate(selected_quizzes, start=1):
            quiz.display(i)

            # 보너스: 힌트 기능 (0 입력 시 힌트, 힌트 사용 시 감점)
            if quiz.hint:
                print("  0. 힌트 보기")

            while True:
                answer = get_int_input("정답 번호를 입력하세요: ", min_value=0, max_value=4)
                if answer == 0:
                    if quiz.hint:
                        print(f"  힌트: {quiz.hint}")
                        hint_used_count += 1
                        continue
                    else:
                        print("이 문제는 힌트가 없습니다. 1~4 중에서 선택해 주세요.")
                        continue
                break #루프탈출

            if quiz.check_answer(answer):
                print("정답입니다!")
                correct_count += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번 이었습니다.")

        # 힌트 1회당 1점 차감(최소 0점)
        score = max(0, correct_count - hint_used_count)

        print("\n----- 결과 -----")
        print(f"총 {len(selected_quizzes)}문제 중 {correct_count}개 정답")
        if hint_used_count > 0:
            print(f"힌트 사용 {hint_used_count}회로 {hint_used_count}점 차감되었습니다.")
        print(f"최종 점수: {score}점")

        if score > self.best_score:
            print("축하합니다. 최고 점수를 갱신했습니다!")
            self.best_score = score
        else:
            print(f"현재 최고 점수: {self.best_score}점")

        # 보너스: 점수 기록 히스토리 저장, (String Format Time) 날짜를 문자열 형식으로 바꿉
        self.history.append(
            {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_questions": len(selected_quizzes),
                "correct": correct_count,
                "score": score,
            }
        )

        self.save_data()

    # -----------------------------------------------------------
    # 2) 퀴즈 추가
    # -----------------------------------------------------------
    def add_quiz(self):
        print("\n[퀴즈 추가]")
        question = get_text_input("문제를 입력하세요: ")

        choices = []
        for i in range(1, 5):
            choice = get_text_input(f"선택지 {i}번을 입력하세요: ")
            choices.append(choice)

        answer = get_int_input("정답 번호(1~4)를 입력하세요: ", min_value=1, max_value=4)
        hint = input("힌트를 입력하세요 (없으면 그냥 Enter): ").strip()

        new_quiz = Quiz(question, choices, answer, hint)
        self.quizzes.append(new_quiz)
        self.save_data()
        print("새 퀴즈가 추가되었습니다.")

    # -----------------------------------------------------------
    # 3) 퀴즈 목록 보기
    # -----------------------------------------------------------
    def list_quizzes(self):
        print("\n[퀴즈 목록]")
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"{i}. {quiz.question} (정답: {quiz.answer}번)")

    # -----------------------------------------------------------
    # 4) 점수 확인 (보너스: 히스토리 출력)
    # -----------------------------------------------------------
    def show_score(self):
        print("\n[점수 확인]")
        if not self.history:
            print("아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어보세요!")
            return

        print(f"현재 최고 점수: {self.best_score}점")
        print("\n최근 기록 (최대 5개):")
        for record in self.history[-5:]:
            print(
                f" - {record['datetime']} | "
                f"{record['correct']}/{record['total_questions']} 정답 | "
                f"점수 {record['score']}점"
            )

    # -----------------------------------------------------------
    # 5) 퀴즈 삭제 (보너스)
    # -----------------------------------------------------------
    def delete_quiz(self):
        print("\n[퀴즈 삭제]")
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        self.list_quizzes()
        index = get_int_input(
            f"삭제할 퀴즈 번호를 입력하세요 (1~{len(self.quizzes)}): ",
            min_value=1,
            max_value=len(self.quizzes),
        )
        removed = self.quizzes.pop(index - 1)
        self.save_data()
        print(f"🗑️ '{removed.question}' 퀴즈가 삭제되었습니다.")

    # -----------------------------------------------------------
    # 프로그램 실행 (메인 루프)
    # -----------------------------------------------------------
    def run(self):
        print("퀴즈 게임을 시작합니다. (종료: 메뉴에서 0 입력, 또는 Ctrl+C)")
        try:
            while True:
                self.show_menu()
                choice = get_int_input("메뉴 번호를 선택하세요: ", min_value=0, max_value=5)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                elif choice == 5:
                    self.delete_quiz()
                elif choice == 0:
                    self.save_data()
                    print("\n게임을 종료합니다. 데이터가 저장되었습니다. 안녕히 가세요!")
                    break

        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 또는 입력 스트림 종료 시 비정상 종료 대신
            # 안내 메시지를 출력하고 안전하게 저장 후 종료합니다.
            print("\n\n[안내] 입력이 중단되어 프로그램을 종료합니다.")
            self.save_data()
            print("지금까지의 데이터가 저장되었습니다. 안녕히 가세요!")
