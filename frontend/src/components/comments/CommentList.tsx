import { useComments } from "../../hooks/comment/useComments";

interface CommentListProps {
  id: string;
}

export const CommentList = ({ id }: CommentListProps) => {
  const { data: comments, isLoading: isCLoading } = useComments(id);

  return isCLoading ? (
    <p className="helper-text">Loading...</p>
  ) : (
    <ul className="space-y-3">
      {(comments ?? []).length === 0 && (
        <p className="helper-text">No messages yet.</p>
      )}
      {[...(comments ?? [])]
        .sort(
          (a, b) =>
            new Date(a.created_at).getTime() -
            new Date(b.created_at).getTime(),
        )
        .map((comment) => (
          <li key={comment.id} className="rounded-md bg-slate-50 p-3 text-sm">
            <p className="mb-1 font-medium text-slate-700">
              {comment.author.full_name}
              {["mechanic", "admin"].includes(comment.author.role) && (
                <span className="ml-1 font-normal text-slate-400">
                  ({comment.author.role})
                </span>
              )}
            </p>
            <p className="text-slate-600">{comment.message}</p>
          </li>
        ))}
    </ul>
  );
};
