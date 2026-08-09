# quiz.py
# -----------------------------------------------------------
# 이 파일은 퀴즈 "문제 1개"를 표현하는 Quiz 클래스를 담고 있습니다.
# quiz_game.py 는 이 Quiz 객체를 여러 개 모아서 게임을 진행합니다.
# -----------------------------------------------------------


class Quiz:
    """퀴즈 1개(문제 + 선택지 4개 + 정답 번호 + 힌트)를 표현하는 클래스입니다."""

    def __init__(self, question, choices, answer, hint=""):
        """
        Quiz 객체를 만들 때 호출되는 생성자입니다.

        Parameters
        ----------
        question : str   문제 내용 (예: "대한민국의 수도는?")
        choices  : list  선택지 4개를 담은 문자열 리스트
        answer   : int   정답 번호 (1~4 중 하나)
        hint     : str   힌트 문구. 보너스 기능(힌트)에서 사용, 없으면 빈 문자열
        """
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def display(self, index):
        """문제 번호와 함께 문제 + 선택지를 화면에 출력합니다."""
        print(f"\nQ{index}. {self.question}")
        for i, choice in enumerate(self.choices, start=1):
            print(f"  {i}. {choice}")

    def check_answer(self, user_answer):
        """사용자가 입력한 번호(int)가 정답인지 True/False로 알려줍니다."""
        return user_answer == self.answer

    def to_dict(self):
        """
        Quiz 객체를 JSON 파일에 저장할 수 있는 dict 형태로 바꿔줍니다.
        json.dump()는 클래스 객체를 그대로 저장할 수 없기 때문에 필요합니다.
        """
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """
        JSON 파일에서 읽어온 dict 데이터를 다시 Quiz 객체로 만들어줍니다.
        to_dict()의 반대 역할을 하는 메서드입니다.
        """
        return cls(
            question=data.get("question", ""), # 질문 가져오되, 없으면 빈 문자열
            choices=data.get("choices", ["", "", "", ""]), # 보기 가져오되, 없으면 빈 리스트
            answer=data.get("answer", 1), # 정답 가져오되, 없으면 1번으로 가정
            hint=data.get("hint", ""), # 힌트 가져오되, 없으면 빈 문자열
        )
