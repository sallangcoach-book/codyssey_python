# main.py
# -----------------------------------------------------------
# 이 프로그램의 "진입점(entry point)"입니다.
# 실제 기능(퀴즈 문제 다루기, 게임 진행)은 quiz.py 와 quiz_game.py 에
# 나뉘어 구현되어 있고, main.py는 그것들을 불러와서(import) 실행만 합니다.
#
# 실행 방법:
#   1) 터미널(명령 프롬프트)을 엽니다.
#   2) 이 파일이 있는 폴더로 이동합니다.  예) cd quiz_game
#   3) 아래 명령어를 입력합니다.
#        python main.py
#      (환경에 따라 python3 main.py 를 사용해야 할 수도 있습니다.)
# -----------------------------------------------------------

from quiz_game import QuizGame


def main():
    game = QuizGame(data_file="state.json")
    game.run()


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 main()이 호출됩니다.
    # (다른 파일에서 import 할 때는 자동 실행되지 않도록 하는 관용적인 패턴입니다.)
    main()
