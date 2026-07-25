import { RegisterUserForm } from "../components/auth/RegisterUserForm";

export const RegisterPage = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="mb-16 w-full max-w-sm">
        <h1 className="mb-6 text-center text-2xl font-semibold text-primary">
          MotoFlow
        </h1>

        <div className="card">
          <RegisterUserForm />
        </div>
      </div>
    </div>
  );
};
