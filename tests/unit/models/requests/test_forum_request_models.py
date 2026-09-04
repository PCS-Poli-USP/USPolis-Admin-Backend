from server.models.http.requests.forum_request_models import (
    ForumPostRegister,
    to_forumpost_model,
    to_forumreply_model,
)


class TestToForumpostModel:
    def test_without_filter_tags_defaults_to_one(self) -> None:
        input = ForumPostRegister(
            user_id=1, content="Dúvida sobre a prova", subject_id=2
        )

        post = to_forumpost_model(input)

        assert post.filter_tags == 1
        assert post.content == "Dúvida sobre a prova"
        assert post.reply_of_post_id is None

    def test_multiplies_filter_tags_together(self) -> None:
        input = ForumPostRegister(
            user_id=1, content="Dúvida", subject_id=2, filter_tags=[2, 3, 5]
        )

        post = to_forumpost_model(input)

        assert post.filter_tags == 30


class TestToForumreplyModel:
    def test_sets_the_reply_of_post_id(self) -> None:
        input = ForumPostRegister(user_id=1, content="Resposta", subject_id=2)

        reply = to_forumreply_model(10, input)

        assert reply.reply_of_post_id == 10
        assert reply.content == "Resposta"
