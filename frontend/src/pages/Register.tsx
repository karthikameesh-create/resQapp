import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import ButtonSpinner from "../components/ui/ButtonSpinner";
import { useAuth } from "../context/useAuth";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await register({
        full_name: fullName,
        email,
        password,
      });

      navigate("/dashboard");
    } catch {
      setError(
        "Registration failed. The email may already be registered."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create Account</h1>
        <p>Join ResQAI</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="fullName">
            Full Name
          </label>

          <input
            id="fullName"
            value={fullName}
            onChange={(event) =>
              setFullName(event.target.value)
            }
            minLength={2}
            maxLength={100}
            required
          />

          <label htmlFor="email">
            Email
          </label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            required
          />

          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            minLength={8}
            maxLength={128}
            required
          />

          {error && (
            <p className="form-error" aria-live="polite">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <ButtonSpinner />
                Creating account...
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        <p>
          Already registered?{" "}
          <Link to="/login">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}