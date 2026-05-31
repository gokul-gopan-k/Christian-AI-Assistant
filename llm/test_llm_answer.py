from src.llm.answer_generator import AnswerGenerator

retrieved_docs = [
    {
        "id": "wsc_1",
        "content":
            "Man's chief end is to glorify God and enjoy Him forever.",
        "tradition": "Protestant",
        "source": "Westminster Shorter Catechism"
    },
    {
        "id": "1_cor_10_31",
        "content":
            "Whether therefore ye eat, or drink, or whatsoever ye do, do all to the glory of God.",
        "tradition": "Scripture",
        "source": "KJV Bible"
    }
]

generator = AnswerGenerator()

response = generator.answer(
    question="What is the purpose of life?",
    retrieved_docs=retrieved_docs
)

print(response)