import { SignUp } from "@clerk/nextjs";
import Link from "next/link";

export default function SignUpPage() {
  return (
    <main style={{ maxWidth: 480, margin: "48px auto", padding: "0 16px" }}>
      <p className="muted" style={{ marginBottom: 16 }}>
        <Link href="/login">← Email / workspace register (API token)</Link>
      </p>
      <SignUp routing="hash" signInUrl="/sign-in" />
    </main>
  );
}
