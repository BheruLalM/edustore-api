from sqlalchemy.orm import Session
from models.comments import Comment
from models.user import User

def fetch_comments_for_document(*, db: Session, document_id: int):
    from models.student import Student
    
    return (
        db.query(
            Comment.id,
            Comment.content,
            Comment.is_deleted,
            Comment.parent_id,
            Comment.created_at,
            User.id.label("user_id"),
            User.email.label("email"),
            Student.name.label("name"),
            Student.profile_url.label("avatar_url"),
        )
        .join(User, User.id == Comment.user_id)
        .outerjoin(Student, Student.user_id == User.id)  # Left join for non-students
        .filter(Comment.document_id == document_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

def build_comment_tree_raw(comments):
    nodes = {}
    children_map = {}

    for c in comments:
        node = {
            "id": c.id,
            "content": c.content,
            "is_deleted": c.is_deleted,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "user": {
                "id": c.user_id,
                "name": c.name,
                "email": c.email,
                "username": c.name or c.email,  # Fallback for compatibility
                "avatar_url": c.avatar_url,
            },
            "replies": [],
        }

        nodes[c.id] = node
        children_map.setdefault(c.parent_id, []).append(node)

    return nodes, children_map

def build_comment_response(*, nodes: dict, children_map: dict, max_depth: int = 3):
    def attach(parent_id: int | None, depth: int):
        if depth >= max_depth:
            return []

        result = []
        for node in children_map.get(parent_id, []):
            result.append(
                {
                    "id": node["id"],
                    "content": None if node["is_deleted"] else node["content"],
                    "is_deleted": node["is_deleted"],
                    "user": node["user"],
                    "created_at": node["created_at"],
                    "replies": attach(node["id"], depth + 1),
                }
            )
        return result

    return attach(None, 0)

def get_document_comments(*, db: Session, document_id: int, max_depth: int = 3):
    # Security: Verify document exists and is accessible
    from models.document import Document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted.is_(False),
    ).first()
    
    if not document:
        from core.exceptions import DocumentNotFound
        raise DocumentNotFound()
    
    # Note: Visibility check should be done at the route level with current_user
    # This function assumes the caller has already verified access
    
    comments = fetch_comments_for_document(db=db, document_id=document_id)
    nodes, children_map = build_comment_tree_raw(comments)
    return build_comment_response(nodes=nodes, children_map=children_map, max_depth=max_depth)
