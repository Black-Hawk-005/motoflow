import { useComments } from "../../hooks/comment/useComments";

interface CommentListProps {
  id: string;
}

export const CommentList = ({ id }: CommentListProps) => {
  const { data: comments, isLoading: isCLoading } = useComments(id);

  return isCLoading ? (
    <p>Loading...</p>
  ) : (
    <ul>
      {[...(comments ?? [])]
        .sort(
          (a, b) =>
            new Date(a.created_at).getTime() -
            new Date(b.created_at).getTime(),
        )
        .map((comment) => (
          <li key={comment.id}>
            {" "}
            {comment.author.full_name}
            {["mechanic", "admin"].includes(comment.author.role) &&
              ` (${comment.author.role})`}{" "}
            - {comment.message}{" "}
          </li>
        ))}
    </ul>
  );
};
