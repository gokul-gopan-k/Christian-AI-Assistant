class RetrievalFilters:

    @staticmethod
    def by_tradition(
        docs,
        tradition
    ):

        return [
            doc
            for doc in docs
            if doc["tradition"].lower()
            == tradition.lower()
        ]

    @staticmethod
    def by_type(
        docs,
        doc_type
    ):

        return [
            doc
            for doc in docs
            if doc["type"].lower()
            == doc_type.lower()
        ]

    @staticmethod
    def scripture_only(
        docs
    ):

        return [
            doc
            for doc in docs
            if doc["tradition"]
            == "Scripture"
        ]

    @staticmethod
    def catholic_only(
        docs
    ):

        return [
            doc
            for doc in docs
            if doc["tradition"]
            == "Catholic"
        ]

    @staticmethod
    def protestant_only(
        docs
    ):

        return [
            doc
            for doc in docs
            if doc["tradition"]
            == "Protestant"
        ]

    @staticmethod
    def orthodox_only(
        docs
    ):

        return [
            doc
            for doc in docs
            if doc["tradition"]
            == "Orthodox"
        ]