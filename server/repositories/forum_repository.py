from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select
from server.models.database.forum_db_model import ForumPost 
from server.models.database.forum_post_report_link import ForumPostReportLink
from server.models.database.forum_post_reacts_link import ForumPostReactsLink



class ForumRepository:
    @staticmethod
    def create(*, input: ForumPost, session: Session) -> ForumPost:
        new_post = input
        new_post.created_at = datetime.now()
        new_post.report_count = 0

        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post

    @staticmethod
    def get_post_like_reaction(mobile_user_id: int | None, post_id: int, session:Session):
        user_statement = select(ForumPostReactsLink).where(
            col(ForumPostReactsLink.mobile_user_id)==mobile_user_id,
            col(ForumPostReactsLink.forum_post_id)==post_id
        )

        user_liked_this_post = False
        user_like_post = session.exec(user_statement).first()

        if user_like_post != None:   
            user_liked_this_post = user_like_post.post_like

        return user_liked_this_post

    @staticmethod
    def get_all_posts(*, subject_id: int, filter_tags: list[int] | None, session: Session) -> list[ForumPost]:
        """Returns all posts matching, ordered by desceding creation date (newer first), the filter_tags criteria as follows:\n
        - Each filter tags must be an prime number (e.g.: 2, 3, 5...)
        - Multiple filter tags will be the multiplication of corresponding tag numbers: (e.g.: 10 = 2*5 - tags 2 and 5)
        - If a post has no filter, its filter_tags will be 1 (not a prime multiplication)
        - To search, all posts with ANY filter_tags combination received from the request are going to be returned 
            - e.g.:filter_tags = [2, 5, 3], from request, means posts with the following filter_tags will be returned: [2, 5, 3, 10, 6, 15, 30]
        """
        statement = select(ForumPost).where(
            col(ForumPost.subject_id)==subject_id, 
            col(ForumPost.reply_of_post_id)==None,
            col(ForumPost.enabled) == True) \
            .order_by(col(ForumPost.created_at).desc())
        
        if filter_tags != None:
            # if there are filter tags, use them to search
            filter_expressions = []
            for tag in filter_tags:
                filter_expressions.append(col(ForumPost.filter_tags)%tag==0)
            statement = statement.filter(or_(*filter_expressions))

        posts = session.exec(statement).all()

        return list(posts)

    @staticmethod
    def get_post_by_id(*, post_id: int, session: Session) -> ForumPost:
        statement = select(ForumPost).where(col(ForumPost.id) == post_id, col(ForumPost.enabled) == True)
        post = session.exec(statement).one()
        return post

    @staticmethod
    def disable_post(*, post_id: int, session: Session):
        statement = select(ForumPost).where(col(ForumPost.id) == post_id)
        post = session.exec(statement).one()
        
        post.enabled = False

        session.add(post)
        session.commit()

    @staticmethod
    def update_forum_report_count(
        *, post_id: int, mobile_user_id: int, session: Session
    ) -> ForumPost:
        statement = select(ForumPost).where(col(ForumPost.id) == post_id)

        user_statement = select(ForumPostReportLink).where(
            col(ForumPostReportLink.mobile_user_id)==mobile_user_id,
            col(ForumPostReportLink.forum_post_id)==post_id)
            
        post = session.exec(statement).one()
        reported_post = session.exec(user_statement).first()

        if reported_post == None :
            # Did NOT found a report for this user and post!

            # Count reports for this post
            reports_statement = select(ForumPostReportLink).where(
                col(ForumPostReportLink.forum_post_id)==post_id)
            reports_count = len(list(session.exec(reports_statement).all())) + 1 # Adds the current report to counter
            post.report_count = reports_count
            
            # Create new report for this post and user
            new_reported_post = ForumPostReportLink(forum_post_id=post_id, mobile_user_id=mobile_user_id)

            session.add(new_reported_post)
            session.add(post)
            session.commit()
            session.refresh(post)

        return post

    @staticmethod
    def create_reply(*, input: ForumPost, session: Session):
        try:
            # Gets, and counts, all replies from this post (except this new one)
            replies_statement = select(ForumPost).where(col(ForumPost.reply_of_post_id) == input.reply_of_post_id)
            replies_count = len(list(session.exec(replies_statement).all())) + 1 # Adds the current reply to counter
            post = session.exec(select(ForumPost).where(col(ForumPost.id) == input.reply_of_post_id)).first()
            
            if post == None:
                raise PostNotFoundException(input.reply_of_post_id) # type: ignore
            post.replies_count = replies_count
            
            input.created_at = datetime.now()
            
            session.add(input)
            session.add(post)
            session.commit()
        except IntegrityError:
            raise PostNotFoundException(input.reply_of_post_id) # type: ignore

        session.refresh(input)
        return input

    @staticmethod
    def get_all_replies(*, post_id: int ,session: Session):
        statement = select(ForumPost).where(
            col(ForumPost.reply_of_post_id)==post_id,
            col(ForumPost.enabled) == True) \
            .order_by(col(ForumPost.created_at).asc())
        replies = session.exec(statement).all()
        
        return list(replies)
    
    @staticmethod
    def change_forum_post_like(
        *, post_id: int, mobile_user_id: int, like_state: bool, session: Session
    ) -> ForumPost:

        statement = select(ForumPost).where(col(ForumPost.id) == post_id)

        user_statement = select(ForumPostReactsLink).where(
            col(ForumPostReactsLink.mobile_user_id)==mobile_user_id,
            col(ForumPostReactsLink.forum_post_id)==post_id
        )
            
        post = session.exec(statement).one()
        liked_post = session.exec(user_statement).first()

        # Create or Update
        if liked_post == None:
            new_react = ForumPostReactsLink(forum_post_id=post_id, mobile_user_id=mobile_user_id, post_like=like_state)
            session.add(new_react)

        else:
            liked_post.post_like = like_state

            session.add(liked_post)

        # Update Like Count
        likes_statement = select(ForumPostReactsLink).where(
            col(ForumPostReactsLink.forum_post_id)==post_id,
            col(ForumPostReactsLink.post_like)==True
        )
        post.likes_count = len(list(session.exec(likes_statement).all()))

        session.add(post)
        session.commit()
        session.refresh(post)

        return post
    

class PostNotFoundException(HTTPException):
    def __init__(self, post_id: int) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Forum Post {post_id} does not exists"
        )
