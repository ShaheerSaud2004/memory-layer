import { SignIn } from "@clerk/nextjs";
import Link from "next/link";

/** Hash routing avoids optional catch-all route issues with `next build` on some setups. */
export default function SignInPage() {
  return (
    <main style={{ maxWidth: 480, margin: "48px auto", padding: "0 16px" }}>
      <p className="muted" style={{ marginBottom: 16 }}>
        <Link href="/login">← Email / workspace login (API token)</Link>
      </p>
      <SignIn routing="hash" signUpUrl="/sign-up" />
    </main>
  );
}
